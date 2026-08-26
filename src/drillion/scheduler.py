"""The Leitner ladder: what comes back today, what is new, and what a pass is worth.

A 5-box ladder, not FSRS: the horizon is 12 weeks and Cepeda 2008 puts the optimal
gap at 10-20% of that, so intervals are fixed rather than fitted. ponytail: a
5-element list beats a dependency with 21 trained weights we have no data to fit.
"""

from datetime import date, timedelta

from .state import card, today

LADDER = [2, 4, 8, 16, 28]           # days until the next sighting, per box
INTERVIEW = date(2026, 11, 2)        # everything recycles before this
NEW_PER_DAY = 2
GRADES = {"fail": -2, "struggled": 0, "pass": +1, "easy": +2}


def due_today(st, exs):
    return [s for s in exs if card(st, s)["seen"] > 0 and card(st, s)["due"] <= today()]


def unseen(st, exs):
    """Unstarted exercises whose prereqs are cleared. Under a focus tag, prereqs
    outside the tag are ignored — else a track stalls on an exercise it lacks."""
    focus = st.get("focus")
    by_topic = {m["topic"]: s for s, m in exs.items()}
    ready = []
    for slug, meta in exs.items():
        if card(st, slug)["seen"] or (focus and focus not in meta.get("tags", [])):
            continue
        prereqs = [by_topic[p] for p in meta.get("prereqs", []) if p in by_topic]
        if focus:
            prereqs = [s for s in prereqs if focus in exs[s].get("tags", [])]
        if all(card(st, s)["box"] >= 1 for s in prereqs):
            ready.append(slug)
    return ready


def queue(st, exs):
    """Today: every due review (most overdue first), then the new picks left."""
    done_today = sum(1 for e in st["log"] if e["date"] == today() and e["new"])
    fresh = sorted((s for s in unseen(st, exs) if s not in st["open"]),
                   key=lambda s: exs[s]["topic"])
    return {"review": sorted(due_today(st, exs), key=lambda s: card(st, s)["due"]),
            "new": fresh[:max(0, NEW_PER_DAY - done_today)],
            "done_today": done_today}


def pick(st, exs):
    """The one suggestion. Interleaved by construction: due dates scatter topics."""
    q = queue(st, exs)
    for kind in ("review", "new"):
        if q[kind]:
            return q[kind][0], kind
    return None, None


def grade_of(attempts, secs, par, solution_shown):
    if solution_shown:
        return "struggled"          # a peeked answer never promotes (Aleven: hint abuse)
    if attempts == 1 and secs < par * 60:
        return "easy"
    if attempts <= 2 and secs < par * 60 * 2:
        return "pass"
    return "struggled"


def reschedule(c, grade):
    c["box"] = max(0, min(len(LADDER) - 1, c["box"] + GRADES[grade]))
    gap = LADDER[c["box"]]
    nxt = date.today() + timedelta(days=gap)
    cutoff = INTERVIEW - timedelta(days=7)
    c["due"] = min(nxt, cutoff).isoformat()
    return (min(nxt, cutoff) - date.today()).days
