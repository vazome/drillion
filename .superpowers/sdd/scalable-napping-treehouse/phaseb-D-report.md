# Phase B — batch D report (concept exercises k=15..19, topics 245–259)

10 drill folders written under `exercises/`. Nothing else touched.

## Drills

| slug | topic | title | minutes | tags | prereqs | covers |
| --- | --- | --- | --- | --- | --- | --- |
| `245_cater_waiter` | 245 | sets — dedupe the recipes, build the shopping list | 14 | `exercism, sets, data-structures` | 200, 221, 227, 233, 236 | cater-waiter tasks 1, 5, 6 |
| `246_cater_waiter` | 246 | sets — spot the alcohol, tag the allergens | 14 | `exercism, sets, data-structures` | 200, 221, 227, 233, 236, 245 | tasks 2, 4 |
| `247_cater_waiter` | 247 | sets — sort dishes into diets, find the singleton ingredients | 15 | `exercism, sets, data-structures` | 200, 221, 227, 233, 236, 246 | tasks 3, 7 |
| `248_ellens_alien_game` | 248 | classes — Ellen's alien, its own health and its own position | 15 | `exercism, classes, core` | 200, 203, 206, 212, 215, 221, 227, 233, 236, 245 | ellens-alien-game tasks 1–6 |
| `249_ellens_alien_game` | 249 | classes — spawn a wave of aliens from a list of positions | 12 | `exercism, classes, core` | …, 245, 248 | task 7 |
| `251_plane_tickets` | 251 | generators — seat every passenger on the plane | 15 | `exercism, generators, data-structures` | 209, 221, 227, 236, 248 | plane-tickets tasks 1–4 |
| `254_log_levels` | 254 | enums — name the six log levels once | 15 | `exercism, enums, data-structures` | 209, 218, 227, 233, 248 | log-levels tasks 1–5 |
| `257_restaurant_rozalynn` | 257 | none — lay the dining room out with empty seats | 13 | `exercism, none, core` | 203, 209, 224, 227, 239 | restaurant-rozalynn tasks 1, 2 |
| `258_restaurant_rozalynn` | 258 | none — find the empty seats and count them | 12 | `exercism, none, core` | …, 239, 257 | tasks 3, 4 |
| `259_restaurant_rozalynn` | 259 | none — seat the walk-ins, clear the tables | 13 | `exercism, none, core` | …, 239, 258 | tasks 5, 6 |

Entry points: `solve()` returns a dict of functions everywhere except `248` (returns the `Alien`
class, per ex_096) and `249` (single function, so `solve(positions)` *is*
`new_aliens_collection`). Unused topic numbers in the allotted ranges: 250, 252, 253, 255, 256 —
those exercises needed fewer sub-drills than the range allowed.

## Splits and why

- **cater-waiter (7 functions → 3 drills), grouped by set operation, not by task order.**
  245 = construction / union / difference (tasks 1, 5, 6) and needs no reference data at all;
  246 = `isdisjoint` / `&` against two reference lists (tasks 2, 4); 247 = subset `<=` and
  symmetric difference `^` (tasks 3, 7), the two whose reference data arrives as an argument.
  Contiguous grouping would have put `categorize_dish` (five 25-line category constants) in the
  same learner region as `tag_special_ingredients`.
- **ellens-alien-game (class + 1 function → 2 drills).** 248 is the class (instance vs class
  attributes, tasks 1–6); 249 is the standalone factory with the finished `Alien` given as
  `# given — do not edit`.
- **restaurant-rozalynn (6 functions → 3 drills)** by what `None` is doing: placeholder + default
  argument (1–2), `is None` as a read test (3–4), writing `None` back / all-or-nothing update (5–6).

## Deviations from the Exercism sources (all deliberate)

1. **`categorize_dish` signature.** Exercism imports `VEGAN`/`VEGETARIAN`/`KETO`/`PALEO`/`OMNIVORE`
   from `sets_categories_data.py`; here the function takes a third argument,
   `categories` — a tuple of `(name, ingredient_set)` pairs already in the order to try. Documented
   in the README's `## You get` note. Exercism's *real* `VEGAN` and `OMNIVORE` sets are embedded in
   247's machinery (below the marker, invisible to the learner) so the two canonical examples from
   `instructions.md` are graded against the genuine data.
2. **`singleton_ingredients` second parameter** is described as `overlapping` ("ingredients that
   appear in more than one dish"), which is exactly what Exercism's `<CATEGORY>_INTERSECTIONS`
   constants hold. Semantics unchanged; `_reference` uses the exemplar's `^` fold minus that set.
3. **`ALCOHOLS` / `SPECIAL_INGREDIENTS`** (246) are `# given — do not edit` module constants in the
   learner region instead of an import — same values, verbatim from `sets_categories_data.py`.
4. **plane-tickets `generate_seats` — exemplar bug, instructions implemented.** The exemplar does
   `number = number + 4 if number >= 13 else number` and then skips row 13 inside the loop. For
   `13 <= number < 48` no row 13 is ever reached, so it yields `number + 4` seats (e.g. 17 for an
   asked-for 13). `_reference` yields exactly `number` seats and steps row 12 → 14. Exercism's own
   tests only cover 1–5 and 56, all of which agree with both versions, so every canonical case is
   still asserted unchanged. The README states the rule explicitly ("asking for `number` seats
   gives exactly `number` seats").
5. **restaurant-rozalynn `arrange_reservations` — exemplar bug, instructions implemented.** The
   exemplar loops `for seat_number in range(1, len(guests)): seats[seat_number] = guests[seat_number]`,
   which drops the first guest and seats the rest one place early; `none_test.py` encodes that
   result (`{1: 'Frank', ...}`) while `instructions.md` documents `{1: 'Walter', ...}`. `_reference`
   follows the instructions, the canonical assertion uses the instructions' output, and 257's README
   carries a `> [!NOTE]` telling the learner about the disagreement so the verbatim Instructions
   section does not read as contradicting the grader.
6. **log-levels `LogLevelInt` is not required.** Exercism's test file imports it, but its own hints
   say "another enum or any other solution"; the drill grades `LogLevel` plus the four functions and
   lets the code mapping be a dict, a second enum or `if`s. The README pins down the two things the
   Exercism tests decide but the prose does not: member names are UPPER CASE (`LogLevel.INFO`, while
   `instructions.md` writes `LogLevel.Info`) and `UNKNOWN = "UKN"`.
7. **cater-waiter canonical cases come from `instructions.md` and `.docs/introduction.md`**, not from
   `sets_test.py`: that test file only zips over a separate 458-line `sets_test_data.py` fixture.
   Each canonical assertion is a literal example printed in Exercism's own text (Punjabi-Style Chole,
   the three-dish master list, the appetizer list, the two drinks, the two allergen dishes, the two
   categorised dishes, and both symmetric-difference examples). The `example_dishes` /
   `EXAMPLE_INTERSECTION` results were recomputed and asserted to match Exercism's printed answers
   before being embedded.
8. **`# noqa: PIE796`** on `WARN = "WRN"` in 254's `_reference` — the duplicate value is the alias
   the exercise is about, and this repo's ruff configuration flags it.
9. **`hit()` ambiguity kept.** Exercism accepts both "health may go negative" and "clamp at zero";
   248's grader accepts either and only insists `is_alive()` agrees with whichever was chosen —
   same as `classes_test.py`.
10. Headings from `introduction.md` / `instructions.md` / `hints.md` are demoted one level and
    `~~~~exercism/note` blocks become `> [!NOTE]` callouts; `<br>` lines dropped. Everything else is
    verbatim, including Exercism's reference-link definitions.

## Verification

`uv run ruff check` over all ten drills:

```
All checks passed!
```

Stub run — every drill fails with `NotImplementedError`:

```
$ uv run pytest exercises/245_cater_waiter … exercises/259_restaurant_rozalynn -q -p no:cacheprovider
FAILED exercises/245_cater_waiter/drill.py::test_solve - NotImplementedError
FAILED exercises/246_cater_waiter/drill.py::test_solve - NotImplementedError
FAILED exercises/247_cater_waiter/drill.py::test_solve - NotImplementedError
FAILED exercises/248_ellens_alien_game/drill.py::test_solve - NotImplementedE...
FAILED exercises/249_ellens_alien_game/drill.py::test_solve - NotImplementedE...
FAILED exercises/251_plane_tickets/drill.py::test_solve - NotImplementedError
FAILED exercises/254_log_levels/drill.py::test_solve - NotImplementedError
FAILED exercises/257_restaurant_rozalynn/drill.py::test_solve - NotImplemente...
FAILED exercises/258_restaurant_rozalynn/drill.py::test_solve - NotImplemente...
FAILED exercises/259_restaurant_rozalynn/drill.py::test_solve - NotImplemente...
10 failed in 0.12s
```

Reference run (`solve = _reference`, `STUDY_SEED` 1 / 2 / 42, 30 runs):

```
245_cater_waiter  STUDY_SEED=1  test_solve() PASSED
245_cater_waiter  STUDY_SEED=2  test_solve() PASSED
245_cater_waiter  STUDY_SEED=42  test_solve() PASSED
246_cater_waiter  STUDY_SEED=1  test_solve() PASSED
246_cater_waiter  STUDY_SEED=2  test_solve() PASSED
246_cater_waiter  STUDY_SEED=42  test_solve() PASSED
247_cater_waiter  STUDY_SEED=1  test_solve() PASSED
247_cater_waiter  STUDY_SEED=2  test_solve() PASSED
247_cater_waiter  STUDY_SEED=42  test_solve() PASSED
248_ellens_alien_game  STUDY_SEED=1  test_solve() PASSED
248_ellens_alien_game  STUDY_SEED=2  test_solve() PASSED
248_ellens_alien_game  STUDY_SEED=42  test_solve() PASSED
249_ellens_alien_game  STUDY_SEED=1  test_solve() PASSED
249_ellens_alien_game  STUDY_SEED=2  test_solve() PASSED
249_ellens_alien_game  STUDY_SEED=42  test_solve() PASSED
251_plane_tickets  STUDY_SEED=1  test_solve() PASSED
251_plane_tickets  STUDY_SEED=2  test_solve() PASSED
251_plane_tickets  STUDY_SEED=42  test_solve() PASSED
254_log_levels  STUDY_SEED=1  test_solve() PASSED
254_log_levels  STUDY_SEED=2  test_solve() PASSED
254_log_levels  STUDY_SEED=42  test_solve() PASSED
257_restaurant_rozalynn  STUDY_SEED=1  test_solve() PASSED
257_restaurant_rozalynn  STUDY_SEED=2  test_solve() PASSED
257_restaurant_rozalynn  STUDY_SEED=42  test_solve() PASSED
258_restaurant_rozalynn  STUDY_SEED=1  test_solve() PASSED
258_restaurant_rozalynn  STUDY_SEED=2  test_solve() PASSED
258_restaurant_rozalynn  STUDY_SEED=42  test_solve() PASSED
259_restaurant_rozalynn  STUDY_SEED=1  test_solve() PASSED
259_restaurant_rozalynn  STUDY_SEED=2  test_solve() PASSED
259_restaurant_rozalynn  STUDY_SEED=42  test_solve() PASSED
```

Selfcheck (all batches present on disk at the time of the run):

```
$ uv run study selfcheck
157/157 ok
```

Catalogue:

```
$ uv run python -c "from study.catalogue import exercises; …"
245_cater_waiter           topic=245 minutes=14 hints=3 tags=['exercism', 'sets', 'data-structures'] prereqs=[200, 221, 227, 233, 236] sections_ok=True
246_cater_waiter           topic=246 minutes=14 hints=3 tags=['exercism', 'sets', 'data-structures'] prereqs=[200, 221, 227, 233, 236, 245] sections_ok=True
247_cater_waiter           topic=247 minutes=15 hints=3 tags=['exercism', 'sets', 'data-structures'] prereqs=[200, 221, 227, 233, 236, 246] sections_ok=True
248_ellens_alien_game      topic=248 minutes=15 hints=3 tags=['exercism', 'classes', 'core'] prereqs=[200, 203, 206, 212, 215, 221, 227, 233, 236, 245] sections_ok=True
249_ellens_alien_game      topic=249 minutes=12 hints=3 tags=['exercism', 'classes', 'core'] prereqs=[200, 203, 206, 212, 215, 221, 227, 233, 236, 245, 248] sections_ok=True
251_plane_tickets          topic=251 minutes=15 hints=3 tags=['exercism', 'generators', 'data-structures'] prereqs=[209, 221, 227, 236, 248] sections_ok=True
254_log_levels             topic=254 minutes=15 hints=3 tags=['exercism', 'enums', 'data-structures'] prereqs=[209, 218, 227, 233, 248] sections_ok=True
257_restaurant_rozalynn    topic=257 minutes=13 hints=3 tags=['exercism', 'none', 'core'] prereqs=[203, 209, 224, 227, 239] sections_ok=True
258_restaurant_rozalynn    topic=258 minutes=12 hints=3 tags=['exercism', 'none', 'core'] prereqs=[203, 209, 224, 227, 239, 257] sections_ok=True
259_restaurant_rozalynn    topic=259 minutes=13 hints=3 tags=['exercism', 'none', 'core'] prereqs=[203, 209, 224, 227, 239, 258] sections_ok=True
total in catalogue: 157
```

(`sections_ok` = `## Why`, `## You get`, `## You return`, `## Rules` and `## Read first` all present
in `spec_md`.) A separate structural pass confirmed for all ten READMEs: balanced code fences
(counting inside blockquotes), no raw HTML outside code spans, section order
`Why · Introduction · Instructions · You get · You return · Rules · Exercism hints · Read first · Hints`,
exactly one `## Hints` block with `### Hint 1..3` and nothing after Hint 3, one attribution line.
The `# ══ machinery …` marker in all ten `drill.py` files is byte-identical to `303_bob/drill.py`'s.

## Concerns

- **Two Exercism exemplars are wrong** (deviations 4 and 5). Both are implemented per the
  instructions, and in the restaurant case that means one of Exercism's own canonical test
  expectations is deliberately *not* ported. A reviewer should agree with that call before merge.
- **`categorize_dish` no longer has Exercism's signature** (deviation 1). It is the only signature
  change in the batch, and it is the price of not putting ~120 lines of ingredient constants in the
  learner's editor pane.
- `249_ellens_alien_game` is the thinnest drill in the batch (task 7 is three lines). It earns its
  place on tuple-unpacking-into-a-constructor and on "a list, not a generator", but it is closer to
  10 minutes than 12.

---

## Controller notes (added after review, 2026-08-26)

Review verdict: Needs fixes → all fixed by the controller. Review report: `phaseb-D-review.md`.

- **All three concerns above were ruled in this report's favour**, each re-verified against the
  sources: the `categorize_dish` signature trade is right and documented; the plane-tickets and
  restaurant-rozalynn exemplar bugs are real, and following the instructions is correct in both.
- **I-1 (Important, fixed)**: `### Hint 2` handed over the literal solution in `249`, `258` and
  `259` — in 249's case a fence containing the whole of the drill's only function, in the drill's own
  parameter name, leaving nothing for Hint 3. Same defect at lower intensity in `247`, `251`, `254`.
  All six rewritten to name the routing, the operator and the builtin without spelling the working
  expression. This is the batch F rule ("Hint 2 must not contain the reference body written with the
  drill's own parameter names") applied to concept drills; precedent commit `af68f83`.
- **m-1 (fixed)**: two `## Read first` anchors used `library/enum.html#using-auto` and
  `#functional-api`; both fragments live on `howto/enum.html`. The `library/enum.html` link inside the
  verbatim Exercism section is untouched — it is Exercism's, and it is correct.
- **m-2 (fixed)**: the towardsdatascience set-problems link 404s. Inherited verbatim from Exercism's
  `concepts/sets/links.json`, so the implementer followed the contract — but it sits in *our*
  `## Read first`, where a dead link reads as ours. Dropped.
- **m-3 (no change; recorded here as the deviation list missed it)**: Exercism's
  `cater-waiter/.docs/introduction.md:342` is `# Set Symmetric Difference`, a level-1 heading where
  every sibling is `##` — an upstream typo. All three cater-waiter READMEs demote it **two** levels,
  not the one the rule specifies. That is the right call: one level would have produced a top-level
  `## Set Symmetric Difference` and broken the section contract. Standing ruling for later batches:
  when an upstream heading level is itself anomalous, demote to the level its siblings land on.
- **m-4 (no change; known ceiling)**: runs of two blank lines in the Exercism sources render as one
  in the READMEs (21 places in the cater-waiter Introduction, 10 in restaurant-rozalynn, 7 in
  plane-tickets, 3 in ellens-alien-game). Rendering-neutral in GFM and consistent across the batch,
  but "line for line" is the stated bar and this is the only systematic departure from it. Trailing
  whitespace inside fences *is* preserved.
- **m-5 (fixed)**: `## Rules` never said `WARNING` must be declared before `WARN`. A learner
  declaring them the other way round still passes `get_warn_alias()` (both names resolve to the same
  object) but fails the messageless canonical `get_members()` assertion. One clause added.
