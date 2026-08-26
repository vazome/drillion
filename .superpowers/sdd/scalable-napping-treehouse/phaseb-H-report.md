# Phase B — batch H report (practice 330–339)

Ten drills, all Exercism *practice* exercises, one `solve` entry point each.
`330`–`337` were written by a previous implementer that was killed before it could verify or
report; this pass audited them line by line and verified them. `338` and `339` are new.

## The ten drills

| slug | title | minutes | prereqs | tags | entry point |
| --- | --- | --- | --- | --- | --- |
| 330_pig_latin | pig-latin — translate English into a children's code | 15 | 200, 203, 209 | exercism, conditionals, core | `solve(text) -> str` |
| 331_protein_translation | protein-translation — decode an RNA strand until the stop signal | 15 | 200, 209, 215, 218, 221, 227 | exercism, core | `solve(strand) -> list[str]` |
| 332_transpose | transpose — turn the rows of a block of text into its columns | 15 | 200, 203, 206, 209, 215, 218, 221, 224, 227, 242 | exercism, unpacking-and-multiple-assignment, core | `solve(text) -> str` |
| 333_sublist | sublist — say how two lists relate to each other | 15 | 200, 203, 209, 212, 221 | exercism, comparisons, core | `solve(list_one, list_two)` → one of four given constants |
| 334_prime_factors | prime-factors — break a number into the primes it is built from | 15 | 200, 206, 209, 221, 224, 227 | exercism, core | `solve(value) -> list[int]` |
| 335_nth_prime | nth-prime — produce primes on demand and take the nth one | 15 | 200, 203, 206, 209, 212, 215, 221, 224, 227 | exercism, generators, data-structures | `solve(number) -> int`, raises `ValueError("there is no zeroth prime")` |
| 336_sieve | sieve — find every prime up to a limit by crossing out multiples | 20 | 200, 206, 209, 221, 224, 227, 245 | exercism, sets, data-structures | `solve(limit) -> list[int]` |
| 337_saddle_points | saddle-points — find the cells that win their row and lose their column | 20 | 200, 209, 221, 224, 227, 245 | exercism, loops, core | `solve(matrix) -> list[dict]`, raises `ValueError("irregular matrix")` |
| 338_clock | clock — a time-of-day class that wraps around midnight | 20 | 200, 206, 215, 248 | exercism, class-composition, rich-comparisons, string-formatting, core | `solve()` returns the **class** `Clock(hour, minute)` (ex_096 shape) |
| 339_high_scores | high-scores — a score list that answers three questions | 20 | 200, 221, 224, 248 | exercism, classes, core | `solve()` returns the **class** `HighScores(scores)` (ex_096 shape) |

Metadata rules applied: `minutes` from Exercism difficulty (d2 → 15, d3 → 20); `tags` =
`exercism` + the exercise's `practices` list from `config.json` + one section tag
(conditionals/comparisons/loops/classes/class-*/rich-comparisons/string-formatting/
unpacking-and-multiple-assignment → `core`; generators/sets → `data-structures`; no practices →
`core`); `prereqs` = the topic number of the first sub-drill for each Exercism prerequisite
concept (basics 200 · bools 203 · numbers 206 · conditionals 209 · comparisons 212 · strings 215 ·
string-methods 218 · lists 221 · list-methods 224 · loops 227 · unpacking 242 · sets 245 ·
classes 248). Every value in the table above was re-derived from
`/tmp/exercism-python/config.json` in this pass and matches.

`338` and `339` are the batch's two class exercises. Both follow `exercises/096_async_cm/` and the
sibling `exercises/326_space_age/`: `solve()` takes no arguments and returns the class itself,
`_reference()` returns an equivalent class, and `test_solve` asserts `inspect.isclass(...)` first.

## The two new drills

### 338_clock
- Sources: `.docs/instructions.md` + the long `.docs/instructions.append.md` (the `__repr__` /
  `__str__` essay), `.meta/example.py`, `clock_test.py`. No `introduction.md`, no `hints.md`, so
  `## Introduction` and `## Exercism hints` are correctly absent.
- **Deviation from `.meta/example.py` (deliberate):** the exemplar's `__add__`/`__sub__` mutate
  `self` and return `self`, and its `__eq__` compares `repr()` strings. The reference here returns
  a **new** `Clock` from `+`/`-` and compares the normalised `(hour, minute)` pair. The exemplar's
  mutating operators are a latent bug (`c + 3` silently changes `c`), and the common instructions
  say to implement the instructions rather than copy an exemplar that contradicts good practice.
  Because this strengthens the contract beyond Exercism's tests, the README states it twice — as a
  bullet under `## Rules` and as a `> [!WARNING]` — and `test_solve` checks it explicitly.
- Also written down in `## Rules` (things Exercism leaves open): `repr()` shows the **normalised**
  numbers unpadded (`Clock(72, 8640)` reprs as `Clock(0, 0)`), `str()` is zero-padded `HH:MM`.
  Both follow from the exemplar and from the canonical tests; neither is spelled out upstream.
- `_gen` mixes in-range hours, negative hours, hours far past 24, in-range minutes, minutes in the
  thousands either sign, and exact-hour multiples, then also exercises `+`/`-` with a random signed
  shift, a day-later equality and a minute-later inequality on every case.
- 6 canonical asserts copied from `clock_test.py` (repr, minute roll-over, negative hour+minute,
  add, subtract, hour-overflow equality).

### 339_high_scores
- Sources: `.docs/instructions.md` + `.docs/instructions.append.md`, `.meta/example.py`,
  `high_scores_test.py`. No `introduction.md`, no `hints.md`.
- `_reference` is the exemplar unchanged (it is already correct and non-mutating).
- The non-mutation requirement is the point of the drill and is the thing Exercism's tests check
  last, so it is a `> [!WARNING]` in the README and the generated loop calls
  `personal_top_three()` **before** asserting `.latest()` and `.scores`.
- `_gen` varies list length 1–12 and, one time in three, draws from a three-value pool so ties are
  everywhere (the `[40, 40, 30]` case); otherwise scores spread over 0–1000.
- 6 canonical asserts copied from `high_scores_test.py`, including the `.scores`-unchanged case.

## Audit of the inherited eight — what I found and changed

**Changed: nothing.** Every check below passed as written, so the eight files are exactly as the
previous implementer left them. What was checked:

- **Frontmatter** — all eight re-derived from `config.json` (difficulty → minutes, practices →
  tags, prerequisites → prereqs). All correct; see the table above.
- **Verbatim fidelity** — a script diffs each README's `## Introduction` / `## Instructions` /
  `## Exercism hints` against the Exercism source files, normalising only the sanctioned
  transformations (the source's own `# Introduction` / `# Instructions` / `# Instructions append`
  H1 dropped, `~~~~exercism/note` → `> [!NOTE]`, heading demotion, blank-line collapsing).
  **0 missing or changed lines** across all ten drills. `hints.md` does not exist for any of these
  ten exercises, so the absent `## Exercism hints` section is correct in all ten.
- **Batch F lesson** — no line inside a ```` ```python ```` fence was demoted into a heading; a
  fence-aware scan of all ten READMEs finds zero heading-shaped lines inside code fences.
- **Structure** — section order (`Why` → [`Introduction`] → `Instructions` → `You get` →
  `You return` → `Rules` → `Read first` → attribution → `Hints`), balanced fences, exactly one
  attribution line, exactly three `### Hint N`, nothing after Hint 3, no raw HTML.
- **Marker** — byte-identical to `exercises/303_bob/drill.py`'s in all ten; exactly one occurrence;
  no docstring in the learner region; stub body is `raise NotImplementedError`.
- **`_reference` correctness** — the strongest check in this pass: each drill's `_reference` was
  run against the **entire** Exercism canonical test file for its exercise (via a shim module, no
  drill code modified). 183 upstream tests, all passing — see the verification block.
- **README examples** — every `solve(...)  # -> …` example in the eight READMEs was evaluated
  against `_reference` (54 examples, all matching), and the two class drills' examples were checked
  by hand for the same reason.
- **`_gen` variety** — 200 draws per drill: 137–200 distinct inputs out of 200, with the error
  branches genuinely reached (335 raises on 30/200 draws, 337 on 17/200) and the empty/degenerate
  results reached (331 stop-first 11/200, 334 `solve(1)` 15/200, 336 limit<2 5/200,
  337 no-saddle-point 71/200). 333 produces all four verdicts in near-equal proportion
  (unequal 78, superlist 75, equal 65, sublist 82 in 300 draws); 330 reaches all 37 of its words.
- **Canonical cases** — each drill's canonical block was matched against the Exercism test file;
  every asserted case appears upstream with the same expected value (330: 9, 331: 7, 332: 7,
  333: 10, 334: 8, 335: 4 + the first-20 sequence + both error cases, 336: 5, 337: 8 + the error
  case). The two error-raising drills use `pytest.raises(ValueError, match=r"^…$")` with the exact
  upstream message.
- **Hints** — hint 1 nudges, hint 2 gives strategy, hint 3 works the same idea on different data
  inside a fence. No hint contains a literal answer for this drill's own graded data.

Two notes rather than defects (left as written):
- `333_sublist` hint 2 spells out the last window start as `len(big) - len(small) + 1`. That is the
  off-by-one the hint exists to head off, and `big`/`small` are not the drill's parameter names
  (`list_one`/`list_two`), so it stays inside the batch F rule; it is the one hint in the eight
  that comes closest to it.
- `337_saddle_points` hint 2 restates the `{"row": r + 1, "column": c + 1}` shape, but that shape
  is already fully specified in `## You return`, so it leaks nothing.

## Verification

All commands run from `/home/daniel/study`.

### ruff
```
$ uv run ruff check exercises/330_pig_latin/drill.py exercises/331_protein_translation/drill.py \
    exercises/332_transpose/drill.py exercises/333_sublist/drill.py \
    exercises/334_prime_factors/drill.py exercises/335_nth_prime/drill.py \
    exercises/336_sieve/drill.py exercises/337_saddle_points/drill.py \
    exercises/338_clock/drill.py exercises/339_high_scores/drill.py
All checks passed!
```

### stub run (must fail with NotImplementedError)
```
$ for s in 330_pig_latin … 339_high_scores; do uv run pytest exercises/$s -q -p no:cacheprovider; done
330_pig_latin            FAILED exercises/330_pig_latin/drill.py::test_solve - NotImplementedError 1 failed in 0.08s
331_protein_translation  FAILED exercises/331_protein_translation/drill.py::test_solve - NotImplemente... 1 failed in 0.06s
332_transpose            FAILED exercises/332_transpose/drill.py::test_solve - NotImplementedError 1 failed in 0.07s
333_sublist              FAILED exercises/333_sublist/drill.py::test_solve - NotImplementedError 1 failed in 0.07s
334_prime_factors        FAILED exercises/334_prime_factors/drill.py::test_solve - NotImplementedError 1 failed in 0.06s
335_nth_prime            FAILED exercises/335_nth_prime/drill.py::test_solve - NotImplementedError 1 failed in 0.06s
336_sieve                FAILED exercises/336_sieve/drill.py::test_solve - NotImplementedError 1 failed in 0.06s
337_saddle_points        FAILED exercises/337_saddle_points/drill.py::test_solve - NotImplementedError 1 failed in 0.07s
338_clock                FAILED exercises/338_clock/drill.py::test_solve - NotImplementedError 1 failed in 0.07s
339_high_scores          FAILED exercises/339_high_scores/drill.py::test_solve - NotImplementedError 1 failed in 0.06s
```

### reference run — `solve = _reference`, `test_solve()` at STUDY_SEED 1, 2, 42
```
seed 1 330_pig_latin OK            seed 2 330_pig_latin OK            seed 42 330_pig_latin OK
seed 1 331_protein_translation OK  seed 2 331_protein_translation OK  seed 42 331_protein_translation OK
seed 1 332_transpose OK            seed 2 332_transpose OK            seed 42 332_transpose OK
seed 1 333_sublist OK              seed 2 333_sublist OK              seed 42 333_sublist OK
seed 1 334_prime_factors OK        seed 2 334_prime_factors OK        seed 42 334_prime_factors OK
seed 1 335_nth_prime OK            seed 2 335_nth_prime OK            seed 42 335_nth_prime OK
seed 1 336_sieve OK                seed 2 336_sieve OK                seed 42 336_sieve OK
seed 1 337_saddle_points OK        seed 2 337_saddle_points OK        seed 42 337_saddle_points OK
seed 1 338_clock OK                seed 2 338_clock OK                seed 42 338_clock OK
seed 1 339_high_scores OK          seed 2 339_high_scores OK          seed 42 339_high_scores OK
(0.37s wall for all thirty runs)
```

### each `_reference` against the full Exercism canonical suite
```
330_pig_latin: 23 passed in 0.04s
331_protein_translation: 26 passed in 0.04s
332_transpose: 12 passed in 0.02s
333_sublist: 22 passed in 0.53s
334_prime_factors: 12 passed in 0.02s
335_nth_prime: 6 passed in 0.06s
336_sieve: 5 passed in 0.01s
337_saddle_points: 10 passed in 0.02s
338_clock: 55 passed in 0.05s
339_high_scores: 12 passed in 0.02s
```

### verbatim fidelity of the Exercism sections
```
330_pig_latin  <-  pig-latin            Introduction: OK (5 lines)   Instructions: OK (27 lines)   hints: absent (no source) OK
331_protein_translation                 Introduction: absent OK      Instructions: OK (27 lines)   hints: absent OK
332_transpose                           Introduction: absent OK      Instructions: OK (42 lines)   hints: absent OK
333_sublist                             Introduction: absent OK      Instructions: OK (19 lines)   hints: absent OK
334_prime_factors                       Introduction: absent OK      Instructions: OK (25 lines)   hints: absent OK
335_nth_prime                           Introduction: absent OK      Instructions: OK (11 lines)   hints: absent OK
336_sieve                               Introduction: OK (4 lines)   Instructions: OK (68 lines)   hints: absent OK
337_saddle_points                       Introduction: OK (6 lines)   Instructions: OK (26 lines)   hints: absent OK
338_clock                               Introduction: absent OK      Instructions: OK (64 lines)   hints: absent OK
339_high_scores                         Introduction: absent OK      Instructions: OK (9 lines)    hints: absent OK
ALL OK
```

### README examples evaluated against `_reference`
```
330_pig_latin: 7   331_protein_translation: 6   332_transpose: 6   333_sublist: 8
334_prime_factors: 7   335_nth_prime: 7   336_sieve: 6   337_saddle_points: 7
EXAMPLES OK          (338/339 use the `Clock = solve()` form and were evaluated separately: all match)
```

### selfcheck
```
$ uv run study selfcheck
161/161 ok
```

### catalogue
```
330_pig_latin            topic=330 minutes=15 hints=3 prereqs=[200, 203, 209] tags=['exercism', 'conditionals', 'core']
331_protein_translation  topic=331 minutes=15 hints=3 prereqs=[200, 209, 215, 218, 221, 227] tags=['exercism', 'core']
332_transpose            topic=332 minutes=15 hints=3 prereqs=[200, 203, 206, 209, 215, 218, 221, 224, 227, 242] tags=['exercism', 'unpacking-and-multiple-assignment', 'core']
333_sublist              topic=333 minutes=15 hints=3 prereqs=[200, 203, 209, 212, 221] tags=['exercism', 'comparisons', 'core']
334_prime_factors        topic=334 minutes=15 hints=3 prereqs=[200, 206, 209, 221, 224, 227] tags=['exercism', 'core']
335_nth_prime            topic=335 minutes=15 hints=3 prereqs=[200, 203, 206, 209, 212, 215, 221, 224, 227] tags=['exercism', 'generators', 'data-structures']
336_sieve                topic=336 minutes=20 hints=3 prereqs=[200, 206, 209, 221, 224, 227, 245] tags=['exercism', 'sets', 'data-structures']
337_saddle_points        topic=337 minutes=20 hints=3 prereqs=[200, 209, 221, 224, 227, 245] tags=['exercism', 'loops', 'core']
338_clock                topic=338 minutes=20 hints=3 prereqs=[200, 206, 215, 248] tags=['exercism', 'class-composition', 'rich-comparisons', 'string-formatting', 'core']
339_high_scores          topic=339 minutes=20 hints=3 prereqs=[200, 221, 224, 248] tags=['exercism', 'classes', 'core']
catalogue: 161 drills, all 10 present with 3 hints each
```
(161 rather than 159 because two sibling batches landed folders while this batch ran; the ten
above are all in the ok set.)

## Concerns

1. **`338_clock` asks for slightly more than Exercism does.** `+`/`-` must return a new `Clock` and
   leave the receiver alone. Exercism's own tests never notice the difference, and its exemplar
   fails this requirement. It is stated in `## Rules` and in a `> [!WARNING]`, so it is not a
   gotcha — but a reviewer who wants strict Exercism parity should drop the second `> [!WARNING]`
   and the `"+ and - must not change …"` assert in `test_solve` together.
2. **`335_nth_prime` grades `solve(10001)`.** That is Exercism's own `test_big_prime`, and the
   reference answers it in well under a second, but a learner's naive `all(n % d for d in
   range(2, n))` primality test will time out rather than fail cleanly. The README warns about
   effort in `## You get` and hint 2 points at the square-root bound; worth a glance if the runner
   has a tight per-drill timeout.
3. **`336_sieve` canonical block is long** — the full list of primes below 1000, ~15 lines of
   literal. It is copied from the Exercism test file and is correct; it is only visually heavy if
   a learner opens the machinery.
4. Nothing in the inherited eight needed a fix, which is a claim worth spot-checking: the evidence
   is the canonical-suite run (116 upstream tests against the eight `_reference`s; 183 across all ten) plus the
   0-changed-lines verbatim diff, both reproducible from the scripts described above.
