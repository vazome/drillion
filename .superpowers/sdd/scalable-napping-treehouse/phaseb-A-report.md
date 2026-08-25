# Phase B — batch A report (concept exercises k=0..4, topics 200–214)

Worktree: `/home/daniel/study-exercism` (branch `exercism-drills`). 7 files written, nothing else
touched. All are multi-function drills: `solve()` takes no arguments and returns a dict of the
required functions; `_reference()` returns the same dict; `test_solve()` calls `solve()[name](...)`.

## Files

| file | topic | title | minutes | prereqs | tags |
|---|---|---|---|---|---|
| `exercises/ex_200_guidos_gorgeous_lasagna.py` | 200 | basics — Guido's lasagna kitchen timer | 12 | `[]` | `["exercism", "basics", "core"]` |
| `exercises/ex_203_ghost_gobble_arcade_game.py` | 203 | bools — the Pac-Man rulebook | 12 | `[200]` | `["exercism", "bools", "core"]` |
| `exercises/ex_206_currency_exchange.py` | 206 | numbers — the currency exchange desk | 12 | `[200]` | `["exercism", "numbers", "core"]` |
| `exercises/ex_207_currency_exchange.py` | 207 | numbers — whole bills, leftovers and the booth's cut | 15 | `[200, 206]` | `["exercism", "numbers", "core"]` |
| `exercises/ex_209_meltdown_mitigation.py` | 209 | conditionals — reactor meltdown control | 15 | `[200, 203]` | `["exercism", "conditionals", "core"]` |
| `exercises/ex_212_black_jack.py` | 212 | comparisons — blackjack card values | 15 | `[200, 203, 209]` | `["exercism", "comparisons", "core"]` |
| `exercises/ex_213_black_jack.py` | 213 | comparisons — blackjack hand decisions | 15 | `[200, 203, 209, 212]` | `["exercism", "comparisons", "core"]` |

Every source exercise has exactly one entry in its `concepts` list in
`/tmp/exercism-python/config.json`, so each tag list is `exercism` + that concept + the section tag
`core` (all five concepts map to `core` in the phase-B section map).

### Splits

- `guidos-gorgeous-lasagna` (3 functions + 1 constant), `ghost-gobble-arcade-game` (4 functions) and
  `meltdown-mitigation` (3 functions) are single drills — each is within the ≤ 4 functions rule.
- `currency-exchange` has 6 functions → split at the sub-concept seam.
  - 206 = plain arithmetic operators: `exchange_money`, `get_change`, `get_value_of_bills`.
  - 207 = floor division / modulo and the composite: `get_number_of_bills`,
    `get_leftover_of_bills`, `exchangeable_value`.
- `black-jack` has 6 functions → split.
  - 212 = scoring and ranking: `value_of_card`, `higher_card`, `value_of_ace`.
  - 213 = hand decisions: `is_blackjack`, `can_split_pairs`, `can_double_down`. `value_of_card` is
    supplied above `solve` under `# given — do not edit`, so 213 is about the comparison rules and
    not about re-typing 212's answer.

Both split pairs keep the `ex_<NNN>_<slug_underscored>.py` naming; the topic number keeps the two
filenames (and catalogue keys) distinct.

## Deviations from the Exercism sources

1. **`ex_200` returns a constant alongside functions.** Task 1 of the exercise is "define the
   `EXPECTED_BAKE_TIME` constant", which is the whole point of the `basics` concept. Dropping it
   would lose that. So the spec reads "YOU RETURN: a dict with these four entries" and the dict has
   `"EXPECTED_BAKE_TIME": 40` next to the three functions. Everything else follows the
   multi-function contract.
2. **`ex_200` drops Exercism task 5** ("add docstrings to your functions"). It cannot be graded by
   the drill runner in any useful way — a learner would have to docstring closures inside `solve`.
   The habit is instead demonstrated by the `# given` docstring in `ex_213`.
3. **`ex_209` `reactor_efficiency`: `>= 80` rather than the exemplar's `80 <= p <= 100`.** The
   exemplar returns `'black'` for anything over 100% efficiency, which contradicts its own
   instructions ("green -> efficiency of 80% or more"). The canonical tests never exceed 100%, so
   the bug is invisible there. `_reference` implements the instructions; `_gen` caps the generated
   efficiency at 99.5% so the two readings can never disagree on a generated case.
4. **`ex_206` `get_value_of_bills`: spec pins `denomination` to a whole number.** The exemplar
   returns `denomination * number_of_bills` while its own docstring example
   (`get_value_of_bills(15.13, 16) -> 242`) implies truncation. The canonical tests only use whole
   denominations. The spec therefore states the booth deals only in whole-number face values, which
   removes the ambiguity instead of inheriting it.
5. **`ex_207` `exchangeable_value` spread wording.** Restated as "a percentage OF THE RATE, added to
   it" with the 1.20/10% → 1.32 worked example from the instructions, because the original wording
   trips people into applying the spread to the budget.
6. **Canonical case counts.** These are multi-function drills, so "3–6 canonical cases" is applied
   per function (3–8 rows each, driven by a small `for` table copied out of the Exercism test file)
   rather than 3–6 for the whole file — 3 cases for a 4-band ladder would not pin the boundaries.
7. No exercise in this batch raises, so there are no `pytest.raises` assertions. `ex_206` and
   `ex_207` import `pytest` only for `pytest.approx` on float results.

`_gen` variety: `ex_209` and `ex_213` deliberately steer the random inputs into every outcome band
(LOW/NORMAL/DANGER, green/orange/red/black, and blackjack-capable hands) instead of relying on
chance, while staying clear of the exact band boundaries so float rounding can never make a correct
solution disagree with `_reference`.

## Verification (run from `/home/daniel/study-exercism`)

`uv run ruff check exercises/ex_200_... ex_203_... ex_206_... ex_207_... ex_209_... ex_212_... ex_213_...`

```
All checks passed!
```

Stub runs, `uv run pytest exercises/<file> -q -p no:cacheprovider`, last line each:

```
FAILED exercises/ex_200_guidos_gorgeous_lasagna.py::test_solve - NotImplement...
FAILED exercises/ex_203_ghost_gobble_arcade_game.py::test_solve - NotImplemen...
FAILED exercises/ex_206_currency_exchange.py::test_solve - NotImplementedError
FAILED exercises/ex_207_currency_exchange.py::test_solve - NotImplementedError
FAILED exercises/ex_209_meltdown_mitigation.py::test_solve - NotImplementedError
FAILED exercises/ex_212_black_jack.py::test_solve - NotImplementedError
FAILED exercises/ex_213_black_jack.py::test_solve - NotImplementedError
```

`uv run study.py selfcheck`:

```
104/104 ok
```

(104 = the pre-existing 87 drills + batch C's 10 practice drills that landed while this batch was
being written + these 7. No file failed.)

Also run, beyond the required set, because several drills compare floats:
`STUDY_SEED` 1..300 against all 7 files with `solve = _reference` →

```
seeds 1..300 ok
```

and the full `uv run study.py selfcheck` under `STUDY_SEED` 1, 2, 3, 5, 11, 42, 99, 12345 → `104/104
ok` each.

Catalogue check, `uv run python -c "import study; print(len(study.exercises()))"` →

```
104
```

with all seven slugs present:

```
ex_200_guidos_gorgeous_lasagna | 200 | basics — Guido's lasagna kitchen timer | ['exercism', 'basics', 'core'] | [] | 12
ex_203_ghost_gobble_arcade_game | 203 | bools — the Pac-Man rulebook | ['exercism', 'bools', 'core'] | [200] | 12
ex_206_currency_exchange | 206 | numbers — the currency exchange desk | ['exercism', 'numbers', 'core'] | [200] | 12
ex_207_currency_exchange | 207 | numbers — whole bills, leftovers and the booth's cut | ['exercism', 'numbers', 'core'] | [200, 206] | 15
ex_209_meltdown_mitigation | 209 | conditionals — reactor meltdown control | ['exercism', 'conditionals', 'core'] | [200, 203] | 15
ex_212_black_jack | 212 | comparisons — blackjack card values | ['exercism', 'comparisons', 'core'] | [200, 203, 209] | 15
ex_213_black_jack | 213 | comparisons — blackjack hand decisions | ['exercism', 'comparisons', 'core'] | [200, 203, 209, 212] | 15
```

`git status --short` shows only the seven new files; no existing file was modified. (One clean-up
note: a `study.py selfcheck` of mine was killed by a command timeout and left its `_selfcheck_ex_*.py`
temp files behind; I deleted them after confirming no selfcheck process was running. Nothing else in
the tree was touched.)

## Open concerns

1. **`# SOURCE:` before `# READ FIRST:` disables the READ FIRST panel — affects every Phase B batch,
   not just this one.** `study.read_first()` takes the first run of comment lines after the module
   docstring and returns `[]` unless that run's *first* line starts with `READ FIRST`. With the
   mandated ordering, the first line is the `SOURCE:` line, so `read_first` returns `[]` for all
   exercism drills. Confirmed empirically: all 17 exercism files currently in the worktree (my 7 and
   batch C's `ex_300`–`ex_309`) report 0 read-first lines, while their non-exercism neighbours that
   have a block report it fine. I followed the contract as written rather than deviating alone.
   The fix is one line in `study.py` — skip leading comment lines until one starts with
   `READ FIRST` — and belongs to the controller, applied once for all batches.
2. `ex_200`'s dict mixes a constant in with functions (deviation 1 above). If the reviewer wants
   strict "a dict with these functions", the fix is to drop the `EXPECTED_BAKE_TIME` entry and its
   paragraph, and delete the two lines in `test_solve` that assert it — but the drill then no longer
   teaches constants, which is a quarter of the `basics` concept.
3. `ex_207`'s `exchangeable_value` and `get_number_of_bills` are compared with `==` rather than
   `pytest.approx`, because both are specified to be whole numbers. A learner who leaves the result
   as a float (`amount // denomination` on a float gives a float) still passes, since `3 == 3.0`.
   That matches Exercism's own `assertEqual` behaviour; hint 2 mentions the type explicitly.
