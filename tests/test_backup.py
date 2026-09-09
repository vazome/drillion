"""Backup and restore run against throwaway roots, never anyone's practice history."""

import asyncio
import io
import shutil
import tempfile
import zipfile
from pathlib import Path

import httpx
import pytest

from drillion import backup, region, state
from drillion.api import app
from drillion.settings import settings

SLUG = "009_fstrings"
OTHER = "008_slicing"
SOURCE = settings.tasks_dir


def _root(extra=()):
    """A throwaway root holding one task, plus any `extra` slugs a test needs."""
    tmp = Path(tempfile.mkdtemp(prefix="drillion_backup_"))
    (tmp / "tasks").mkdir()
    for slug in (SLUG, *extra):
        shutil.copytree(SOURCE / slug, tmp / "tasks" / slug)
    shutil.copy(SOURCE / "_lib.py", tmp / "tasks" / "_lib.py")
    return tmp


@pytest.fixture
def root(monkeypatch):
    tmp = _root()
    monkeypatch.setattr(settings, "root", tmp)
    yield tmp
    shutil.rmtree(tmp, ignore_errors=True)


def _write(slug, body):
    path = settings.tasks_dir / slug / "task.py"
    src = path.read_text(encoding="utf-8")
    region.write_region(path, region.validate(body, src))


def _body(slug):
    path = settings.tasks_dir / slug / "task.py"
    return region.cut(path.read_text(encoding="utf-8")).body


def test_a_bundle_round_trips_progress_and_saved_code(root):
    with state.writing() as st:
        st["notes"][SLUG] = "my note"
        st["cards"][SLUG] = {"box": 3, "due": "2030-01-01", "seen": 2, "lapses": 1}
    mine = "def solve(rows):\n    return 'mine'\n"
    _write(SLUG, mine)
    data = backup.bundle()

    with state.writing() as st:
        st["notes"].clear()
        st["cards"].clear()
    _write(SLUG, "def solve(rows):\n    return 'clobbered'\n")

    summary = backup.restore(data)
    assert summary["brings"]["tasks"] == 1
    assert summary["unknown"] == []
    assert state.load()["notes"][SLUG] == "my note"
    assert state.load()["cards"][SLUG]["box"] == 3
    assert _body(SLUG) == mine.strip("\n")


def test_restoring_keeps_the_data_it_replaces(root):
    with state.writing() as st:
        st["notes"][SLUG] = "before"
    data = backup.bundle()
    with state.writing() as st:
        st["notes"][SLUG] = "after"
    kept = Path(backup.restore(data)["kept"])
    assert kept.is_file()
    with zipfile.ZipFile(kept) as zf:
        assert backup.MANIFEST in zf.namelist()


def test_a_task_this_version_does_not_ship_is_reported_not_dropped(root):
    data = backup.bundle()
    buf = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(data)) as old, zipfile.ZipFile(buf, "w") as new:
        for item in old.infolist():
            new.writestr(item, old.read(item.filename))
        new.writestr(f"{backup.REGIONS}999_retired.py", "def solve():\n    return 1\n")
    assert backup.inspect(buf.getvalue())["unknown"] == ["999_retired"]
    assert backup.restore(buf.getvalue())["unknown"] == ["999_retired"]


@pytest.fixture
def two_roots(monkeypatch):
    """Two tasks, so a restore has somewhere to fail part-way through."""
    tmp = _root(extra=(OTHER,))
    monkeypatch.setattr(settings, "root", tmp)
    yield tmp
    shutil.rmtree(tmp, ignore_errors=True)


def test_a_region_that_will_not_splice_stops_the_whole_restore(two_roots):
    with state.writing() as st:
        st["notes"][SLUG] = "in the bundle"
    _write(SLUG, "def solve(rows):\n    return 'bundled'\n")
    data = backup.bundle()

    with state.writing() as st:
        st["notes"][SLUG] = "on disk now"
    _write(SLUG, "def solve(rows):\n    return 'on disk now'\n")
    before = (_body(SLUG), _body(OTHER))

    # one region in the bundle no longer fits the machinery it has to land in
    buf = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(data)) as old, zipfile.ZipFile(buf, "w") as new:
        for item in old.infolist():
            body = old.read(item.filename)
            if item.filename == f"{backup.REGIONS}{OTHER}.py":
                body = b"def solve(xs: return 1\n"
            new.writestr(item, body)

    with pytest.raises(backup.Rejected, match=OTHER):
        backup.restore(buf.getvalue())
    assert (_body(SLUG), _body(OTHER)) == before
    assert state.load()["notes"][SLUG] == "on disk now"


def test_a_write_that_fails_part_way_puts_the_earlier_files_back(
    two_roots, monkeypatch
):
    with state.writing() as st:
        st["notes"][SLUG] = "in the bundle"
    _write(SLUG, "def solve(rows):\n    return 'bundled'\n")
    _write(OTHER, _body(OTHER).replace("raise NotImplementedError", "return 'bundled'"))
    data = backup.bundle()

    with state.writing() as st:
        st["notes"][SLUG] = "on disk now"
    _write(SLUG, "def solve(rows):\n    return 'on disk now'\n")
    _write(
        OTHER, _body(OTHER).replace("raise NotImplementedError", "return 'on disk now'")
    )
    before = (_body(SLUG), _body(OTHER))

    real, calls = region.write_region, []

    def fail_on_the_second(path, new_src):
        calls.append(path)
        if len(calls) == 2:
            raise OSError("disk full")
        real(path, new_src)

    monkeypatch.setattr(backup.region, "write_region", fail_on_the_second)
    with pytest.raises(backup.Rejected):
        backup.restore(data)

    monkeypatch.setattr(backup.region, "write_region", real)
    assert (_body(SLUG), _body(OTHER)) == before
    assert state.load()["notes"][SLUG] == "on disk now"


@pytest.mark.parametrize(
    "make",
    [
        lambda: b"not a zip at all",
        lambda: _zip({"manifest.json": '{"format": 99}'}),
        lambda: _zip({"manifest.json": '{"format": 1}'}),  # no progress
        lambda: _zip({"manifest.json": '{"format": 1}', "progress.json": "["}),
        lambda: _zip(
            {"manifest.json": '{"format": 1}', "progress.json": '{"version": 99}'}
        ),
    ],
)
def test_a_bundle_we_cannot_read_changes_nothing(root, make):
    with state.writing() as st:
        st["notes"][SLUG] = "untouched"
    before = settings.state_path.read_bytes()
    with pytest.raises(backup.Rejected):
        backup.restore(make())
    assert settings.state_path.read_bytes() == before
    assert state.load()["notes"][SLUG] == "untouched"


def _zip(files):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, text in files.items():
            zf.writestr(name, text)
    return buf.getvalue()


def test_the_routes_download_preview_and_restore(root):
    async def drive():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://127.0.0.1"
        ) as api:
            paths = (await api.get("/api/settings")).json()
            assert paths["root"] == str(root)

            with state.writing() as st:
                st["notes"][SLUG] = "kept"
            got = await api.get("/api/backup")
            assert got.headers["content-type"] == "application/zip"
            assert "drillion-backup-" in got.headers["content-disposition"]
            data = got.content

            with state.writing() as st:
                st["notes"][SLUG] = "gone"
            preview = (await api.post("/api/restore/preview", content=data)).json()
            assert preview["brings"]["tasks"] == 1 and preview["brings"]["notes"] == 1
            assert preview["replaces"]["notes"] == 1
            assert state.load()["notes"][SLUG] == "gone"  # a preview changes nothing

            done = (await api.post("/api/restore", content=data)).json()
            assert done["brings"]["tasks"] == 1
            assert state.load()["notes"][SLUG] == "kept"

            bad = await api.post("/api/restore", content=b"not a zip")
            assert bad.status_code == 400 and "error" in bad.json()

    asyncio.run(drive())


def test_erasing_clears_progress_and_puts_every_task_back_to_its_stub(root):
    stub = _body(SLUG)
    # a leftover from before SQLite: a fresh database imports it, so an erase has to take it
    (root / "progress.json").write_text('{"version": 1, "notes": {}}', encoding="utf-8")
    with state.writing() as st:
        st["notes"][SLUG] = "my note"
        st["cards"][SLUG] = {"box": 3, "due": "2030-01-01", "seen": 2, "lapses": 0}
        st["archive"][SLUG] = [{"date": "2026-01-01", "grade": "PASS"}]
    _write(SLUG, stub.replace("raise NotImplementedError", "return 'mine'"))

    summary = backup.erase()

    assert summary["cleared"] == 1 and summary["failed"] == []
    assert _body(SLUG) == stub
    # the storage goes too, or the next read imports the legacy JSON straight back
    assert not settings.state_path.exists()
    assert not (settings.root / "progress.json").exists()
    st = state.load()
    assert st["cards"] == {} and st["notes"] == {} and st["archive"] == {}


def test_what_an_erase_destroys_is_in_the_backup_it_writes_first(root):
    with state.writing() as st:
        st["notes"][SLUG] = "my note"
    _write(SLUG, _body(SLUG).replace("raise NotImplementedError", "return 'mine'"))

    kept = Path(backup.erase()["kept"])

    assert kept.name == "backup-before-reset.zip"
    backup.restore(kept.read_bytes())
    assert state.load()["notes"][SLUG] == "my note"
    assert "return 'mine'" in _body(SLUG)


def test_the_reset_route_refuses_anything_but_the_phrase(root):
    async def drive():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://127.0.0.1"
        ) as api:
            with state.writing() as st:
                st["notes"][SLUG] = "still here"

            for confirm in ("", "yes", "Erase Progress!"):
                refused = await api.post("/api/reset", json={"confirm": confirm})
                assert refused.status_code == 400, confirm
                assert state.load()["notes"][SLUG] == "still here"

            done = (
                await api.post("/api/reset", json={"confirm": backup.PHRASE})
            ).json()
            assert done["cleared"] == 0 and done["failed"] == []
            assert state.load()["notes"] == {}

    asyncio.run(drive())
