"""The Leitner ladder: what comes back today, what is new, and what a pass is worth.

A 7-box ladder, not FSRS: fixed intervals over a season of practice, sized near
Cepeda 2008's 10-20% of the retention interval rather than fitted per card.
ponytail: a 7-element list beats a dependency with 21 trained weights we have no
data to fit.
"""

from datetime import date, timedelta

from .state import card, today

# days until the next sighting, per box. The tail past 28 is what keeps review load from
# growing without bound: while 28 was the ceiling, every card you had mastered still came
# back monthly, so a finished catalogue settled at ~6 reviews a day before a single new
# pick. 60 and 120 shed that load without inventing a fifth status for "retired" — the card
# is simply `done`, and a done card you keep getting right comes back rarely.
LADDER = [2, 4, 8, 16, 28, 60, 120]
NEW_PER_DAY = 2
# The most reviews a day may hand you. Unbounded, the day you come back from three weeks
# away is 100 rows deep and the ladder never recovers. Anki ships 200 against 20 new — a
# 10:1 ratio — but a drillion review is a whole coding task rather than a flashcard, so 12
# is roughly the same hour. A constant, not a setting: there is no settings screen.
REVIEWS_PER_DAY = 12
# Struggles on one task before it is flagged as beating you. Anki suspends a flashcard at
# 8 lapses; a drillion lapse costs a whole sitting rather than seconds, so the same wasted
# time arrives around 4. Flag only: nothing is suspended, hidden or rescheduled by it.
LAPSE_LIMIT = 4
# every grade grade_of() can return. A struggle costs a box: without a negative step the
# ladder is not adaptive at all — a task that fights you every sitting would hold the top box
# and its 120-day gap forever, on the same schedule as one you have aced. -1 rather than back
# to box 0: `struggled` is the grade for anything slow, anything over two runs and anything
# peeked, so it is common, and a repeated struggle still walks the card all the way down.
GRADES = {"struggled": -1, "pass": +1, "quick": +2}


def buried(st, slug):
    """Is this card out of today's queue by hand? Bury is "not today", never "not ever": it
    stores the single day it applies to, so tomorrow's date no longer matches and the bury is
    gone without anything having to expire it. It touches no box, no due date and no count —
    the card is still exactly as due as it was, it is simply not offered today."""
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

    Box 1 is the bar: a first pass graded `struggled` clamps back to box 0 and clears
    nothing. Under a focus, prereqs outside it are ignored — else a track stalls on a task
    it lacks."""
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
    task's tier, track and tags alike, so any of the three filters.

    A buried task drops out here as well as out of the reviews: bury means "not in today's
    queue", and the new picks are half of that queue. The next unblocked task takes the slot."""
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

    Both lists are capped, and the caps interact. While the backlog is deeper than the review
    cap you are `behind`, and drillion offers nothing new until you are not — starting new
    material while already behind only makes the backlog worse.

    `due_total`, `behind` and `no_new` ride along because a silent cap is worse than no cap:
    twelve rows read as "done for today" when ninety cards are still waiting. The page must
    say all of it out loud — "showing 12 of 100 due", "new picks paused while you catch up"."""
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

    Ordered the way the rules bite: the backlog holds everything else, then today's cap, then
    a prereq, and a focus only when nothing unstarted is left under it. `ready` counts what is
    unlocked and waiting for tomorrow — a bury does not take a task off that count, because it
    is still unlocked and it is back in the queue in the morning. `nearest` is the task closest
    to opening: fewest unmet prereqs, lowest topic number breaking the tie."""
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
        return "struggled"  # a peeked answer never promotes (Aleven: hint abuse)
    if attempts == 1 and secs < par * 60:
        return "quick"
    if attempts <= 2 and secs < par * 60 * 2:
        return "pass"
    return "struggled"


def reschedule(c, grade):
    """Apply a grade to a card: its lapse count, its box, and its next due date.

    A struggle is counted as well as demoted, because the two answer different questions. One
    struggle is ordinary and is exactly what the ladder is for; `LAPSE_LIMIT` of them say the
    task is the problem rather than the sitting — its prereqs are wrong, it sits above your
    level, or its spec is unclear. Demotion cannot tell those apart and says nothing out loud.
    Nothing resets the count: a task you have fought four times is worth knowing about even
    after you finally beat it."""
    if grade == "struggled":
        c["lapses"] = c.get("lapses", 0) + 1
    c["box"] = max(0, min(len(LADDER) - 1, c["box"] + GRADES[grade]))
    gap = LADDER[c["box"]]
    c["due"] = (date.today() + timedelta(days=gap)).isoformat()
    return gap
