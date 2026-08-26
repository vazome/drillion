"""The attempt: one timer per task, from the first open until the pass.

Time is *active* seconds — every touch adds the gap since the last one, capped at
two minutes, so a coffee break is not study. Grades, hints and the solution gate
all price themselves in that currency.
"""

import random
from datetime import datetime

from .region import cut, splice, stub
from .scheduler import grade_of, reschedule
from .state import card, today

HINT_GAP = 60  # active seconds between hints, times the level
SOLUTION_GATE = (3, 600)  # attempts, active seconds
NUDGE_SECS = 1800  # active seconds of reading before a hint is offered


class Gated(Exception):
    """A hint (or the solution) that has not been earned yet. `owed` carries what is
    still to be spent: nothing for an exhausted hint list, attempts and seconds for
    the answer. Callers report it; they never re-derive it."""

    def __init__(self, wait_secs=0, **owed):
        super().__init__(f"wait {wait_secs}s")
        self.wait_secs, self.owed = wait_secs, owed


class NoAttempt(Exception):
    """An action that needs an open attempt, on a task that has none."""


def touch(o):
    """Active seconds only: a gap longer than two minutes was a break, not work.

    Clamped at both ends. A wall clock is not monotonic — a DST fall-back or an NTP
    correction steps it backwards — and a negative tick runs the timer down: enough of
    them and the solution gate becomes unpayable and a long sitting grades as `quick`."""
    now = datetime.now()
    o["active"] += max(
        0,
        int(min((now - datetime.fromisoformat(o["last"])).total_seconds(), 120)),
    )
    o["last"] = now.isoformat()
    return o["active"]


def current(st, slug):
    """The open attempt, its timer wound on. Every acting route starts here."""
    if slug not in st["open"]:
        raise NoAttempt(slug)
    o = st["open"][slug]
    touch(o)
    return o


def open_attempt(st, slug):
    """The attempt is the timer: it lives from the first open until the pass.
    The file is already a stub, so nothing is written here."""
    o = st["open"].get(slug)
    if o:
        touch(o)
        return o
    now = datetime.now().isoformat()
    st["open"][slug] = {
        "seed": random.randint(1000, 9999),
        "attempts": 0,
        "hints": 0,
        "new": card(st, slug)["seen"] == 0,
        "started": now,
        "last": now,
        "active": 0,
        "solution_shown": False,
    }
    return st["open"][slug]


def grade_reason(o, par, grade):
    """Why `grade_of` landed where it did — the cause, never the number.

    Par is the grader's input and never reaches the browser, so the reason names what
    counted (the runs, the time, the peek) and no threshold to race. The rubric stays
    defined once: each factor is probed by asking `grade_of` what it would have graded
    on that factor alone, rather than restating its branches here."""
    if o["solution_shown"]:
        return "the solution was shown"
    if grade == "quick":
        return "one run, inside par"
    causes = []
    if (
        grade_of(o["attempts"], 0, par, False) == grade
    ):  # the runs alone cost it this grade
        causes.append("the runs it took")
    if grade_of(1, o["active"], par, False) == grade:  # ...and so did the time alone
        causes.append("the time it took")
    return " and ".join(causes)


def nudge_due(o):
    """Half an hour of active reading with nothing run and no hint taken: offer one.

    The gate opens hints silently, which is no use to the learner who is not looking at
    the panel — you cannot brute-force something nobody has told you about. Taking a hint
    or running the tests answers it, so the nudge clears itself once it has been acted on."""
    return (
        bool(o) and not o["attempts"] and not o["hints"] and o["active"] >= NUDGE_SECS
    )


def record_pass(st, slug, meta, code):
    """Grade, reschedule, log and archive a pass; return (grade, gap_days, box, reason).
    The caller writes stub(body) back to the file."""
    o = st["open"][slug]
    touch(o)
    c = card(st, slug)
    grade = grade_of(o["attempts"], o["active"], meta["minutes"], o["solution_shown"])
    reason = grade_reason(o, meta["minutes"], grade)
    gap = reschedule(c, grade)
    c["seen"] += 1
    st["log"].append(
        {
            "date": today(),
            "slug": slug,
            "grade": grade,
            "attempts": o["attempts"],
            "secs": o["active"],
            "new": o["new"],
        }
    )
    st["archive"].setdefault(slug, []).append(
        {"date": today(), "grade": grade, "code": code}
    )
    del st["open"][slug]
    return grade, gap, c["box"], reason


def abandon(st, slug, disk_src):
    """Drop the attempt and return the stubbed source; keep the work if it got anywhere."""
    body = cut(disk_src).body
    stubbed = stub(body)
    if body.strip() != stubbed.strip():
        st["archive"].setdefault(slug, []).append(
            {"date": today(), "grade": "abandoned", "code": body}
        )
    st["open"].pop(slug, None)
    return splice(disk_src, stubbed)


def next_hint(st, slug, hints):
    """Hints cost active time — clicking through them teaches nothing."""
    o = st["open"][slug]
    level = o["hints"]
    if level >= len(hints):
        raise Gated(0)  # exhausted: the solution is the next step
    wait = HINT_GAP * (level + 1) - o["active"]
    if level and wait > 0:
        raise Gated(int(wait))
    o["hints"] += 1
    return level + 1, hints[level]


def _gate(o):
    """(unlocked, attempts still owed, active seconds still owed). Pure — the one
    definition of "has this been earned"; `unlock_solution` is this plus the mark."""
    attempts, secs = SOLUTION_GATE
    if o is None:
        return False, attempts, secs
    return (
        o["solution_shown"] or (o["attempts"] >= attempts and o["active"] >= secs),
        max(0, attempts - o["attempts"]),
        max(0, secs - o["active"]),
    )


def unlock_solution(st, slug):
    """The answer opens only after real effort, and marks the attempt as peeked.
    Raises Gated carrying what is still owed, so no caller re-derives the gate."""
    o = st["open"][slug]
    unlocked, need_attempts, need_secs = _gate(o)
    if not unlocked:
        raise Gated(need_attempts=need_attempts, need_secs=need_secs)
    o["solution_shown"] = True


def solution_text(path):
    """The reference answer, read from disk. The gate is the caller's line above."""
    txt = path.read_text()
    marker = "def _reference("
    return txt[txt.index(marker) :].split("\ndef test_")[0].strip()


def attempt_view(o, hints):
    """What the page may know about an attempt: the timer, the hints, the gate.

    `o` is None when nothing is open. Every number here answers exactly as the
    matching action would, because both read `_gate` and HINT_GAP from this module."""
    unlocked, need_attempts, need_secs = _gate(o)
    shown = o["hints"] if o else 0
    next_in = None
    if o and shown < len(hints):
        next_in = max(0, HINT_GAP * (shown + 1) - o["active"]) if shown else 0
    return {
        "attempt": {
            k: o[k] for k in ("attempts", "hints", "active", "seed", "solution_shown")
        }
        if o
        else None,
        "nudge": nudge_due(o),
        "hints": {"total": len(hints), "shown": hints[:shown], "next_in": next_in},
        "solution": {
            "unlocked": unlocked,
            "need_attempts": need_attempts,
            "need_secs": need_secs,
        },
    }
