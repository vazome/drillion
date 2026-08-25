"""Attempts: the timer, hints, the solution gate, abandoning and the state file."""

import shutil
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from study import attempts, region, state
from study.settings import settings

SRC = (settings.exercises_dir / "ex_001_fstrings.py").read_text()


def _solved(src=SRC, code="return ''"):
    """`src` with the region's `raise` replaced by real code."""
    return region.splice(src, region.cut(src).body.replace("raise NotImplementedError", code))


def _exs():
    """A tiny catalogue: ex_b needs ex_a, which is not in the rsample track."""
    return {"ex_a": {"topic": 1, "minutes": 5, "prereqs": [], "tags": ["core"]},
            "ex_b": {"topic": 2, "minutes": 5, "prereqs": [1], "tags": ["core", "rsample"]},
            "ex_c": {"topic": 3, "minutes": 5, "prereqs": [], "tags": ["rsample"]}}


def _st(**kw):
    return {"focus": None, "cards": {}, "open": {}, "log": [], "archive": {}, **kw}


def test_solution_returns_only_the_reference():
    text = attempts._solution(settings.exercises_dir / "ex_001_fstrings.py")
    assert text.startswith("def _reference(") and "def test_" not in text


def test_touch_caps_a_long_gap():
    o = {"active": 0, "last": (datetime.now() - timedelta(seconds=600)).isoformat()}  # noqa: DTZ005
    assert attempts.touch(o) == 120                                   # a break is not work
    assert attempts.touch(o) == 120                                   # no time has passed since


def test_attempt_lifecycle():
    st, exs = _st(), _exs()
    o = attempts.open_attempt(st, "ex_a")
    assert o["new"] and o["attempts"] == 0 and 1000 <= o["seed"] <= 9999
    assert attempts.open_attempt(st, "ex_a") is o                     # reopening keeps the timer
    o["attempts"], o["active"] = 1, 30
    grade, gap, box = attempts.record_pass(st, "ex_a", exs["ex_a"], "def solve(x):\n    return x")
    assert (grade, gap, box) == ("easy", 8, 2)
    assert st["open"] == {} and st["cards"]["ex_a"]["seen"] == 1
    assert st["log"][-1] == {"date": state.today(), "slug": "ex_a", "grade": "easy",
                             "attempts": 1, "secs": 30, "new": True}
    assert st["archive"]["ex_a"][0]["code"].startswith("def solve(")
    assert attempts.open_attempt(st, "ex_a")["new"] is False           # a review, not a new pick


def test_hints_are_gated_by_active_time():
    st, hints = _st(), ["one", "two", "three"]
    o = attempts.open_attempt(st, "ex_a")
    assert attempts.next_hint(st, "ex_a", hints) == (1, "one")         # the first is free
    with pytest.raises(attempts.Gated) as e:
        attempts.next_hint(st, "ex_a", hints)
    assert 0 < e.value.wait_secs <= 120
    o["active"] = 600
    assert attempts.next_hint(st, "ex_a", hints) == (2, "two")
    assert attempts.next_hint(st, "ex_a", hints) == (3, "three")
    with pytest.raises(attempts.Gated):
        attempts.next_hint(st, "ex_a", hints)                          # exhausted: use the solution


def test_solution_unlocks_after_three_attempts_and_ten_minutes():
    st = _st()
    o = attempts.open_attempt(st, "ex_a")
    o.update(attempts=3, active=599)
    assert attempts.unlock_solution(st, "ex_a") is False
    o["active"] = 600
    assert attempts.unlock_solution(st, "ex_a") is True
    assert o["solution_shown"] is True


def test_abandon_archives_real_work_and_resets_the_file():
    st = _st()
    attempts.open_attempt(st, "ex_001_fstrings")
    assert attempts.abandon(st, "ex_001_fstrings", _solved()) == SRC
    assert st["open"] == {}
    kept = st["archive"]["ex_001_fstrings"][0]
    assert kept["grade"] == "abandoned" and "return ''" in kept["code"] and '"""WHY' not in kept["code"]


def test_abandon_does_not_archive_an_untouched_stub():
    st = _st()
    attempts.open_attempt(st, "ex_001_fstrings")
    assert attempts.abandon(st, "ex_001_fstrings", SRC) == SRC
    assert st["archive"] == {} and st["open"] == {}


def test_load_fills_in_the_keys_an_older_file_lacks():
    tmp, keep = Path(tempfile.mkdtemp()), settings.root
    try:
        settings.root = tmp                                          # progress.json lives under root
        assert state.load() == {"focus": None, "cards": {}, "open": {}, "log": [], "archive": {}}
        state.save({"cards": {"ex_a": {"box": 1, "due": "2020-01-01", "seen": 1}}})
        st = state.load()
        assert st["cards"]["ex_a"]["box"] == 1                       # what was there is kept
        assert st["focus"] is None and st["open"] == {} and st["log"] == []
        assert not list(tmp.glob("*.tmp"))                           # the write was atomic
    finally:
        settings.root = keep
        shutil.rmtree(tmp)
