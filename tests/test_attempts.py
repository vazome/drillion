"""Attempts: the timer, hints, the solution gate, abandoning and the state file."""

import shutil
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from drillion import attempts, region, state
from drillion.settings import settings

SRC = (settings.tasks_dir / "001_fstrings" / "task.py").read_text()


def _solved(src=SRC, code="return ''"):
    """`src` with the region's `raise` replaced by real code."""
    return region.splice(
        src, region.cut(src).body.replace("raise NotImplementedError", code)
    )


def _exs():
    """A tiny catalogue: 002_b needs 001_a, which is not in the rsample track."""
    return {
        "001_a": {"topic": 1, "minutes": 5, "prereqs": [], "tags": ["core"]},
        "002_b": {"topic": 2, "minutes": 5, "prereqs": [1], "tags": ["core", "rsample"]},
        "003_c": {"topic": 3, "minutes": 5, "prereqs": [], "tags": ["rsample"]},
    }


def _st(**kw):
    return {"focus": None, "cards": {}, "open": {}, "log": [], "archive": {}, **kw}


def test_solution_returns_only_the_reference():
    text = attempts.solution_text(settings.tasks_dir / "001_fstrings" / "task.py")
    assert text.startswith("def _reference(") and "def test_" not in text


def test_touch_caps_a_long_gap():
    o = {"active": 0, "last": (datetime.now() - timedelta(seconds=600)).isoformat()}  # noqa: DTZ005
    assert attempts.touch(o) == 120  # a break is not work
    assert attempts.touch(o) == 120  # no time has passed since


def test_attempt_lifecycle():
    st, all_tasks = _st(), _exs()
    o = attempts.open_attempt(st, "001_a")
    assert o["new"] and o["attempts"] == 0 and 1000 <= o["seed"] <= 9999
    assert attempts.open_attempt(st, "001_a") is o  # reopening keeps the timer
    o["attempts"], o["active"] = 1, 30
    grade, gap, box = attempts.record_pass(
        st, "001_a", all_tasks["001_a"], "def solve(x):\n    return x"
    )
    assert (grade, gap, box) == ("quick", 8, 2)
    assert st["open"] == {} and st["cards"]["001_a"]["seen"] == 1
    assert st["log"][-1] == {
        "date": state.today(),
        "slug": "001_a",
        "grade": "quick",
        "attempts": 1,
        "secs": 30,
        "new": True,
    }
    assert st["archive"]["001_a"][0]["code"].startswith("def solve(")
    assert (
        attempts.open_attempt(st, "001_a")["new"] is False
    )  # a review, not a new pick


def test_hints_are_gated_by_active_time():
    st, hints = _st(), ["one", "two", "three"]
    o = attempts.open_attempt(st, "001_a")
    assert attempts.next_hint(st, "001_a", hints) == (1, "one")  # the first is free
    with pytest.raises(attempts.Gated) as e:
        attempts.next_hint(st, "001_a", hints)
    assert 0 < e.value.wait_secs <= 120
    o["active"] = 600
    assert attempts.next_hint(st, "001_a", hints) == (2, "two")
    assert attempts.next_hint(st, "001_a", hints) == (3, "three")
    with pytest.raises(attempts.Gated):
        attempts.next_hint(st, "001_a", hints)  # exhausted: use the solution


def test_solution_unlocks_after_three_attempts_and_ten_minutes():
    st = _st()
    o = attempts.open_attempt(st, "001_a")
    o.update(attempts=3, active=599)
    with pytest.raises(attempts.Gated) as gate:
        attempts.unlock_solution(st, "001_a")
    assert gate.value.owed == {
        "need_attempts": 0,
        "need_secs": 1,
    }  # what is still to be spent
    o["active"] = 600
    attempts.unlock_solution(st, "001_a")
    assert o["solution_shown"] is True


def test_the_view_answers_the_same_gate_the_action_enforces():
    st, hints = _st(), ["a", "b", "c"]
    assert attempts.attempt_view(None, hints) == {
        "attempt": None,
        "hints": {"total": 3, "shown": [], "next_in": None},
        "solution": {"unlocked": False, "need_attempts": 3, "need_secs": 600},
    }
    o = attempts.open_attempt(st, "001_a")
    assert attempts.attempt_view(o, hints)["hints"]["next_in"] == 0  # the first is free
    attempts.next_hint(st, "001_a", hints)
    assert attempts.attempt_view(o, hints)["hints"] == {
        "total": 3,
        "shown": ["a"],
        "next_in": 120,
    }  # HINT_GAP * 2, none spent
    o.update(attempts=3, active=600)
    assert attempts.attempt_view(o, hints)["solution"]["unlocked"] is True
    attempts.unlock_solution(st, "001_a")  # the action agrees


def test_abandon_archives_real_work_and_resets_the_file():
    st = _st()
    attempts.open_attempt(st, "001_fstrings")
    assert attempts.abandon(st, "001_fstrings", _solved()) == SRC
    assert st["open"] == {}
    kept = st["archive"]["001_fstrings"][0]
    assert kept["grade"] == "abandoned" and "return ''" in kept["code"]


def test_abandon_does_not_archive_an_untouched_stub():
    st = _st()
    attempts.open_attempt(st, "001_fstrings")
    assert attempts.abandon(st, "001_fstrings", SRC) == SRC
    assert st["archive"] == {} and st["open"] == {}


def test_load_fills_in_the_keys_an_older_file_lacks():
    tmp, keep = Path(tempfile.mkdtemp()), settings.root
    try:
        settings.root = tmp  # progress.json lives under root
        assert state.load() == {
            "focus": None,
            "cards": {},
            "open": {},
            "log": [],
            "archive": {},
        }
        state.save({"cards": {"001_a": {"box": 1, "due": "2020-01-01", "seen": 1}}})
        st = state.load()
        assert st["cards"]["001_a"]["box"] == 1  # what was there is kept
        assert st["focus"] is None and st["open"] == {} and st["log"] == []
        assert not list(tmp.glob("*.tmp"))  # the write was atomic
    finally:
        settings.root = keep
        shutil.rmtree(tmp)


def test_writing_commits_once_and_reading_never_does():
    tmp, keep = Path(tempfile.mkdtemp()), settings.root
    try:
        settings.root = tmp
        with state.writing() as st:
            st["focus"] = "core"
        with state.reading() as st:
            assert st["focus"] == "core"
            st["focus"] = "gone"  # a GET may scribble on its copy
        assert state.load()["focus"] == "core"  # nothing it scribbles is kept
        with pytest.raises(RuntimeError), state.writing() as st:
            st["focus"] = "half"
            raise RuntimeError("mid-transaction")
        assert state.load()["focus"] == "core"  # a failed route commits nothing
    finally:
        settings.root = keep
        shutil.rmtree(tmp)
