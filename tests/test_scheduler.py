"""Scheduler: grades, the Leitner ladder and today's queue."""

from datetime import date, timedelta

from drillion import scheduler, state


def _exs():
    """A tiny catalogue: 002_b needs 001_a, which is not in the rsample track."""
    return {
        "001_a": {
            "topic": 1,
            "minutes": 5,
            "prereqs": [],
            "tier": "core",
            "tags": ["loops"],
        },
        "002_b": {
            "topic": 2,
            "minutes": 5,
            "prereqs": [1],
            "tier": "core",
            "track": "rsample",
            "tags": ["loops"],
        },
        "003_c": {
            "topic": 3,
            "minutes": 5,
            "prereqs": [],
            "tier": "advanced",
            "track": "rsample",
            "tags": ["llm"],
        },
    }


def _st(**kw):
    return {"focus": None, "cards": {}, "open": {}, "log": [], "archive": {}, **kw}


def test_grade_of():
    assert scheduler.grade_of(1, 120, 10, False) == "quick"
    assert scheduler.grade_of(2, 900, 10, False) == "pass"
    assert scheduler.grade_of(4, 100, 10, False) == "struggled"
    assert (
        scheduler.grade_of(1, 10, 10, True) == "struggled"
    )  # a peeked answer never promotes


def test_reschedule():
    c = {"box": 0, "due": "2000-01-01", "seen": 1}
    assert (
        scheduler.reschedule(c, "quick") == 8 and c["box"] == 2
    )  # +2 boxes, LADDER[2]
    assert (
        scheduler.reschedule(c, "struggled") == 4 and c["box"] == 1
    )  # -1 box: a struggle costs
    assert scheduler.reschedule(c, "pass") == 8 and c["box"] == 2  # +1 box
    assert c["due"] == (date.today() + timedelta(days=8)).isoformat()  # noqa: DTZ011
    # the top box is the ceiling: a quick pass there moves nothing
    assert scheduler.reschedule(c, "quick") == 28 and c["box"] == 4
    assert scheduler.reschedule(c, "quick") == 120 and c["box"] == 6
    assert scheduler.reschedule(c, "quick") == 120 and c["box"] == 6


def test_a_struggle_walks_a_card_back_down_the_ladder():
    """One box per struggle walks a card back down over a few sittings, and box 0 is the floor."""
    c = {"box": 4, "due": "2000-01-01", "seen": 9}
    assert [scheduler.reschedule(c, "struggled") for _ in range(6)] == [
        16,
        8,
        4,
        2,
        2,
        2,
    ]
    assert c["box"] == 0


def test_a_struggle_is_counted_as_well_as_demoted():
    """One struggle is ordinary; `LAPSE_LIMIT` of them is information about the task. Nothing
    resets the count."""
    c = {"box": 4, "due": "2000-01-01", "seen": 9, "lapses": 0}
    for _ in range(scheduler.LAPSE_LIMIT):
        scheduler.reschedule(c, "struggled")
    assert c["lapses"] == scheduler.LAPSE_LIMIT  # the count the page flags on
    scheduler.reschedule(c, "pass")
    scheduler.reschedule(c, "quick")
    assert c["lapses"] == scheduler.LAPSE_LIMIT  # only a struggle is a lapse


def test_a_card_written_before_the_newest_fields_existed_still_reads():
    """`load()` defaults top-level keys only, so `card()` fills the per-card blanks on the
    way out."""
    old = _st(cards={"001_a": {"box": 3, "due": "2020-01-01", "seen": 7}})
    assert state.card(old, "001_a")["lapses"] == 0
    assert state.card(old, "001_a")["buried"] == ""  # never buried, not buried today
    assert not scheduler.buried(old, "001_a")
    assert state.card(old, "002_b") == {
        "box": 0,
        "due": state.today(),
        "seen": 0,
        "lapses": 0,
        "buried": "",
    }


def test_a_buried_card_leaves_todays_queue_and_comes_back_tomorrow():
    """Bury is "not today": the card stays due, both bands drop it, and tomorrow it is back."""
    yesterday = (date.today() - timedelta(days=1)).isoformat()  # noqa: DTZ011
    cards = {
        "001_a": {"box": 2, "due": "2020-01-01", "seen": 3},  # due for review
        "002_b": {"box": 1, "due": "2020-01-01", "seen": 1},  # due for review
    }
    st = _st(cards=cards)
    q = scheduler.queue(st, _exs())
    assert q["review"] == ["001_a", "002_b"] and q["new"] == ["003_c"]

    st["cards"]["001_a"]["buried"] = state.today()  # a review: not today
    st["cards"]["003_c"] = {
        "box": 0,
        "due": state.today(),
        "seen": 0,
        "buried": state.today(),
    }
    q = scheduler.queue(st, _exs())
    assert q["review"] == ["002_b"] and q["new"] == []  # both bands drop it
    assert (
        q["due_total"] == 1
    )  # ...and the backlog agrees: a buried card is not due today
    assert scheduler.due_today(st, _exs()) == ["002_b"]

    for slug in ("001_a", "003_c"):  # the next day, with nobody having touched anything
        st["cards"][slug]["buried"] = yesterday
    q = scheduler.queue(st, _exs())
    assert q["review"] == ["001_a", "002_b"] and q["new"] == ["003_c"]


def test_burying_a_card_changes_nothing_about_its_schedule():
    """A bury moves no box, no due date, no seen count and no lapse count: forgetting one
    costs exactly one day of not being asked."""
    was = {"box": 3, "due": "2020-01-01", "seen": 5, "lapses": 2}
    st = _st(cards={"001_a": dict(was)})
    state.card(st, "001_a")["buried"] = state.today()
    scheduler.queue(st, _exs())  # and reading the queue must not write to it either
    assert {k: st["cards"]["001_a"][k] for k in was} == was


def test_unseen_respects_prereqs():
    assert scheduler.unseen(_st(), _exs()) == [
        "001_a",
        "003_c",
    ]  # 002_b waits for topic 1
    st = _st(cards={"001_a": {"box": 1, "due": "2000-01-01", "seen": 1}})
    assert scheduler.unseen(st, _exs()) == ["002_b", "003_c"]


def test_focus_ignores_out_of_focus_prereqs():
    assert scheduler.unseen(_st(focus="rsample"), _exs()) == [
        "002_b",
        "003_c",
    ]  # a track
    assert scheduler.unseen(_st(focus="core"), _exs()) == ["001_a"]  # a tier
    assert scheduler.unseen(_st(focus="loops"), _exs()) == ["001_a"]  # a tag
    assert scheduler.unseen(_st(focus="llm"), _exs()) == ["003_c"]


def test_an_empty_day_names_the_one_reason_and_a_bury_is_not_one():
    """`no_new` names the rule that actually bit, and a bury unlocks nothing."""
    st = _st(focus="core")  # 002_b waits on 001_a; 003_c is out of focus
    assert scheduler.queue(st, _exs())["no_new"] is None  # 001_a is on offer

    state.card(st, "001_a")["buried"] = state.today()
    q = scheduler.queue(st, _exs())
    assert q["new"] == [] and q["no_new"] == {"why": "cap", "ready": 1}

    st = _st(focus="core", cards={"001_a": {"box": 0, "due": "2999-01-01", "seen": 1}})
    assert scheduler.queue(st, _exs())["no_new"] == {
        "why": "prereqs",
        "nearest": "002_b",
    }  # started at box 0 clears nothing

    st = _st(focus="core", cards={"001_a": {"box": 0, "due": "2999-01-01", "seen": 1}})
    st["cards"]["002_b"] = {"box": 0, "due": "2999-01-01", "seen": 1}
    assert scheduler.queue(st, _exs())["no_new"] == {"why": "focus"}
    st["focus"] = None
    st["cards"]["003_c"] = {"box": 0, "due": "2999-01-01", "seen": 1}
    assert scheduler.queue(st, _exs())["no_new"] == {"why": "done"}


def test_queue_caps_new_picks_and_skips_open_attempts():
    q = scheduler.queue(_st(open={"001_a": {}}), _exs())
    assert q == {
        "review": [],
        "new": ["003_c"],
        "done_today": 0,
        "due_total": 0,
        "behind": False,
        "no_new": None,  # there is something new to offer, so there is no reason to give
    }
    done = [
        {
            "date": state.today(),
            "slug": "001_a",
            "grade": "pass",
            "attempts": 1,
            "secs": 9,
            "new": True,
        },
        {
            "date": state.today(),
            "slug": "009_z",
            "grade": "pass",
            "attempts": 1,
            "secs": 9,
            "new": False,
        },
    ]
    q = scheduler.queue(_st(log=done), _exs())
    assert q["done_today"] == 1 and q["new"] == ["001_a"]  # one new pick left today


def test_queue_caps_reviews_and_holds_new_picks_while_behind():
    """Reviews are capped, nothing new is offered while behind, and both facts ride on the
    payload — a cap the page cannot see reads as "done for today"."""
    cap = scheduler.REVIEWS_PER_DAY
    all_tasks = {
        f"{i:03d}_x": {
            "topic": i,
            "minutes": 5,
            "prereqs": [],
            "tier": "core",
            "tags": [],
        }
        for i in range(1, cap + 7)
    }
    backlog = list(all_tasks)[: cap + 1]  # one deeper than the cap: behind
    st = _st(
        cards={
            s: {"box": 2, "due": f"2020-01-{i + 1:02d}", "seen": 1}
            for i, s in enumerate(backlog)
        }
    )
    q = scheduler.queue(st, all_tasks)
    assert (
        q["due_total"] == cap + 1 and len(q["review"]) == cap
    )  # the rest waits its turn
    assert q["review"] == backlog[:cap]  # still most overdue first
    assert q["behind"] is True and q["new"] == []  # ...and nothing new today

    st["cards"][backlog[-1]]["due"] = "2999-01-01"  # one card back under the cap
    q = scheduler.queue(st, all_tasks)
    assert q["due_total"] == cap and len(q["review"]) == cap  # the whole backlog shows
    assert (
        q["behind"] is False and len(q["new"]) == scheduler.NEW_PER_DAY
    )  # new picks return


def test_queue_puts_the_most_overdue_review_first():
    st = _st(
        cards={
            "001_a": {"box": 1, "due": "2020-01-02", "seen": 1},
            "003_c": {"box": 1, "due": "2020-01-01", "seen": 1},
        }
    )
    assert scheduler.queue(st, _exs())["review"] == ["003_c", "001_a"]
    assert scheduler.pick(st, _exs()) == ("003_c", "review")


def test_the_ladder_sheds_review_load_at_the_top():
    """The rungs past 28 days: the top interval alone decides the steady review load."""
    assert scheduler.LADDER == sorted(scheduler.LADDER), (
        "a rung must never return sooner than the one below"
    )
    assert scheduler.LADDER[-1] >= 90, "the top rung has to be a season, not a month"

    c = {"box": len(scheduler.LADDER) - 1, "due": "2000-01-01", "seen": 9}
    assert (
        scheduler.reschedule(c, "quick") == scheduler.LADDER[-1]
    )  # clamps rather than wraps
    assert c["box"] == len(scheduler.LADDER) - 1
