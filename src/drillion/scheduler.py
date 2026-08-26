"""The Leitner ladder: what comes back today, what is new, and what a pass is worth."""

from datetime import date, timedelta

from .state import card, today

# days until the next sighting, per box
LADDER = [2, 4, 8, 16, 28, 60, 120]
NEW_PER_DAY = 2
REVIEWS_PER_DAY = 12
# struggles on one task before it is flagged; a flag only, nothing is suspended by it
LAPSE_LIMIT = 4
# box steps, one per grade `grade_of()` can return
GRADES = {"struggled": -1, "pass": +1, "quick": +2}


def buried(st, slug):
    """Is this card out of today's queue by hand? Bury is "not today", never "not ever": it
    stores the single day it applies to, and touches no box, no due date and no count."""
    return card(st, slug)["buried"] == today()


def due_today(st, all_tasks):
    return [
        s
        for s in all_tasks
        if card(st, s)["seen"] > 0
        and card(st, s)["due"] <= today()
        and not buried(st, s)
    ]


def _facets(meta):
    """Everything `focus` may name: the tier, the track and the tags, as one set."""
    return {meta.get("tier"), meta.get("track"), *meta.get("tags", [])} - {None}


def blocked(st, all_tasks):
    """Per unstarted task, the prereqs it has not passed yet — the reason `unseen()` skips it.

    Box 1 is the bar, and under a focus prereqs outside it are ignored."""
    focus = st.get("focus")
    by_topic = {m["topic"]: s for s, m in all_tasks.items()}
    out = {}
    for slug, meta in all_tasks.items():
        if card(st, slug)["seen"]:
            continue
        prereqs = [by_topic[p] for p in meta.get("prereqs", []) if p in by_topic]
        if focus:
            prereqs = [s for s in prereqs if focus in _facets(all_tasks[s])]
        out[slug] = [s for s in prereqs if card(st, s)["box"] < 1]
    return out


def unseen(st, all_tasks):
    """Unstarted tasks whose prereqs are cleared. Focus is one string matched against a
    task's tier, track and tags alike, so any of the three filters."""
    focus = st.get("focus")
    return [
        slug
        for slug, prereqs in blocked(st, all_tasks).items()
        if not prereqs
        and not buried(st, slug)
        and (not focus or focus in _facets(all_tasks[slug]))
    ]


def queue(st, all_tasks):
    """Today: the most overdue reviews up to the cap, then the new picks left.

    Both lists are capped: while the backlog is deeper than the review cap you are `behind`,
    and nothing new is offered. `due_total`, `behind` and `no_new` ride along for the page."""
    done_today = sum(1 for e in st["log"] if e["date"] == today() and e["new"])
    due = sorted(due_today(st, all_tasks), key=lambda s: card(st, s)["due"])
    behind = len(due) > REVIEWS_PER_DAY
    fresh = sorted(
        (s for s in unseen(st, all_tasks) if s not in st["open"]),
        key=lambda s: all_tasks[s]["topic"],
    )
    new = [] if behind else fresh[: max(0, NEW_PER_DAY - done_today)]
    return {
        "review": due[:REVIEWS_PER_DAY],
        "new": new,
        "done_today": done_today,
        "due_total": len(due),
        "behind": behind,
        "no_new": None if new else _no_new(st, all_tasks, behind=behind),
    }


def _no_new(st, all_tasks, *, behind):
    """The one reason there is nothing new to offer, for the page to name rather than guess.

    Ordered the way the rules bite: the backlog, then today's cap, then a prereq, then a
    focus. `ready` counts what is unlocked and waiting for tomorrow; `nearest` is the task
    closest to opening."""
    focus = st.get("focus")
    if behind:
        return {"why": "behind"}
    held = {
        slug: prereqs
        for slug, prereqs in blocked(st, all_tasks).items()
        if slug not in st["open"] and (not focus or focus in _facets(all_tasks[slug]))
    }
    if ready := [s for s in held if not held[s]]:
        return {"why": "cap", "ready": len(ready)}
    if waiting := {s: p for s, p in held.items() if p}:
        nearest = min(waiting, key=lambda s: (len(waiting[s]), all_tasks[s]["topic"]))
        return {"why": "prereqs", "nearest": nearest}
    return {"why": "focus" if focus else "done"}


def pick(st, all_tasks):
    """The one suggestion. Interleaved by construction: due dates scatter topics."""
    q = queue(st, all_tasks)
    for kind in ("review", "new"):
        if q[kind]:
            return q[kind][0], kind
    return None, None


def grade_of(attempts, secs, par, solution_shown):
    if solution_shown:
        return "struggled"
    if attempts == 1 and secs < par * 60:
        return "quick"
    if attempts <= 2 and secs < par * 60 * 2:
        return "pass"
    return "struggled"


def reschedule(c, grade):
    """Apply a grade to a card: its lapse count, its box, and its next due date.

    A struggle is counted as well as demoted, and nothing ever resets the count."""
    if grade == "struggled":
        c["lapses"] = c.get("lapses", 0) + 1
    c["box"] = max(0, min(len(LADDER) - 1, c["box"] + GRADES[grade]))
    gap = LADDER[c["box"]]
    c["due"] = (date.today() + timedelta(days=gap)).isoformat()
    return gap
