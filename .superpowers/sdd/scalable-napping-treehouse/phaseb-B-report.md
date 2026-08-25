# Phase B — batch B report (concept exercises k=5..9, topics 215–229)

Five Exercism concept exercises became **8 drill folders** under `exercises/`, each
`README.md` (frontmatter → `# title` → `## Why` → `## Introduction` → `## Instructions` →
`## You get` / `## You return` / `## Rules` → `## Exercism hints` → `## Read first` →
attribution → `## Hints` with exactly three `### Hint N`) plus `drill.py` (learner region
above the byte-identical `# ══ machinery` marker, machinery below).

Exercism's `introduction.md`, `instructions.md` and `hints.md` are in each README
**verbatim**, headings demoted one level (`# Introduction`/`# Instructions`/`# Hints`
dropped, `## 1. Task` → `### 1. Task`), `~~~~exercism/note` blocks folded into
`> [!NOTE]` alerts with their link-reference definitions hoisted out of the quote.
Split exercises carry the **full** Instructions in both sub-drills (the `212`/`213`
model), with `## You get` and `## Rules` naming which tasks the drill covers.

## The drills

| topic | folder | title | minutes | tags | prereqs | Exercism tasks |
| --- | --- | --- | --- | --- | --- | --- |
| 215 | `215_little_sisters_vocab` | strings — prefixes, suffixes and slices | 15 | `[exercism, strings, core]` | `[200, 209]` | 1–4 (all) |
| 218 | `218_little_sisters_essay` | string-methods — the essay clean-up pass | 12 | `[exercism, string-methods, core]` | `[200, 215]` | 1–4 (all) |
| 221 | `221_card_games` | lists — the poker round tracker | 12 | `[exercism, lists, core]` | `[209, 215]` | 1–3 |
| 222 | `222_card_games` | lists — Black Joe hand averages | 15 | `[exercism, lists, core]` | `[209, 215, 221]` | 4–7 |
| 224 | `224_chaitanas_colossal_coaster` | list-methods — joining the coaster queue | 12 | `[exercism, list-methods, core]` | `[221]` | 1–3 |
| 225 | `225_chaitanas_colossal_coaster` | list-methods — thinning out the coaster queue | 15 | `[exercism, list-methods, core]` | `[221, 224]` | 4–7 |
| 227 | `227_making_the_grade` | loops — rounding and counting exam scores | 12 | `[exercism, loops, core]` | `[200, 212, 215, 221, 224]` | 1–3 |
| 228 | `228_making_the_grade` | loops — grade bands, rankings and the first perfect score | 15 | `[exercism, loops, core]` | `[200, 212, 215, 221, 224, 227]` | 4–6 |

Every `.meta/config.json` lists exactly one concept, so no extra concept tags were added.
Prereqs are the Exercism prerequisites mapped through the concept → first-sub-drill table
(basics 200 · comparisons 212 · conditionals 209 · strings 215 · lists 221 · list-methods 224),
plus the previous sub-drill's topic for every `i > 0` drill.

Splits (≤ 4 functions per drill, grouped by sub-concept):

- **card-games** (7 functions) → 221 *building/joining/searching a list*
  (`get_rounds`, `concatenate_rounds`, `list_contains_round`) and 222 *interrogating a list of
  numbers* (`card_average`, `approx_average_is_average`, `average_even_is_average_odd`,
  `maybe_double_last`).
- **chaitanas-colossal-coaster** (7 functions) → 224 *growing the queue*
  (`add_me_to_the_queue`, `find_my_friend`, `add_me_with_my_friends`) and 225 *shrinking,
  counting and copying it* (`remove_the_mean_person`, `how_many_namefellows`,
  `remove_the_last_person`, `sorted_names`).
- **making-the-grade** (6 functions) → 227 *the three loop shapes* (`round_scores` = `while` +
  `pop`, `count_failed_students` = `for` + counter, `above_threshold` = `for` + accumulator) and
  228 *`range` with a step, `enumerate`, `break`* (`letter_grades`, `student_ranking`,
  `perfect_score`).
- little-sisters-vocab and little-sisters-essay have exactly 4 functions each → one drill each.

## Deviations from the sources

1. **`card-games/.docs/introduction.md` contains a raw HTML `<table>`** (the
   left/right indexing diagram, with `<br>` and inline `style=` attributes). The renderer
   takes no raw HTML, so in `221_card_games` and `222_card_games` that block is a plain
   GFM table with the two direction labels ("index from left ⟹", "⟸ index from right")
   as ordinary lines above and below it, and the `<br>` tags dropped. Every cell value is
   preserved. This is the **only** Exercism line not carried over byte-for-byte —
   a mechanical coverage check reports `missing lines: 0` for all six other drills and
   exactly those 8 HTML lines for the two card-games drills (see Verification).
2. **`making-the-grade`'s exemplar `letter_grades` contradicts the instructions.** The
   exemplar does `for score in range(41, highest, increment)`, which yields **five**
   thresholds whenever `(highest - 40) % 8 == 2` (e.g. `highest` 66, 74, 82, 90, 98) because
   `round()` sends the half increment down. The instructions promise one lower threshold per
   `D`, `C`, `B`, `A` — four. `_reference` therefore implements the instructions
   (`[41 + increment * band for band in range(4)]`), which reproduces all five canonical
   cases exactly. To keep a learner who followed Exercism's own `range()` hint from failing
   on a value the canonical tests never exercise, `_gen` draws `highest` only from values
   where both readings agree; the README carries a `> [!WARNING]` explaining the trap.
3. **`chaitanas-colossal-coaster/.docs/hints.md` opens with `# General`** (level 1, no
   `# Hints` title). It is demoted to `### General` so it sits under our `## Exercism hints`
   like every other hint sub-heading, rather than rendering as a page-sized title.
   `card-games` hints.md has an empty `## General` section; it is kept, empty, as `### General`.
4. **`maybe_double_last` and `round_scores` mutate their argument in Exercism's exemplars.**
   `_reference` keeps that behaviour (it is what the instructions describe), and `test_solve`
   hands `solve()` and `_reference()` their own copies of every list, so a learner who writes
   a non-mutating version passes too — exactly as on Exercism, whose tests `deepcopy` for the
   same reason.
5. **Tighter than Exercism, deliberately, and documented in each README:** the boolean-returning
   functions are asserted with `is True` / `is False` (Exercism uses `assertEqual`), the
   identity contracts Exercism checks with `assertIs` / `assertIsNot` are asserted here too
   (`add_me_to_the_queue`, `add_me_with_my_friends`, `remove_the_mean_person` return the list
   they were given; `sorted_names` returns a different one and leaves the queue's order alone;
   `remove_the_last_person` shortens the queue), and `round_scores` must return `int`s
   (`round(n, 0)` gives a float). Each of these has a `> [!WARNING]` in the README.
6. `_reference` uses an f-string in `student_ranking` where the exemplar concatenates with
   `str()` and `+`; same output, idiomatic.

## Verification

### ruff

```
$ uv run ruff check exercises/215_little_sisters_vocab/drill.py \
    exercises/218_little_sisters_essay/drill.py exercises/221_card_games/drill.py \
    exercises/222_card_games/drill.py exercises/224_chaitanas_colossal_coaster/drill.py \
    exercises/225_chaitanas_colossal_coaster/drill.py \
    exercises/227_making_the_grade/drill.py exercises/228_making_the_grade/drill.py
All checks passed!
```

### Stub run — every drill fails with NotImplementedError

```
$ uv run pytest exercises/<slug> -q -p no:cacheprovider
215_little_sisters_vocab        drill.py:2: NotImplementedError   1 failed in 0.06s
218_little_sisters_essay        drill.py:2: NotImplementedError   1 failed in 0.06s
221_card_games                  drill.py:2: NotImplementedError   1 failed in 0.06s
222_card_games                  drill.py:2: NotImplementedError   1 failed in 0.06s
224_chaitanas_colossal_coaster  drill.py:2: NotImplementedError   1 failed in 0.06s
225_chaitanas_colossal_coaster  drill.py:2: NotImplementedError   1 failed in 0.06s
227_making_the_grade            drill.py:2: NotImplementedError   1 failed in 0.06s
228_making_the_grade            drill.py:2: NotImplementedError   1 failed in 0.07s
```

### Reference run — `solve = _reference`, `test_solve()` under STUDY_SEED 1, 2, 42

```
$ uv run python /tmp/phb/refrun.py       # importlib-loads each drill.py, sets solve = _reference
seed  1  215_little_sisters_vocab         ok
seed  1  218_little_sisters_essay         ok
seed  1  221_card_games                   ok
seed  1  222_card_games                   ok
seed  1  224_chaitanas_colossal_coaster   ok
seed  1  225_chaitanas_colossal_coaster   ok
seed  1  227_making_the_grade             ok
seed  1  228_making_the_grade             ok
seed  2  215_little_sisters_vocab         ok
seed  2  218_little_sisters_essay         ok
seed  2  221_card_games                   ok
seed  2  222_card_games                   ok
seed  2  224_chaitanas_colossal_coaster   ok
seed  2  225_chaitanas_colossal_coaster   ok
seed  2  227_making_the_grade             ok
seed  2  228_making_the_grade             ok
seed 42  215_little_sisters_vocab         ok
seed 42  218_little_sisters_essay         ok
seed 42  221_card_games                   ok
seed 42  222_card_games                   ok
seed 42  224_chaitanas_colossal_coaster   ok
seed 42  225_chaitanas_colossal_coaster   ok
seed 42  227_making_the_grade             ok
seed 42  228_making_the_grade             ok
failures: 0
```

Also swept seeds 1–60 (480 runs) for `_gen` edge cases — `failures: 0`.

### selfcheck

```
$ uv run study selfcheck
120/120 ok
```

(120, not 112 — other Phase B implementers were adding their folders at the same time.
All eight batch-B slugs are in the ok set; no `FAILED` lines.)

### Catalogue

```
$ uv run python -c "from study.catalogue import exercises; ..."
215_little_sisters_vocab         topic=215  minutes=15  hints=3 tags=['exercism', 'strings', 'core'] prereqs=[200, 209] spec=18174 chars
218_little_sisters_essay         topic=218  minutes=12  hints=3 tags=['exercism', 'string-methods', 'core'] prereqs=[200, 215] spec=12329 chars
221_card_games                   topic=221  minutes=12  hints=3 tags=['exercism', 'lists', 'core'] prereqs=[209, 215] spec=18514 chars
222_card_games                   topic=222  minutes=15  hints=3 tags=['exercism', 'lists', 'core'] prereqs=[209, 215, 221] spec=19384 chars
224_chaitanas_colossal_coaster   topic=224  minutes=12  hints=3 tags=['exercism', 'list-methods', 'core'] prereqs=[221] spec=18726 chars
225_chaitanas_colossal_coaster   topic=225  minutes=15  hints=3 tags=['exercism', 'list-methods', 'core'] prereqs=[221, 224] spec=18951 chars
227_making_the_grade             topic=227  minutes=12  hints=3 tags=['exercism', 'loops', 'core'] prereqs=[200, 212, 215, 221, 224] spec=19131 chars
228_making_the_grade             topic=228  minutes=15  hints=3 tags=['exercism', 'loops', 'core'] prereqs=[200, 212, 215, 221, 224, 227] spec=19557 chars

all 8 batch-B slugs present; catalogue has 119 drills
```

The same run asserts, per slug: `## Why`, `## Introduction`, `## Instructions`, `## You get`,
`## You return`, `## Rules`, `## Exercism hints`, `## Read first` all present; `spec_md`
starts with `# <title>` matching the frontmatter `title`; the attribution line is in the spec;
`## Hints` did not leak into the spec; code fences balanced; no raw HTML outside inline code.

### Exercism content coverage

Every non-blank, non-heading line of each `introduction.md`, `instructions.md` and
`hints.md` appears in the matching README (blockquote prefixes normalised):

```
215_little_sisters_vocab         missing lines: 0
218_little_sisters_essay         missing lines: 0
221_card_games                   missing lines: 8   (the <table>/<tr>/<td>/<br> lines, rewritten — deviation 1)
222_card_games                   missing lines: 8   (same block)
224_chaitanas_colossal_coaster   missing lines: 0
225_chaitanas_colossal_coaster   missing lines: 0
227_making_the_grade             missing lines: 0
228_making_the_grade             missing lines: 0
```

### Marker line

All eight `drill.py` marker lines are byte-identical to `exercises/303_bob/drill.py`'s
(checked as raw bytes), and each sits at line 5 with the learner region above it.

### Scope

```
$ git status --porcelain | grep -E '215_|218_|221_|222_|224_|225_|227_|228_'
?? exercises/215_little_sisters_vocab/
?? exercises/218_little_sisters_essay/
?? exercises/221_card_games/
?? exercises/222_card_games/
?? exercises/224_chaitanas_colossal_coaster/
?? exercises/225_chaitanas_colossal_coaster/
?? exercises/227_making_the_grade/
?? exercises/228_making_the_grade/
```

Nothing else was written. No state-changing git commands were run.

## Concerns

- **Topics 216, 217, 219, 220, 223, 226, 229 are unused.** The exercises did not need three
  sub-drills each; the numbers are left free, as the `200 + 3k + i` scheme allows.
- **Deviation 2 (`letter_grades`) is the one place a reviewer should look.** `_reference`
  follows the instructions rather than the exemplar, and `_gen` avoids the values where the
  two disagree. If the project would rather mirror the exemplar bug-for-bug, the change is
  three lines in `228_making_the_grade/drill.py`.
- The `### General` section in `221`/`222`'s Exercism hints is empty because Exercism's
  `card-games/.docs/hints.md` has nothing under its `## General` heading. Kept for fidelity.
- `222_card_games`'s `average_even_is_average_odd` divides by zero on a one-card hand and
  `approx_average_is_average` is only meaningful for odd-length hands. Both are Exercism's
  stated preconditions; `_gen` only ever produces hands of 3, 5 or 7 cards, and `## You get`
  states the preconditions.
