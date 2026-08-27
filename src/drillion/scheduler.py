"""The Leitner ladder: what comes back today, what is new, and what a pass is worth."""

from collections import Counter
from datetime import date, timedelta

from .state import card, today

# days until the next sighting, per box
LADDER = [2, 4, 8, 16, 28, 60, 120]
NEW_PER_DAY = 2
REVIEWS_PER_DAY = 12
# struggles on one task before it is flagged; a flag only, nothing is suspended by it
LAPSE_LIMIT = 4
WINDOW = 7  # days in the consistency window; the page reads it off the payload
FORECAST_DAYS = 14  # how far ahead the progress page looks
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


def unseen(st, all_tasks, held=None):
    """Unstarted tasks whose prereqs are cleared. Focus is one string matched against a
    task's tier, track and tags alike, so any of the three filters.

    `held` is `blocked()`'s answer when the caller already has it."""
    focus = st.get("focus")
    return [
        slug
        for slug, prereqs in (blocked(st, all_tasks) if held is None else held).items()
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
    held = blocked(st, all_tasks)
    fresh = sorted(
        (s for s in unseen(st, all_tasks, held) if s not in st["open"]),
        key=lambda s: all_tasks[s]["topic"],
    )
    new = [] if behind else fresh[: max(0, NEW_PER_DAY - done_today)]
    return {
        "review": due[:REVIEWS_PER_DAY],
        "new": new,
        "done_today": done_today,
        "due_total": len(due),
        "behind": behind,
        "no_new": None
        if new
        else _no_new(st, all_tasks, held, fresh, behind=behind, done_today=done_today),
    }


def _no_new(st, all_tasks, held, fresh, *, behind, done_today):
    """The one reason there is nothing new to offer, for the page to name rather than guess.

    Ordered the way the rules bite: the backlog, then today's cap, then a bury, then a
    prereq, then a focus. `ready` counts what is unlocked and waiting for tomorrow, buried
    or not; `nearest` is the task closest to opening."""
    focus = st.get("focus")
    if behind:
        return {"why": "behind"}
    waiting, ready = {}, len(fresh)
    for slug, prereqs in held.items():
        if slug in st["open"] or (focus and focus not in _facets(all_tasks[slug])):
            continue
        if prereqs:
            waiting[slug] = prereqs
        elif buried(st, slug):  # unlocked and in focus: the bury is what holds it back
            ready += 1
    if fresh or done_today >= NEW_PER_DAY:
        return {"why": "cap", "ready": ready}
    if ready:  # nothing fresh, so every unlocked task left is one you buried
        return {"why": "buried"}
    if waiting:
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


def boxes(st, all_tasks):
    """How many seen cards sit in each ladder box."""
    out = [0] * len(LADDER)
    for slug in all_tasks:
        c = card(st, slug)
        if c["seen"]:
            out[c["box"]] += 1
    return out


def practised(st):
    """Days worked in the last WINDOW, counted from the archive, so a day you gave up on
    still counts. A rolling window, never a streak."""
    cut = (date.fromisoformat(today()) - timedelta(days=WINDOW - 1)).isoformat()
    return len(
        {r["date"] for runs in st["archive"].values() for r in runs if r["date"] >= cut}
    )


def stats(st, all_tasks, due=None):
    """The ladder at a glance: the same block on the catalogue and on the progress page.

    `due` is the whole backlog; pass `queue()`'s count rather than counting it twice."""
    spread = boxes(st, all_tasks)
    return {
        "boxes": spread,
        "ladder": LADDER,
        "due": len(due_today(st, all_tasks)) if due is None else due,
        "seen": sum(spread),
        "total": len(all_tasks),
        "practised": practised(st),
        "window": WINDOW,
    }


def forecast(st, all_tasks):
    """Reviews landing on each of the next FORECAST_DAYS days. Day 0 carries everything
    overdue, except what is buried: that is tomorrow's."""
    start = date.fromisoformat(today())
    out = [0] * FORECAST_DAYS
    for slug in all_tasks:
        c = card(st, slug)
        if not c["seen"]:
            continue
        ahead = (date.fromisoformat(c["due"]) - start).days
        if ahead < FORECAST_DAYS:
            out[max(ahead, 1 if buried(st, slug) else 0)] += 1
    return out


def by_tag(st, all_tasks):
    """Per tag: how much of it you have seen, where it sits on the ladder, what it has cost
    in lapses, and how much of it is due inside the week."""
    week = (date.fromisoformat(today()) + timedelta(days=6)).isoformat()
    out = {}
    for slug, meta in all_tasks.items():
        c = card(st, slug)
        for tag in meta["tags"]:
            t = out.setdefault(
                tag,
                {
                    "seen": 0,
                    "total": 0,
                    "boxes": [0] * len(LADDER),
                    "lapses": 0,
                    "due7": 0,
                },
            )
            t["total"] += 1
            if c["seen"]:
                t["seen"] += 1
                t["boxes"][c["box"]] += 1
                t["lapses"] += c["lapses"]
                t["due7"] += c["due"] <= week
    return out


def stuck(st, all_tasks):
    """The tag whose tasks keep beating you: the most flagged tasks, at least two of them,
    ties broken by total lapses and then by name. None when nothing stands out."""
    flagged, lapses = Counter(), Counter()
    for slug, meta in all_tasks.items():
        n = card(st, slug)["lapses"]
        for tag in meta["tags"]:
            lapses[tag] += n
            if n >= LAPSE_LIMIT:
                flagged[tag] += 1
    worst = min(
        ((tag, n) for tag, n in flagged.items() if n >= 2),
        key=lambda f: (-f[1], -lapses[f[0]], f[0]),
        default=None,
    )
    return {"tag": worst[0], "flagged": worst[1]} if worst else None


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
