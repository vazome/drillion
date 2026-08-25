# Phase B — Exercism drills in the study format

Source: `/tmp/exercism-python` (shallow clone of github.com/exercism/python, MIT licence). Every
derived file carries `# SOURCE: exercism/python <concept|practice>/<slug> (MIT, adapted)` as the
first comment line after the module docstring, and STUDY.md gets one attribution line.

Why: Daniel wants Exercism's tasks (good task writing, proper concept grouping) inside the one
tagged catalogue. Exercism's concept slugs become tags (`dicts`, `string-methods`, `sets`, …),
which is the "concept grouping" he asked for; our section tags stay alongside.

## Scope (batch 1 — 70 Exercism exercises → ~80 drill files)

**Concept exercises (20; `electric-bill` skipped — no concept in config.json).** Each becomes 1–3
drills; topic numbers `200 + 3k + i` (k = row below, i = sub-drill 0..2). Split when the exercise
has more than 4 required functions; group by sub-concept; ≤ 4 functions per drill.

| k | slug | concept tag | prerequisites (Exercism) |
|---|---|---|---|
| 0 | guidos-gorgeous-lasagna | basics | — |
| 1 | ghost-gobble-arcade-game | bools | basics |
| 2 | currency-exchange | numbers | basics |
| 3 | meltdown-mitigation | conditionals | basics, bools |
| 4 | black-jack | comparisons | basics, bools, conditionals |
| 5 | little-sisters-vocab | strings | basics, conditionals |
| 6 | little-sisters-essay | string-methods | basics, strings |
| 7 | card-games | lists | conditionals, strings |
| 8 | chaitanas-colossal-coaster | list-methods | lists |
| 9 | making-the-grade | loops | basics, comparisons, lists, list-methods, strings |
| 10 | pretty-leaflet | string-formatting | strings, loops, lists |
| 11 | tisbury-treasure-hunt | tuples | bools, loops, conditionals, numbers |
| 12 | inventory-management | dicts | loops, lists, tuples |
| 13 | mecha-munch-management | dict-methods | dicts |
| 14 | locomotive-engineer | unpacking-and-multiple-assignment | loops, lists, tuples, dicts |
| 15 | cater-waiter | sets | basics, dicts, lists, loops, tuples |
| 16 | ellens-alien-game | classes | basics, bools, comparisons, loops, dicts, lists, numbers, sets, strings, tuples |
| 17 | plane-tickets | generators | conditionals, dicts, lists, loops, classes |
| 18 | log-levels | enums | classes, conditionals, comprehensions, loops, sequences, string-methods, tuples |
| 19 | restaurant-rozalynn | none | bools, conditionals, functions, dict-methods, list-methods, loops |

**Practice exercises (50), topic numbers 300–349, one drill each** (single function → `solve`
is that function; a class → `solve()` returns the class, like `ex_096_async_cm`):
300 two-fer · 301 leap · 302 raindrops · 303 bob · 304 reverse-string · 305 isogram · 306 pangram ·
307 anagram · 308 hamming · 309 rna-transcription · 310 word-count · 311 acronym ·
312 run-length-encoding · 313 roman-numerals · 314 luhn · 315 isbn-verifier · 316 phone-number ·
317 matching-brackets · 318 series · 319 sum-of-multiples · 320 etl · 321 flatten-array ·
322 grains · 323 collatz-conjecture · 324 triangle · 325 secret-handshake · 326 space-age ·
327 atbash-cipher · 328 rotational-cipher · 329 scrabble-score · 330 pig-latin ·
331 protein-translation · 332 transpose · 333 sublist · 334 prime-factors · 335 nth-prime ·
336 sieve · 337 saddle-points · 338 clock · 339 high-scores · 340 grade-school · 341 allergies ·
342 circular-buffer · 343 robot-simulator · 344 grep · 345 tournament · 346 change ·
347 all-your-base · 348 largest-series-product · 349 binary-search.
Later batch (not now): wordy, matrix, kindergarten-garden, twelve-days, proverb, diamond,
crypto-square, pythagorean-triplet, rectangles, spiral-matrix, and the d5+ set.

## Per-drill contract (identical to the existing files; model: `exercises/ex_001_fstrings.py`,
class-returning model: `exercises/ex_096_async_cm.py`)

- File `exercises/ex_<NNN>_<slug_with_underscores>.py`; module docstring = one line;
  `# SOURCE:` line; `# READ FIRST:` block with 2–3 links taken from
  `concepts/<concept>/links.json` (or the exercise's `.docs/introduction.md` links); for concept
  drills also `#   CONCEPT: <slug> — one sentence from concepts/<slug>/introduction.md`.
- `META = {"topic": N, "title": "<concept or story> — <what you build>", "minutes": M,
  "prereqs": [...], "tags": [...]}` — no `tier`. `minutes`: concept drills 12–15; practice by
  Exercism difficulty d1→10, d2→15, d3→20, d4→25.
  `tags`: `exercism` + the Exercism concept slugs (`practices` for practice exercises, `concepts`
  for concept exercises; both lists as-is, kebab-case) + one section tag by this map:
  basics/bools/numbers/conditionals/comparisons/strings/string-methods/string-formatting/loops/
  lists/list-methods/tuples/unpacking-and-multiple-assignment/functions/function-arguments/
  higher-order-functions/anonymous-functions/recursion/none/classes/class-*/rich-comparisons/
  operator-overloading/decorators → `core`; dicts/dict-methods/sets/enums/generators/
  generator-expressions/iteration/iterators/itertools/list-comprehensions/sequences/collections →
  `data-structures`; regular-expressions/with-statement → `files-text`;
  raising-and-handling-errors/user-defined-errors → `errors`; no concept → `core`.
  `prereqs`: the topic numbers of the concept drills for the Exercism prerequisites listed above
  (first sub-drill's number), only those that exist in this batch; practice exercises use their
  config.json `prerequisites` the same way.
- `solve` docstring opens `WHY:` (the Exercism story in plain words: who needs this and why),
  `YOU GET:` (each argument, with a literal example), `YOU RETURN:` (exact type/shape), then
  `─── exact rules ───` with the precise rules and 2–3 worked examples. For multi-function drills:
  "YOU RETURN: a dict with these functions: …" and one paragraph per function. Keep it under
  ~60 lines; the instructions.md is the source, rewritten, not pasted.
- `HINTS`: exactly 3 — nudge → strategy → the same idea worked through on *different* data.
  Use `.docs/hints.md` when present. No solutions in hints.
- Machinery: `_gen(r)` builds random valid inputs from a seeded `random.Random` (fresh data every
  sitting — vary sizes, values, names; for cipher/number drills vary the inputs, not the rules);
  `_reference(...)` adapted from `.meta/example.py` / `.meta/exemplar.py` (must be correct and
  idiomatic); `test_solve()` loops 4–6 generated cases comparing `solve(...)` with
  `_reference(...)` **and** asserts 3–6 canonical cases copied from the Exercism test file against
  `solve`. For error-raising exercises assert `pytest.raises(ValueError)` with the exact message
  Exercism specifies. Never import the Exercism package; the file is self-contained.
- The stub body is exactly `raise NotImplementedError`; `solve` is the last statement before
  `HINTS`; given code (if any) sits above `solve` with a `# given — do not edit` comment.

## Pipeline

1. Branch `exercism-drills` from `study-ui` **after Task 3 (migration) is merged**, in a git
   worktree at `/home/daniel/study-exercism` so it never collides with the SDD tasks.
2. Batches of 5–7 exercises per implementer (Opus). Each implementer: reads its exercises'
   `.docs/*.md`, `.meta/example.py|exemplar.py`, the test file, `concepts/<slug>/links.json`;
   writes the drills; runs for its files: `uv run ruff check <files>`, a stub run (`pytest <file>`
   must fail with `NotImplementedError`), and the reference run via
   `uv run study.py selfcheck` (all green) — then commits **only its files**
   (`git add exercises/ex_3xx_*.py`). Report file per batch.
3. A reviewer (Opus) per batch checks: WHY/YOU GET/YOU RETURN quality, hints escalate and don't
   leak, `_gen` variety, canonical cases present, tags/prereqs/topic numbers match the table,
   SOURCE line present. Fix loop as in SDD.
4. Controller (Fable): sample-read 1 in 5 files, run full `selfcheck` + `pytest --collect-only`,
   then merge `exercism-drills` into `study-ui`; STUDY.md attribution line; `python-checklist.md`
   untouched.

## Token budget note
~14 batches × (implementer + reviewer) ≈ 14 × ~150k = ~2M tokens. Within the session budget.
