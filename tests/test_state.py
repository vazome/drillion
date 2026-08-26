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
    """No progress.json is shipped, so the first thing a clone does is read a file that
    is not there. That must be a blank slate and not a crash, and it must not write one
    either: opening the menu is not practice."""

    def check(_tmp):
        assert not settings.state_path.exists()
        assert state.load() == {
            "focus": None,
            "cards": {},
            "open": {},
            "log": [],
            "archive": {},
        }
        assert not settings.state_path.exists()

    _root(check)


def test_an_existing_progress_file_upgrades_untouched():
    """Untracking progress.json must cost an existing install nothing: the file stays
    where it always was, load() reads every key back exactly as stored, and there is no
    migration step between the two. This is the half of #4 that could destroy real work."""
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
        assert state.load() == stored  # nothing added, nothing dropped, no move
        with state.writing() as st:  # and a session on top keeps it all
            st["focus"] = None
        assert state.load() == {**stored, "focus": None}

    _root(check)


def test_the_repo_does_not_ship_anybody_s_progress():
    """The only way a clone can arrive with someone else's cards is for progress.json to
    be tracked again. It is ignored *and* untracked — being ignored alone would not stop
    a file already in the index from travelling."""
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
