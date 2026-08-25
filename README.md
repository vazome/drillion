# The drill system

```bash
uv run study                                 # open the drills in a browser
uv run study selfcheck                       # every drill still passes with its reference
uv run pytest exercises/ex_019_counter.py    # run one drill by hand
docker compose up                            # the same app in a container
```

Edit `solve()` in the file it names. The spec is that function's docstring. Nothing else in the file is yours to touch.

## Why it's built this way

**Fresh data every sitting.** Each exercise ships a generator, so when a topic comes back in 8 days the IPs, names and numbers are different. You can't recall the answer because that exact answer never existed. This is the one feature that stops spaced repetition from degrading into memorising files.

**A 5-box ladder, not a fancy algorithm.** Pass an exercise and it returns in 2 → 4 → 8 → 16 → 28 days. Fail and it drops two boxes instead of resetting, because a lapse here costs 30 minutes, not 5 seconds. Nothing is ever scheduled past a week before the target date.

The obvious choice was FSRS (what Anki uses). Tested it: with default settings a topic you get right three times comes back in 46 days, then 90 — i.e. after the interview. It's tuned for people memorising vocabulary over years. Fixed intervals are also the *more* correct choice here: with a known deadline, the research (Cepeda 2008) puts the optimal gap at 10–20% of the time remaining, which is a number you can just write down.

**Grades are computed, not self-reported.** First try under par = EASY (+2 boxes). Two tries = PASS (+1). Slow, or three-plus tries = STRUGGLED (stays put). Looked at the solution = never promotes, regardless of the tests going green. That last rule is the important one: hint-assisted passes are how people finish a curriculum and still can't code.

**Hints are gated.** Three levels — a nudge, then a strategy, then the same idea worked through on *different* data. The full solution unlocks only after 3 attempts and 10 minutes, and taking it queues a fresh variant within days. Levels are 60s apart because clicking through hints is the best-documented way to feel productive while learning nothing.

**Reviews come before new material,** capped at 2 new topics a day. Reviews arrive interleaved rather than blocked — mixing confusable topics is the largest effect in the whole literature (d ≈ 0.83), and it will feel worse than drilling one thing at a time. That feeling is documented and wrong.

## Adding exercises

One file, `exercises/ex_<topic>_<name>.py`, copy the shape of an existing one:

- `META` — topic number from `python-checklist.md`, title, minutes (used as par time), `prereqs` (topic numbers that gate it), `tags` (see below)
- `solve()` — stub with the spec in its docstring
- `HINTS` — exactly 3, escalating, the last one worked on different data
- `_gen(r)` — build inputs from `r` (a seeded Random)
- `_reference(...)` — correct implementation; tests compare yours against it
- `test_solve()` — loop a few generated cases

Whole-task drills add `practices: [...]` listing component topics.

**The region contract.** Everything between `META` and `HINTS` is the learner's: that is the text the
editor shows and the only text a save may replace. `solve` must be the last statement in it, and any
given code (constants, exception classes, a toy app) goes above `solve`, never below.

Sanity check before trusting a new exercise:

```bash
uv run python -c "
import sys, os; sys.path.insert(0,'exercises')
os.environ['STUDY_SEED']='42'
import ex_019_counter as m; m.solve = m._reference; m.test_solve(); print('ok')"
```

## Current coverage

87 drills authored (topics 1–101 with gaps), plus Exercism-derived drills (topics 200+) as they land. The scheduler introduces 2 new ones a day, so the backlog is meant to be larger than what you see in a week.

## Tags

One catalogue, no folders: what an exercise belongs to is `META["tags"]`.

- **Section** — exactly one per exercise, from the topic number: `core` (1–17) ·
  `data-structures` (18–25) · `files-text` (26–34) · `stdlib-ops` (35–42) · `errors` (43–47, 81) ·
  `http` (48–53) · `concurrency` (54–56, 94–97) · `testing` (57–61, 98–99) · `packaging` (62–67) ·
  `cloud` (68–72) · `whole-task` (73–80, 82–86, 100–101) · `llm` (88–93)
- **Library** — from the file's own imports: `boto3` (boto3/moto) · `requests` (requests/responses) ·
  `langchain` (langchain-core) · `fastapi` (fastapi/httpx) · `asyncio`
- **Track** — `rsample`: the 18 drills built around the rsample RAG take-home (10 general drills that
  carry an extra `TAKE-HOME:` line in their READ FIRST block, plus 8 written for it, topics 94–101).

`focus` in `progress.json` is a single tag that restricts which *new* exercises get offered — the
replacement for the old second folder. Reviews and the open catalogue ignore it.
