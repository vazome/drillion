# Task 2 report — `study.py` core + `test_study.py` (TDD)

Commit: `9a98eed study.py core: ast catalogue, region splice, attempt lifecycle, selfcheck`
(branch `study-ui`, parent `67d64f5`). Files changed: `study.py` (522 lines, rewritten),
`test_study.py` (390 lines, new). Nothing else was touched.

## What I implemented

**Kept, unchanged in behaviour:** `ROOT`, `LADDER`, `INTERVIEW`, `NEW_PER_DAY`, `GRADES`,
`save`, `today`, `card`, `due_today`, `pick`, `grade_of`, `reschedule`, `_solution`.
`EXDIR = ROOT/"exercises"`, `STATE = ROOT/"progress.json"` (no `STUDY_DIR`). `load()` returns
`{"focus", "cards", "open", "log", "archive"}` and fills those keys on an older file.
`card()` no longer carries `solution_shown` — per the State section it moved to the attempt.
`cmd_next/cmd_check/cmd_hint/cmd_status` and `DAILY_CAP` (unused) are gone.

**Region + splice (pure):** `bounds`, `cut` → `Region(head, lead, body, trail, tail)` dataclass,
`splice`, `strip_spec` → `Spec(editor, spec_src, spec_text, doc_offset)`, `merge_spec`, `stub`,
`has_given`, `etag` (`sha256(cut(src).body)[:12]`), `validate` (raises `Invalid(msg, line, col)`),
`write_region` (`.tmp` + `os.replace`, refuses a source whose `solve()` has no docstring).

**Catalogue:** `exercises()` is `ast.parse` + `literal_eval` of META/HINTS — no `exec`, no import
of exercise code into this process; one `try` per file so a half-edited drill is skipped rather
than breaking the menu. Each entry is `META + {path, hints, tags, read_first, region_start,
hints_line}`. `read_first(src)` returns the `# READ FIRST` comment block after the module
docstring (`#` and one space stripped), else `[]`.

**Scheduler:** `unseen` hoists `by_topic` out of the loop and, under `focus`, offers only tagged
exercises and ignores prereqs whose exercise lacks the tag. `queue(st, exs)` →
`{review (most overdue first), new (NEW_PER_DAY − done_today, lowest topic, no open attempt),
done_today}`. `pick` is now a thin wrapper over `queue`.

**Attempts:** `touch` (active seconds, gap capped at 120 s), `open_attempt`, `record_pass`
(grade → reschedule → seen+1 → log → archive → drop attempt; returns `(grade, gap_days, box)`;
the caller writes the stub), `abandon` (archives the editor text only if it differs from the
stub, drops the attempt, returns the stubbed source), `next_hint` → `(level, text)` or
`Gated(wait_secs)`, `unlock_solution` → bool.

**Running:** `run_tests(path, seed)` with `cwd=ROOT`, `-x -q --no-header --timeout=10
-p no:cacheprovider`, `timeout=60` (a timeout returns `(False, "timed out …")` instead of
raising). `summarise(out, region_start, doc_offset, hints_line)` →
`{"headline": [...], "output": tail 8 KB}`; a `file.py:NN` inside `[region_start, hints_line)`
becomes `line <editor line>`, anything else is left alone. `selfcheck()` writes
`exercises/_selfcheck_<slug>.py` = `splice(src, solve→return _reference(<same params>))`, runs
one pytest over them, deletes them in `finally`, prints `N/N ok` (plus failing slugs) and returns
the failure count. CLI: `uv run study.py` → lazy `from web import serve`; `uv run study.py
selfcheck` → exit 1 on failures.

## Tests and results

`test_study.py`: 40 plain pytest functions, no fixtures. Sweeps over all 79 `exercises/ex_*.py`
for splice round-trip, stub identity and spec round-trip; the rest are focused unit tests
(merge edge cases, the write gate, catalogue, summarise, scheduler, attempts, load/save).

```
$ uv run pytest test_study.py -q
........................................                                 [100%]
40 passed in 0.42s

$ uv run ruff check study.py test_study.py
All checks passed!

$ uv run study.py selfcheck
79/79 ok            (exit 0, ~12 s)
```

Manual checks beyond the suite (temp copies, nothing written in the repo):

- `uv run study.py` → `no web UI yet (No module named 'web') — try: uv run study.py selfcheck`,
  exit 1. `uv run study.py bogus` → `usage: study.py [serve|selfcheck]`, exit 1.
- selfcheck failure path (a copy of two exercises with a deliberately raising `_reference`):
  prints `FAILED ex_002_slicing` / `1/2 ok`, returns 1, leaves no `_selfcheck_*` files behind.
- End-to-end on a copy of `ex_036_env.py` (the given-code file): catalogue → editor text
  (`TRUTHY` kept, spec stripped, 5 lines) → 2-space edit → `validate` → `write_region` (docstring
  intact on disk) → `run_tests` → `summarise` put the learner's crash at `line 5:` and left the
  test frame `exercises/ex_036_env.py:124` alone.

## TDD evidence

RED — `test_study.py` written first, against a `study.py` that had none of the new functions:

```
$ uv run pytest test_study.py -q
FAILED test_study.py::test_stub_is_identity_on_pristine_files - AttributeErro...
FAILED test_study.py::test_spec_survives_the_round_trip_on_every_file - Attri...
... (33 more)
35 failed, 4 passed in 0.96s
```
(the 4 that passed are `grade_of`, `reschedule`, `unseen` prereqs and `_solution` — the parts the
old `study.py` already had.)

GREEN — after the rewrite:

```
$ uv run pytest test_study.py -q
........................................                                 [100%]
40 passed in 0.42s
```

A second RED/GREEN happened mid-task for the bug below: with the old `ln[4:]` line,
`uv run pytest test_study.py -q -k second_save` → `1 failed`; with the margin fix → `40 passed`.

## Bug found and fixed during the task

`merge_spec` originally re-indented the spec with `pre + line[4:]` (as the plan sketches). That
is only correct while the file on disk still has a 4-space docstring. After one save with a
2-space (or tab) body, the docstring on disk is at that indentation, and the *next* save chopped
4 characters off each spec line — corrupting the docstring (`"""WHY:` → `"WHY:`) and blowing up
inside `validate` with a raw `SyntaxError`. Found by driving the real pipeline twice on a temp
copy of `ex_036_env.py`, not by the unit tests.

Fix: dedent by the spec's own margin (`margin = len(spec_src) - len(spec_src.lstrip(" \t"))`),
which is 4 on a pristine file and whatever the last save used afterwards. Regression test:
`test_a_two_space_save_survives_a_second_save`. `validate` now also wraps the post-merge parse
so an impossible merge is a 400 (`Invalid`) rather than a 500.

## Deviations from the brief (deliberate, please confirm)

1. **`open_attempt(st, slug)`**, not `open_attempt(st, slug, meta)` — `meta` had no use
   (`new` comes from the card, the seed is random), and an unused parameter is worse than a
   one-word difference. `record_pass(st, slug, meta, code)` does take `meta` (for `minutes`).
   Task 4 must call the 2-arg form.
2. **`region_start` is the first line of the region *body***, i.e. `META.end_lineno + 1 +
   len(lead blank lines)`, not literally `META end + 1`. The plan's parenthetical and the
   remap formula `NN - region_start + 1 - …` disagree by the blank lines between META and
   `def solve` (2 in 76 files, 1 in 3); with the body-start definition the arithmetic is exact.
   Pinned by `test_exercises_reads_every_file_by_ast` (`lines[region_start-1]` starts with
   `def solve(` for ex_001) and by the summarise test.
3. **`summarise` derives `doc_end = region_start + doc_offset`** rather than taking a 5th
   argument. When code sits above `solve()` this under-counts by exactly the number of lines
   above the docstring — and those lines are inside the docstring, which never appears in a
   traceback, so every executable line still maps correctly (verified on `ex_036`). Carries a
   `# ponytail:` comment.
4. **`abandon(st, slug, disk_src)`** takes the disk source and returns the stubbed source; the
   etag check stays in `web.py`, where the lock is.
5. The spec round-trip test asserts **exact** equality, not "after normalising blank lines":
   `merge_spec` leaves blank docstring lines verbatim, so no normalisation is needed (a
   stronger assertion than the brief asked for, and it holds on all 79 files).

## Self-review findings (fixed before committing)

- `load()` first used a `BLANK` module dict with `type(empty)()` to avoid shared mutables —
  replaced with the obvious `{defaults, **st}` one-liner.
- The `merge_spec` margin bug above.
- `test_load_fills_in_missing_keys` was a no-op assertion on the real (absent) `progress.json`;
  rewritten to point `study.STATE` at a temp file, exercise `save()` too, and assert the write
  left no `.tmp` behind.
- Long unreadable literal in the `read_first` test split over two lines; `print("FAILED ", slug)`
  double space removed.

## Concerns

- **`study.py` is 522 lines**, over the ~450 guidance in the brief. The excess is docstrings and
  comments (this repo doubles as reading material for Daniel) plus the two small dataclasses;
  no function is longer than ~25 lines. Say the word and I can cut ~60 lines of prose.
- **`uv run ruff check .` reports 5 errors, all pre-existing** and unrelated: `drafts/flow3.py`
  (C413 — `ruff_plan.md` says it is Daniel's, left alone) and `rsample_drill/ex_04_typehints.py`
  + `skipped_ex_03_regex.py` (F841/F401/F811 from Daniel's partial work). Verified identical on
  `git stash` at HEAD. `uv run ruff check study.py test_study.py` is clean. Task 3 deletes
  `rsample_drill/`.
- `pick()` is kept because the brief says keep it, but nothing calls it any more — the API uses
  `queue()`. Candidate for deletion in a later task.
- `uv run pytest -q` (no path) still runs only `exercises/` + `rsample_drill/` per `testpaths`, so
  `test_study.py` is not in the default run until Task 3 adds it. The exercise stubs all fail
  there by design.
- `STUDY.md` still documents `check/hint/next/status` and `STUDY_DIR`; Task 8 owns that.
- `selfcheck` proves the plumbing (signatures, splice, harness), not that a `_reference` is
  *correct* — `solve` and `_reference` are the same function by construction, so a wrong
  reference still passes. That matches "does the whole set still work?" in the plan.
