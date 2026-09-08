"""Persistence failures use throwaway roots, never anyone's practice history."""

import multiprocessing
import os
import sqlite3
from contextlib import closing
from pathlib import Path

import pytest

from drillion import region, state
from drillion.settings import settings


@pytest.fixture
def root(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "root", tmp_path)
    # spawn must import this test module under both pytest entry points/import modes.
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parent.parent))
    return tmp_path


def test_import_is_once_and_keeps_every_legacy_byte(root):
    raw = (Path(__file__).parent / "schema" / "v1.json").read_bytes()
    legacy = root / "progress.json"
    legacy.write_bytes(raw)
    before = state.load()
    assert settings.state_path.name == "progress.sqlite3"
    assert settings.state_path.read_bytes().startswith(b"SQLite format 3")
    with state.writing() as st:
        st["notes"]["012_sortkey"] = "new note"
    assert state.load()["archive"] == before["archive"]
    assert state.load()["notes"]["012_sortkey"] == "new note"
    assert legacy.read_bytes() == raw


@pytest.mark.parametrize(
    "raw",
    [
        '{"cards":',
        "[]",
        '{"cards": []}',
        '{"notes": {"a": 3}}',
        '{"cards": {"task": {"seen": "many"}}}',
        '{"cards": {"task": {"due": "yesterday"}}}',
    ],
)
def test_invalid_import_is_retryable_and_never_replaced_with_empty_progress(root, raw):
    legacy = root / "progress.json"
    legacy.write_text(raw, encoding="utf-8")
    with pytest.raises(state.Unreadable):
        state.load()
    assert legacy.read_text(encoding="utf-8") == raw
    legacy.write_text('{"focus": "core"}', encoding="utf-8")
    assert state.load()["focus"] == "core"


def _increment(root, ready, go):
    settings.root = Path(root)
    ready.put(True)
    assert go.wait(10)
    for _ in range(10):
        with state.writing() as st:
            state.own(st, "task")["seen"] += 1


def test_independent_processes_cannot_lose_updates(root):
    ctx = multiprocessing.get_context("spawn")
    ready, go = ctx.Queue(), ctx.Event()
    workers = [
        ctx.Process(target=_increment, args=(str(root), ready, go)) for _ in range(3)
    ]
    for worker in workers:
        worker.start()
    try:
        for _ in workers:
            ready.get(timeout=10)
        go.set()
        for worker in workers:
            worker.join(15)
            assert worker.exitcode == 0
        assert state.load()["cards"]["task"]["seen"] == 30
    finally:
        for worker in workers:
            if worker.is_alive():
                worker.terminate()
                worker.join()
        ready.close()


def test_a_failed_transaction_rolls_back_all_records(root):
    with state.writing() as st:
        st["notes"]["task"] = "keep"
    with pytest.raises(RuntimeError), state.writing() as st:
        st["notes"]["task"] = "lost"
        st["log"].append({"date": "2026-09-08"})
        raise RuntimeError("request failed")
    assert state.load()["notes"] == {"task": "keep"}
    assert state.load()["log"] == []


def test_timer_update_does_not_rewrite_archive_rows(root):
    with state.writing() as st:
        st["open"]["task"] = {"active": 0}
        st["archive"]["task"] = [
            {"date": "2026-09-08", "grade": "pass", "code": "saved"}
        ]
    with closing(sqlite3.connect(settings.state_path)) as db:
        db.execute("""CREATE TRIGGER protect_archive BEFORE UPDATE ON progress
                      WHEN old.section = 'archive'
                      BEGIN SELECT RAISE(ABORT, 'archive rewritten'); END""")
        db.execute("""CREATE TRIGGER protect_archive_delete BEFORE DELETE ON progress
                      WHEN old.section = 'archive'
                      BEGIN SELECT RAISE(ABORT, 'archive deleted'); END""")
    with state.writing() as st:
        st["open"]["task"]["active"] += 1
    assert state.load()["archive"]["task"][0]["code"] == "saved"


@pytest.mark.parametrize("external_edit", [None, "region", "machinery"])
def test_reset_failure_keeps_archive_and_recovers_on_next_access(
    root, monkeypatch, external_edit
):
    path = root / "tasks" / "task" / "task.py"
    path.parent.mkdir(parents=True)
    source = f"def solve():\n    return 42\n\n\n{region.MARKER}\n"
    replacement = region.splice(source, region.stub(region.cut(source).body))
    path.write_text(source, encoding="utf-8")
    with monkeypatch.context() as patch:

        def fail(*args):
            raise OSError("disk unavailable")

        patch.setattr(region, "write_region", fail)
        with (
            pytest.raises(state.Unreadable, match="Progress is saved"),
            state.writing() as st,
        ):
            st["archive"]["task"] = [
                {"date": "2026-09-08", "grade": "pass", "code": "return 42"}
            ]
            state.reset_after_commit(st, path, source, replacement)
        assert path.read_text(encoding="utf-8") == source
        with closing(sqlite3.connect(settings.state_path)) as db:
            assert db.execute("SELECT count(*) FROM pending_resets").fetchone()[0] == 1
            assert (
                db.execute(
                    "SELECT count(*) FROM progress WHERE section = 'archive' AND position >= 0"
                ).fetchone()[0]
                == 1
            )
    if external_edit == "region":
        replacement = source.replace("return 42", "return 43")
        path.write_text(replacement, encoding="utf-8")
    elif external_edit == "machinery":
        path.write_text(source + "# updated machinery\n", encoding="utf-8")
        replacement += "# updated machinery\n"
    assert state.load()["archive"]["task"][0]["code"] == "return 42"
    assert path.read_text(encoding="utf-8") == replacement


def test_newer_database_is_refused_untouched(root):
    with state.writing() as st:
        st["focus"] = "core"
    with closing(sqlite3.connect(settings.state_path)) as db:
        db.execute(f"PRAGMA user_version = {state.DB_SCHEMA + 1}")
    before = settings.state_path.read_bytes()
    with pytest.raises(state.TooNew), state.writing():
        pytest.fail("newer database opened for writing")
    assert settings.state_path.read_bytes() == before


def _die_before_commit(root):
    settings.root = Path(root)
    store = state._store

    def die(db, st, before):
        store(db, st, before)
        os._exit(23)

    state._store = die
    with state.writing() as st:
        st["focus"] = "uncommitted"


def test_process_death_rolls_back_uncommitted_progress(root):
    with state.writing() as st:
        st["focus"] = "keep"
    worker = multiprocessing.get_context("spawn").Process(
        target=_die_before_commit, args=(str(root),)
    )
    worker.start()
    try:
        worker.join(15)
        assert worker.exitcode == 23
        assert state.load()["focus"] == "keep"
        with closing(sqlite3.connect(settings.state_path)) as db:
            assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    finally:
        if worker.is_alive():
            worker.terminate()
            worker.join()


def test_interrupted_import_rolls_back_schema_and_can_retry(root, monkeypatch):
    legacy = root / "progress.json"
    raw = '{"focus": "core", "future_field": {"keep": true}}'
    legacy.write_text(raw, encoding="utf-8")
    store = state._store
    with monkeypatch.context() as patch:

        def fail(db, st, before):
            store(db, st, before)
            raise RuntimeError("interrupted import")

        patch.setattr(state, "_store", fail)
        with pytest.raises(RuntimeError):
            state.load()
    st = state.load()
    assert st["focus"] == "core"
    assert st["future_field"] == {"keep": True}
    assert legacy.read_text(encoding="utf-8") == raw
