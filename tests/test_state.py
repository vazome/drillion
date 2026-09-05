"""progress.json: a clone brings none, and an upgrade never touches the one you have."""

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from drillion import state
from drillion.settings import settings

REPO = Path(__file__).resolve().parent.parent


def _root(fn):
    """Run `fn(root)` against a throwaway root: state must never be the repo's own."""
    tmp, keep = Path(tempfile.mkdtemp(prefix="drillion_state_")), settings.root
    try:
        settings.root = tmp
        fn(tmp)
    finally:
        settings.root = keep
        shutil.rmtree(tmp)


def test_a_fresh_clone_starts_with_an_empty_ladder():
    """Reading a progress.json that is not there is a blank slate, and writes nothing."""

    def check(_tmp):
        assert not settings.state_path.exists()
        assert state.load() == {
            "version": state.SCHEMA,
            "focus": None,
            "cards": {},
            "open": {},
            "log": [],
            "archive": {},
            "notes": {},
        }
        assert not settings.state_path.exists()

    _root(check)


def test_an_existing_progress_file_upgrades_untouched():
    """An older progress.json reads back whole, with any newer key defaulted blank beside
    it, and no migration step between the two."""
    stored = {
        "focus": "class-inheritance",
        "cards": {"012_sortkey": {"box": 3, "due": "2026-09-01", "seen": 4}},
        "open": {
            "051_sets": {
                "attempts": 2,
                "hints": 1,
                "active": 640,
                "seed": 7,
                "last": "2026-08-26T10:00:00",
                "solution_shown": False,
            }
        },
        "log": [
            {
                "date": "2026-08-20",
                "slug": "012_sortkey",
                "grade": "pass",
                "attempts": 1,
                "secs": 300,
                "new": True,
            }
        ],
        "archive": {
            "012_sortkey": [
                {"date": "2026-08-20", "grade": "pass", "code": "def solve(): return 1"}
            ]
        },
    }

    def check(_tmp):
        settings.state_path.write_text(json.dumps(stored), encoding="utf-8")
        assert state.load() == {**stored, "notes": {}, "version": state.SCHEMA}
        with state.writing() as st:
            st["focus"] = None
        assert state.load() == {
            **stored,
            "focus": None,
            "notes": {},
            "version": state.SCHEMA,
        }

    _root(check)


def test_a_saved_progress_file_says_which_schema_it_is():
    """What this build writes stamps its own shape, so a later drillion never has to guess
    what an unversioned file was."""

    def check(_tmp):
        with state.writing() as st:
            st["focus"] = "class-inheritance"
        stored = json.loads(settings.state_path.read_text(encoding="utf-8"))
        assert stored["version"] == state.SCHEMA

    _root(check)


def test_a_progress_file_from_a_newer_drillion_is_refused_untouched():
    """A rollback — `pip install drillion==0.5` over a 0.6 file — is a normal Tuesday. The
    older build refuses the file it cannot read, on the read, before the commit path can
    write a word of it: the bytes on disk afterwards are the bytes that were there."""

    def check(_tmp):
        raw = json.dumps({"version": state.SCHEMA + 1, "focus": "generators"})
        settings.state_path.write_text(raw, encoding="utf-8")
        before = settings.state_path.read_bytes()
        with pytest.raises(state.TooNew) as refusal:
            state.load()
        assert "upgrade drillion" in str(refusal.value)
        with pytest.raises(state.TooNew), state.writing() as st:
            st["focus"] = None  # never reached: the load raises first
        assert settings.state_path.read_bytes() == before

    _root(check)


def test_a_hand_edited_version_is_read_as_no_version_at_all():
    """`version` is a number or it is nothing: garbage in the key is not a claim about the
    schema, and it is never a TypeError."""

    def check(_tmp):
        raw = json.dumps({"version": "one-ish", "focus": "class-inheritance"})
        settings.state_path.write_text(raw, encoding="utf-8")
        assert state.load()["focus"] == "class-inheritance"

    _root(check)


def test_the_repo_does_not_ship_anybody_s_progress():
    """progress.json is ignored *and* untracked: a file already in the index still travels."""
    tracked = subprocess.run(
        ["git", "ls-files", "progress.json", "progress.json.bak"],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    if tracked.returncode:
        return  # not a git checkout: nothing to ship
    assert tracked.stdout == ""


SCHEMA_DIR = Path(__file__).resolve().parent / "schema"


def _frozen(name, tmp):
    """Lay a frozen historical progress.json down in the throwaway root. Always a copy: a
    load can rewrite the file, and a fixture that gets rewritten stops being frozen."""
    shutil.copyfile(SCHEMA_DIR / name, settings.state_path)
    return settings.state_path


@pytest.mark.parametrize("frozen", ["unversioned.json", "v1.json"])
def test_a_progress_file_from_every_shipped_drillion_still_opens(frozen):
    """The files real people already have. These are bytes captured from a build that shipped,
    not a dict this test builds from today's defaults — a fixture generated from `state` moves
    when `state` moves and proves nothing about the file on somebody's disk."""

    def check(tmp):
        _frozen(frozen, tmp)
        st = state.load()
        assert st["focus"] == "class-inheritance"
        assert st["cards"]["012_sortkey"] == {
            "box": 3,
            "due": "2026-09-01",
            "seen": 4,
            "lapses": 0,
            "buried": "",
        }
        assert st["open"]["051_sets"]["attempts"] == 2
        assert st["log"][0]["slug"] == "012_sortkey"
        assert st["archive"]["012_sortkey"][0]["grade"] == "pass"
        assert st["notes"]["012_sortkey"] == "sort by the key, not the value"

    _root(check)


@pytest.mark.parametrize("frozen", ["unversioned.json", "v1.json"])
def test_an_upgraded_progress_file_is_restamped_by_the_build_that_wrote_it(
    monkeypatch, frozen
):
    """A file carries the schema of the build that last wrote it, not the one that created it.
    Without this the stamp is sticky: a newer drillion writes its own shape into an older
    person's file and leaves the old number on it, so the rollback refusal in `load()` never
    fires for the only people who have progress to lose."""

    def check(tmp):
        _frozen(frozen, tmp)
        monkeypatch.setattr(state, "SCHEMA", state.SCHEMA + 1)
        with state.writing() as st:
            st["focus"] = None
        stored = json.loads(settings.state_path.read_text(encoding="utf-8"))
        assert stored["version"] == state.SCHEMA

    _root(check)
