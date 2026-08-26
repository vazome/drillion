"""The Leitner ladder: what comes back today, what is new, and what a pass is worth.

A 5-box ladder, not FSRS: fixed intervals over a season of practice, sized near
Cepeda 2008's 10-20% of the retention interval rather than fitted per card.
ponytail: a 5-element list beats a dependency with 21 trained weights we have no
data to fit.
"""

from datetime import date, timedelta

from .state import card, today

LADDER = [2, 4, 8, 16, 28]           # days until the next sighting, per box
NEW_PER_DAY = 2
GRADES = {"struggled": 0, "pass": +1, "quick": +2}   # every grade grade_of() can return


def due_today(st, all_tasks):
    return [s for s in all_tasks if card(st, s)["seen"] > 0 and card(st, s)["due"] <= today()]


def _facets(meta):
    """Everything `focus` may name: the tier, the track and the tags, as one set."""
    return {meta.get("tier"), meta.get("track"), *meta.get("tags", [])} - {None}


def unseen(st, all_tasks):
    """Unstarted tasks whose prereqs are cleared. Under a focus, prereqs outside
    it are ignored — else a track stalls on a task it lacks. Focus is one string
    matched against a task's tier, track and tags alike, so any of the three filters."""
    focus = st.get("focus")
    by_topic = {m["topic"]: s for s, m in all_tasks.items()}
    ready = []
    for slug, meta in all_tasks.items():
        if card(st, slug)["seen"] or (focus and focus not in _facets(meta)):
            continue
        prereqs = [by_topic[p] for p in meta.get("prereqs", []) if p in by_topic]
        if focus:
            prereqs = [s for s in prereqs if focus in _facets(all_tasks[s])]
        if all(card(st, s)["box"] >= 1 for s in prereqs):
            ready.append(slug)
    return ready


def queue(st, all_tasks):
    """Today: every due review (most overdue first), then the new picks left."""
    done_today = sum(1 for e in st["log"] if e["date"] == today() and e["new"])
    fresh = sorted((s for s in unseen(st, all_tasks) if s not in st["open"]),
                   key=lambda s: all_tasks[s]["topic"])
    return {"review": sorted(due_today(st, all_tasks), key=lambda s: card(st, s)["due"]),
            "new": fresh[:max(0, NEW_PER_DAY - done_today)],
            "done_today": done_today}


def pick(st, all_tasks):
    """The one suggestion. Interleaved by construction: due dates scatter topics."""
    q = queue(st, all_tasks)
    for kind in ("review", "new"):
        if q[kind]:
            return q[kind][0], kind
    return None, None


def grade_of(attempts, secs, par, solution_shown):
    if solution_shown:
        return "struggled"          # a peeked answer never promotes (Aleven: hint abuse)
    if attempts == 1 and secs < par * 60:
        return "quick"
    if attempts <= 2 and secs < par * 60 * 2:
        return "pass"
    return "struggled"


def reschedule(c, grade):
    c["box"] = max(0, min(len(LADDER) - 1, c["box"] + GRADES[grade]))
    gap = LADDER[c["box"]]
    c["due"] = (date.today() + timedelta(days=gap)).isoformat()
    return gap
