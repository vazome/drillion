"""Scheduler: grades, the Leitner ladder and today's queue."""

from datetime import date, timedelta

from study import scheduler, state


def _exs():
    """A tiny catalogue: 002_b needs 001_a, which is not in the rsample track."""
    return {"001_a": {"topic": 1, "minutes": 5, "prereqs": [], "tags": ["core"]},
            "002_b": {"topic": 2, "minutes": 5, "prereqs": [1], "tags": ["core", "rsample"]},
            "003_c": {"topic": 3, "minutes": 5, "prereqs": [], "tags": ["rsample"]}}


def _st(**kw):
    return {"focus": None, "cards": {}, "open": {}, "log": [], "archive": {}, **kw}


def test_grade_of():
    assert scheduler.grade_of(1, 120, 10, False) == "easy"
    assert scheduler.grade_of(2, 900, 10, False) == "pass"
    assert scheduler.grade_of(4, 100, 10, False) == "struggled"
    assert scheduler.grade_of(1, 10, 10, True) == "struggled"          # a peeked answer never promotes


def test_reschedule():
    c = {"box": 0, "due": "2000-01-01", "seen": 1}
    assert scheduler.reschedule(c, "easy") == 8 and c["box"] == 2      # +2 boxes, LADDER[2]
    assert scheduler.reschedule(c, "struggled") == 8 and c["box"] == 2  # same box, same gap
    assert scheduler.reschedule(c, "fail") == 2 and c["box"] == 0      # -2 boxes, back to the start
    assert c["due"] == (date.today() + timedelta(days=2)).isoformat()  # noqa: DTZ011


def test_unseen_respects_prereqs():
    assert scheduler.unseen(_st(), _exs()) == ["001_a", "003_c"]         # 002_b waits for topic 1
    st = _st(cards={"001_a": {"box": 1, "due": "2000-01-01", "seen": 1}})
    assert scheduler.unseen(st, _exs()) == ["002_b", "003_c"]


def test_focus_ignores_out_of_focus_prereqs():
    assert scheduler.unseen(_st(focus="rsample"), _exs()) == ["002_b", "003_c"]
    assert scheduler.unseen(_st(focus="core"), _exs()) == ["001_a"]


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
