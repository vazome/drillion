"""Scheduler: grades, the Leitner ladder and today's queue."""

import re
from datetime import date, timedelta
from pathlib import Path

from drillion import scheduler, state

ROOT = Path(__file__).resolve().parent.parent


def _exs():
    """A tiny catalogue: 002_b needs 001_a, which is not in the rsample track."""
    return {"001_a": {"topic": 1, "minutes": 5, "prereqs": [], "tier": "core", "tags": ["loops"]},
            "002_b": {"topic": 2, "minutes": 5, "prereqs": [1], "tier": "core", "track": "rsample",
                      "tags": ["loops"]},
            "003_c": {"topic": 3, "minutes": 5, "prereqs": [], "tier": "advanced",
                      "track": "rsample", "tags": ["llm"]}}


def _st(**kw):
    return {"focus": None, "cards": {}, "open": {}, "log": [], "archive": {}, **kw}


def test_grade_of():
    assert scheduler.grade_of(1, 120, 10, False) == "quick"
    assert scheduler.grade_of(2, 900, 10, False) == "pass"
    assert scheduler.grade_of(4, 100, 10, False) == "struggled"
    assert scheduler.grade_of(1, 10, 10, True) == "struggled"          # a peeked answer never promotes


def test_reschedule():
    c = {"box": 0, "due": "2000-01-01", "seen": 1}
    assert scheduler.reschedule(c, "quick") == 8 and c["box"] == 2      # +2 boxes, LADDER[2]
    assert scheduler.reschedule(c, "struggled") == 4 and c["box"] == 1  # -1 box: a struggle costs
    assert scheduler.reschedule(c, "pass") == 8 and c["box"] == 2       # +1 box
    assert c["due"] == (date.today() + timedelta(days=8)).isoformat()   # noqa: DTZ011
    # the top box is the ceiling: a quick pass there moves nothing, which is why /run has to
    # tell the page the box the card came from rather than let it infer a step from the grade
    assert scheduler.reschedule(c, "quick") == 28 and c["box"] == 4
    assert scheduler.reschedule(c, "quick") == 28 and c["box"] == 4


def test_a_struggle_walks_a_card_back_down_the_ladder():
    """Leitner is adaptive only because failing demotes. `struggled` used to be worth +0, so a
    task that fought you every single sitting held box 4 and its 28-day gap forever — the same
    schedule as one you had aced four times, and the struggle cost you nothing but the sitting.
    One box per struggle walks it back down over a few sittings, and box 0 is the floor."""
    c = {"box": 4, "due": "2000-01-01", "seen": 9}
    assert [scheduler.reschedule(c, "struggled") for _ in range(6)] == [16, 8, 4, 2, 2, 2]
    assert c["box"] == 0


def test_unseen_respects_prereqs():
    assert scheduler.unseen(_st(), _exs()) == ["001_a", "003_c"]         # 002_b waits for topic 1
    st = _st(cards={"001_a": {"box": 1, "due": "2000-01-01", "seen": 1}})
    assert scheduler.unseen(st, _exs()) == ["002_b", "003_c"]


def test_focus_ignores_out_of_focus_prereqs():
    assert scheduler.unseen(_st(focus="rsample"), _exs()) == ["002_b", "003_c"]   # a track
    assert scheduler.unseen(_st(focus="core"), _exs()) == ["001_a"]              # a tier
    assert scheduler.unseen(_st(focus="loops"), _exs()) == ["001_a"]             # a tag
    assert scheduler.unseen(_st(focus="llm"), _exs()) == ["003_c"]


def test_queue_caps_new_picks_and_skips_open_attempts():
    q = scheduler.queue(_st(open={"001_a": {}}), _exs())
    assert q == {"review": [], "new": ["003_c"], "done_today": 0}
    done = [{"date": state.today(), "slug": "001_a", "grade": "pass", "attempts": 1, "secs": 9, "new": True},
            {"date": state.today(), "slug": "009_z", "grade": "pass", "attempts": 1, "secs": 9, "new": False}]
    q = scheduler.queue(_st(log=done), _exs())
    assert q["done_today"] == 1 and q["new"] == ["001_a"]            # one new pick left today


def test_queue_puts_the_most_overdue_review_first():
    st = _st(cards={"001_a": {"box": 1, "due": "2020-01-02", "seen": 1},
                    "003_c": {"box": 1, "due": "2020-01-01", "seen": 1}})
    assert scheduler.queue(st, _exs())["review"] == ["003_c", "001_a"]
    assert scheduler.pick(st, _exs()) == ("003_c", "review")


def test_the_web_ladder_matches_the_scheduler():
    """LADDER is hand-copied into three web files — two of them vendored design-system
    components we resync from upstream — so nothing but this keeps them honest."""
    copies = {"web/src/Stats.tsx": r"const LADDER = \[([^\]]*)\]",
              "web/src/ds/LadderMeter.jsx": r"intervals = \[([^\]]*)\]",
              "web/src/ds/Ladder.jsx": r"intervals = \[([^\]]*)\]"}
    for rel, pattern in copies.items():
        found = re.search(pattern, (ROOT / rel).read_text())
        assert found, f"the ladder intervals went missing from {rel}"
        assert [int(n) for n in re.findall(r"\d+", found[1])] == scheduler.LADDER, rel
    # and Task.tsx names the height once — the pass banner's "box 3 of 5" and its
    # top-box copy both read it, so this is the only literal left to drift.
    found = re.search(r"const BOXES = (\d+)", (ROOT / "web/src/Task.tsx").read_text())
    assert found and int(found[1]) == len(scheduler.LADDER), "web/src/Task.tsx"


def test_the_editor_opens_an_attempt_before_it_saves():
    """The server rejects a PUT with 409 unless an attempt is open, and typing is the
    first thing a learner does — so the autosave path, not just Run, has to open one.
    It did not for the whole life of the frontend: `ensureOpen` was wired to Run, the
    hint and the solution, and the 409 was caught and shown as a banner instead."""
    body = re.search(r"const flush = useCallback\(async \(\) => \{(.*?)\n  \}, \[",
                     (ROOT / "web/src/Task.tsx").read_text(), re.DOTALL)
    assert body, "flush() went missing from web/src/Task.tsx"
    assert "await ensureOpen()" in body[1], "flush() must open an attempt before it PUTs"
    assert body[1].index("await ensureOpen()") < body[1].index("method: \"PUT\""), \
        "flush() opens the attempt after the PUT it is meant to make legal"


def test_the_page_starts_the_clock_by_itself():
    """The attempt is the timer, so it starts when the task page settles — not when Run
    is first pressed, which billed the reading as free. Only Task.tsx knows the delay."""
    src = (ROOT / "web/src/Task.tsx").read_text()
    found = re.search(r"const ATTEMPT_MS = (\d+)", src)
    assert found and int(found[1]) == 5000, "the page should open its attempt after 5s"
    assert re.search(r"setTimeout\(.*ensureOpen\(\).*ATTEMPT_MS\)", src), \
        "nothing arms ATTEMPT_MS — the clock is back to starting on Run"
