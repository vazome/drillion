"""progress.json: a clone brings none, and an upgrade never touches the one you have."""

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

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
        "cards": {"008_sortkey": {"box": 3, "due": "2026-09-01", "seen": 4}},
        "open": {
            "021_sets": {
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
                "slug": "008_sortkey",
                "grade": "pass",
                "attempts": 1,
                "secs": 300,
                "new": True,
            }
        ],
        "archive": {
            "008_sortkey": [
                {"date": "2026-08-20", "grade": "pass", "code": "def solve(): return 1"}
            ]
        },
    }

    def check(_tmp):
        settings.state_path.write_text(json.dumps(stored))
        assert state.load() == {**stored, "notes": {}}
        with state.writing() as st:
            st["focus"] = None
        assert state.load() == {**stored, "focus": None, "notes": {}}

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
