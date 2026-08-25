#!/usr/bin/env python3
"""Spaced-repetition drill runner.

    uv run study            what to do now
    uv run study.py check      grade the current exercise
    uv run study.py hint       next hint (gated)
    uv run study status     progress
    STUDY_DIR=rsample_drill uv run study.py   same, for the take-home track

Design notes live in STUDY.md. Scheduler is a 5-box Leitner ladder, not FSRS:
the horizon is 12 weeks and Cepeda 2008 puts the optimal gap at 10-20% of that,
so intervals are fixed rather than fitted. ponytail: 5-element list beats a
dependency with 21 trained weights we have no data to fit.
"""

import argparse
import json
import os
import random
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).parent
EXDIR = ROOT / os.environ.get("STUDY_DIR", "exercises")      # STUDY_DIR=rsample_drill for the take-home track
STATE = ROOT / "progress.json" if EXDIR.name == "exercises" else EXDIR / "progress.json"

LADDER = [2, 4, 8, 16, 28]          # days until next sighting, per box
INTERVIEW = date(2026, 11, 2)        # everything recycles before this
NEW_PER_DAY = 2
DAILY_CAP = 5

GRADES = {"fail": -2, "struggled": 0, "pass": +1, "easy": +2}


# ---------------------------------------------------------------- state
def load():
    if not STATE.exists():
        return {"cards": {}, "log": [], "current": None}
    return json.loads(STATE.read_text())


def save(st):
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(st, indent=1))
    os.replace(tmp, STATE)          # atomic: a crash mid-write can't eat months of progress


def today():
    return date.today().isoformat()


# ---------------------------------------------------------------- exercises
def exercises():
    """{slug: META} for every ex_*.py that parses."""
    out = {}
    if str(EXDIR) not in sys.path:
        sys.path.insert(0, str(EXDIR))      # so `from _lib import rng` resolves
    for f in sorted(EXDIR.glob("ex_*.py")):
        ns = {}
        try:
            exec(compile(f.read_text(), f.name, "exec"), ns)  # noqa: S102
        except Exception:  # noqa: BLE001, S112 — a half-edited file shouldn't break the menu
            continue
        if "META" in ns:
            out[f.stem] = {**ns["META"], "path": f, "hints": ns.get("HINTS", [])}
    return out


def card(st, slug):
    return st["cards"].setdefault(slug, {"box": 0, "due": today(), "seen": 0, "solution_shown": False})


def due_today(st, exs):
    return [s for s in exs if card(st, s)["due"] <= today() and card(st, s)["seen"] > 0]


def unseen(st, exs):
    ready = []
    for slug, meta in exs.items():
        if card(st, slug)["seen"]:
            continue
        prereqs = meta.get("prereqs", [])
        by_topic = {m["topic"]: s for s, m in exs.items()}
        if all(card(st, by_topic[p])["box"] >= 1 for p in prereqs if p in by_topic):
            ready.append(slug)
    return ready


def pick(st, exs):
    """Reviews first (most overdue), then new. Interleaved by construction:
    consecutive picks come from different topics because due dates scatter."""
    reviews = sorted(due_today(st, exs), key=lambda s: card(st, s)["due"])
    if reviews:
        return reviews[0], "review"
    done_today = sum(1 for e in st["log"] if e["date"] == today() and e["new"])
    if done_today < NEW_PER_DAY:
        new = unseen(st, exs)
        if new:
            return min(new, key=lambda s: exs[s]["topic"]), "new"
    return None, None


# ---------------------------------------------------------------- grading
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


def run_tests(path, seed):
    env = {**os.environ, "STUDY_SEED": str(seed)}
    r = subprocess.run(
        [sys.executable, "-m", "pytest", str(path), "-x", "-q", "--timeout=10", "--no-header"],
        env=env, capture_output=True, text=True, check=False,
    )
    return r.returncode == 0, r.stdout


# ---------------------------------------------------------------- commands
def cmd_next(st, exs):
    cur = st.get("current")
    if cur and cur["slug"] in exs:
        print(f"still open: {exs[cur['slug']]['title']}")
        print(f"  file  {exs[cur['slug']]['path'].relative_to(ROOT)}")
        print("  then  uv run study.py check")
        return
    slug, kind = pick(st, exs)
    if not slug:
        print("nothing due. rest is training too — see you tomorrow.")
        return cmd_status(st, exs)
    m = exs[slug]
    c = card(st, slug)
    seed = random.randint(1000, 9999)
    st["current"] = {"slug": slug, "seed": seed, "attempts": 0, "hints": 0,
                     "started": datetime.now().isoformat(), "new": kind == "new"}
    c["solution_shown"] = False
    save(st)
    print(f"[{kind}]  topic {m['topic']} — {m['title']}   (~{m['minutes']} min)")
    print(f"  file  {m['path'].relative_to(ROOT)}")
    print("  edit  solve()  — spec is in its docstring")
    print("  then  uv run study.py check")
    if kind == "review":
        print(f"  seen {c['seen']}x, box {c['box']+1}/5 — data is freshly generated, "
              f"the old answer won't fit")


def cmd_check(st, exs):
    cur = st.get("current")
    if not cur:
        print("nothing open. `uv run study.py` first.")
        return
    slug = cur["slug"]
    m = exs[slug]
    cur["attempts"] += 1
    ok, out = run_tests(m["path"], cur["seed"])
    if not ok:
        save(st)
        print(out.strip()[-1500:])
        print(f"\nattempt {cur['attempts']} — not yet. `uv run study.py hint` if stuck.")
        return
    secs = (datetime.now() - datetime.fromisoformat(cur["started"])).total_seconds()
    c = card(st, slug)
    g = grade_of(cur["attempts"], secs, m["minutes"], c["solution_shown"])
    gap = reschedule(c, g)
    c["seen"] += 1
    st["log"].append({"date": today(), "slug": slug, "grade": g,
                      "attempts": cur["attempts"], "secs": int(secs), "new": cur["new"]})
    st["current"] = None
    save(st)
    print(f"green in {int(secs//60)}m{int(secs%60):02d}s, {cur['attempts']} attempt(s) -> {g.upper()}")
    print(f"back in {gap} days (box {c['box']+1}/5)")
    if g == "struggled" and c["solution_shown"]:
        print("solution was shown, so this didn't promote — you'll get a fresh variant soon.")
    print("\nnext: uv run study.py")


def cmd_hint(st, exs):
    cur = st.get("current")
    if not cur:
        print("nothing open.")
        return
    m = exs[cur["slug"]]
    hints = m["hints"]
    secs = (datetime.now() - datetime.fromisoformat(cur["started"])).total_seconds()
    lvl = cur["hints"]
    if lvl >= len(hints):
        if cur["attempts"] < 3 or secs < 600:
            print(f"solution unlocks after 3 attempts and 10 minutes "
                  f"(you're at {cur['attempts']} and {int(secs//60)}m). Keep going.")
            return
        card(st, cur["slug"])["solution_shown"] = True
        save(st)
        print(_solution(m["path"]))
        print("\n-- read it, then write it yourself. This won't count as a pass,")
        print("   and a variant lands in your queue within 2 days.")
        return
    if lvl > 0 and secs < 60 * (lvl + 1):
        print("wait a bit and try something first — hint-clicking doesn't teach.")
        return
    cur["hints"] += 1
    save(st)
    print(f"hint {lvl+1}/{len(hints)}:  {hints[lvl]}")


def _solution(path):
    txt = path.read_text()
    marker = "def _reference("
    return txt[txt.index(marker):].split("\ndef test_")[0].strip()


def cmd_status(st, exs):
    boxes = [0] * 5
    for slug in exs:
        c = st["cards"].get(slug)
        if c and c["seen"]:
            boxes[c["box"]] += 1
    seen = sum(boxes)
    print(f"\n{seen}/{len(exs)} exercises started   "
          f"{(INTERVIEW - date.today()).days} days to target date")
    for i, n in enumerate(boxes):
        print(f"  box {i+1} (every {LADDER[i]:>2}d)  {'#' * n}{'' if n else '-'}")
    d = len(due_today(st, exs))
    print(f"\ndue now: {d}")
    recent = st["log"][-20:]
    if recent:
        fails = sum(1 for e in recent if e["grade"] in ("fail", "struggled"))
        pct = round(100 * fails / len(recent))
        verdict = ("intervals too timid, widening" if pct < 10 else
                   "too aggressive, ease off" if pct > 30 else "about right")
        print(f"last {len(recent)}: {pct}% struggled — {verdict}")


def main():
    p = argparse.ArgumentParser(description="spaced-repetition drills")
    p.add_argument("cmd", nargs="?", default="next",
                   choices=["next", "check", "hint", "status"])
    a = p.parse_args()
    st, exs = load(), exercises()
    if not exs:
        print(f"no exercises found in {EXDIR}")
        return
    {"next": cmd_next, "check": cmd_check, "hint": cmd_hint, "status": cmd_status}[a.cmd](st, exs)


if __name__ == "__main__":
    main()
