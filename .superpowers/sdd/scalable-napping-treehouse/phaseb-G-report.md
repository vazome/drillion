# Phase B — batch G report (practice exercises, topics 320–329)

Ten new drill folders under `exercises/`, one per Exercism practice exercise. Nothing outside these
ten folders and this report was touched. No git state was changed.

## Drills

| folder | title | minutes | tags | prereqs |
| --- | --- | --- | --- | --- |
| `320_etl` | etl — reshape the score table from one-to-many to one-to-one | 10 | `exercism, dicts, data-structures` | `[236]` |
| `321_flatten_array` | flatten-array — unpack the nested boxes into one flat list | 10 | `exercism, core` | `[200, 209, 215, 221, 224, 227]` |
| `322_grains` | grains — doubling on every chessboard square | 10 | `exercism, numbers, core` | `[200, 206]` |
| `323_collatz_conjecture` | collatz-conjecture — count the steps down to 1 | 10 | `exercism, numbers, core` | `[200, 206]` |
| `324_triangle` | triangle — equilateral, isosceles or scalene | 10 | `exercism, bools, core` | `[200, 203, 206]` |
| `325_secret_handshake` | secret-handshake — turn a five-bit code into a list of actions | 10 | `exercism, list-methods, core` | `[200, 203, 206, 209, 215, 218, 221, 224, 227]` |
| `326_space_age` | space-age — your age in years on any planet | 10 | `exercism, dicts, data-structures` | `[200, 203, 206, 221, 224, 227, 236]` |
| `327_atbash_cipher` | atbash-cipher — mirror the alphabet, then cut into five-letter blocks | 15 | `exercism, string-methods, core` | `[200, 209, 215, 218, 221, 224, 227]` |
| `328_rotational_cipher` | rotational-cipher — ROT-n the letters, leave everything else alone | 10 | `exercism, strings, core` | `[200, 206, 209, 215]` |
| `329_scrabble_score` | scrabble-score — add up a word's letter values | 15 | `exercism, regular-expressions, files-text` | `[200, 215, 218, 221, 227, 236]` |

`minutes` from `config.json` difficulty (1→10, 2→15); `tags` = `exercism` + the slug's `practices`
(kebab-case) + the contract's section tag (`flatten-array` has no practices, so `core`);
`prereqs` = the slug's `prerequisites` mapped through the concept→topic table, unknowns dropped.

## Entry-point shapes

| folder | `solve` |
| --- | --- |
| `320_etl` | `solve(legacy_data)` → dict |
| `321_flatten_array` | `solve(iterable)` → list |
| `322_grains` | `solve()` → `{"square": fn, "total": fn}` |
| `323_collatz_conjecture` | `solve(number)` → int |
| `324_triangle` | `solve()` → `{"equilateral": fn, "isosceles": fn, "scalene": fn}` |
| `325_secret_handshake` | `solve(binary_str)` → list[str] |
| `326_space_age` | `solve()` → the `SpaceAge` **class** (ex_096 shape) |
| `327_atbash_cipher` | `solve()` → `{"encode": fn, "decode": fn}` |
| `328_rotational_cipher` | `solve(text, key)` → str |
| `329_scrabble_score` | `solve(word)` → int |

No exercise in this batch has more than 4 required functions, so none was split.

## Sources and deviations

- **`hints.md` does not exist for any of the ten slugs**, so no `## Exercism hints` section appears in
  any of these READMEs (per the contract, the section is skipped when the file is absent).
- **No `introduction.md`** for `triangle`, `atbash-cipher`, `rotational-cipher` → no `## Introduction`
  section in those three.
- Exercism `introduction.md` / `instructions.md` / `instructions.append.md` are reproduced verbatim
  (checked line by line by script — 0 missing lines). Transformations applied: `# Instructions` /
  `# Introduction` / `# Instructions append` headings dropped, `## X` → `### X`,
  `~~~~exercism/note` blocks → `> [!NOTE]` callouts (link-reference definitions inside a note kept on
  a `>` line so they still resolve). No line inside a fenced block was touched — in particular
  grains' `# when the square value is not in the acceptable range` comment inside its ```python
  fence stays a comment.
- **`323_collatz_conjecture`** — the exemplar halves with `/` (float division), which silently turns
  the running value into a float. `_reference` uses `//`, which is what the instructions describe
  ("divide it by 2" on integers) and gives identical step counts. The README says so explicitly.
- **`326_space_age`** — the exemplar hard-codes per-planet second counts derived from a *sidereal*
  Earth year (`31558149.76`). The instructions specify `365.25` days = `31557600` seconds and give
  the orbital periods as a table, so `_reference` implements the instructions
  (`round(seconds / (31557600 * period), 2)`). Verified: all eight canonical cases pass with these
  constants. The README states the exact expression, so a learner following the text matches the
  grader bit for bit.
- **`321_flatten_array`** — the exemplar flattens any non-string iterable. The canonical tests only
  ever pass lists, so `_reference` and `_gen` are restricted to lists (plus `None` and numbers), and
  the README says the input is a list. A learner's more general solution still passes.
- **`329_scrabble_score`** — the exemplar short-circuits with `if not word.isalpha(): return 0`,
  which is behaviour for input the instructions never define (and which would score `"at bat"` as 0).
  `_reference` is the plain table sum; `_gen` only produces letter-only words and the empty string,
  so the two never disagree on anything the grader asks. The README states the input contract.
- **`320_etl`** — added one assertion that `legacy_data` is not mutated (the README states it as a
  rule; Exercism's tests do not check it).
- **`324_triangle`** — Exercism's tests use `assertIs(..., True/False)`. The generated cases here
  compare with `is` too, and the README carries a `> [!WARNING]` that truthy is not enough.
- Exact error messages are asserted with `pytest.raises(..., match=r"^…$")`:
  `square must be between 1 and 64` (grains) and `Only positive integers are allowed` (collatz),
  both copied character for character from the Exercism test files.

## Verification

### `uv run ruff check` (this batch only)

```
$ uv run ruff check exercises/320_etl/drill.py exercises/321_flatten_array/drill.py \
    exercises/322_grains/drill.py exercises/323_collatz_conjecture/drill.py \
    exercises/324_triangle/drill.py exercises/325_secret_handshake/drill.py \
    exercises/326_space_age/drill.py exercises/327_atbash_cipher/drill.py \
    exercises/328_rotational_cipher/drill.py exercises/329_scrabble_score/drill.py
All checks passed!
```

### Stub run per drill — each fails with `NotImplementedError`

```
$ for d in 320_etl 321_flatten_array 322_grains 323_collatz_conjecture 324_triangle \
           325_secret_handshake 326_space_age 327_atbash_cipher 328_rotational_cipher \
           329_scrabble_score; do uv run pytest exercises/$d -q -p no:cacheprovider; done
exercises/320_etl/drill.py:2: NotImplementedError
FAILED exercises/320_etl/drill.py::test_solve - NotImplementedError
exercises/321_flatten_array/drill.py:2: NotImplementedError
FAILED exercises/321_flatten_array/drill.py::test_solve - NotImplementedError
exercises/322_grains/drill.py:2: NotImplementedError
FAILED exercises/322_grains/drill.py::test_solve - NotImplementedError
exercises/323_collatz_conjecture/drill.py:2: NotImplementedError
FAILED exercises/323_collatz_conjecture/drill.py::test_solve - NotImplemented...
exercises/324_triangle/drill.py:2: NotImplementedError
FAILED exercises/324_triangle/drill.py::test_solve - NotImplementedError
exercises/325_secret_handshake/drill.py:2: NotImplementedError
FAILED exercises/325_secret_handshake/drill.py::test_solve - NotImplementedError
exercises/326_space_age/drill.py:2: NotImplementedError
FAILED exercises/326_space_age/drill.py::test_solve - NotImplementedError
exercises/327_atbash_cipher/drill.py:2: NotImplementedError
FAILED exercises/327_atbash_cipher/drill.py::test_solve - NotImplementedError
exercises/328_rotational_cipher/drill.py:2: NotImplementedError
FAILED exercises/328_rotational_cipher/drill.py::test_solve - NotImplementedE...
exercises/329_scrabble_score/drill.py:2: NotImplementedError
FAILED exercises/329_scrabble_score/drill.py::test_solve - NotImplementedError
```

### Reference run — `solve = _reference`, `test_solve()` under `STUDY_SEED` 1, 2, 42

```
$ uv run python /tmp/refrun_G.py
seed  1  320_etl                  ok
seed  1  321_flatten_array        ok
seed  1  322_grains               ok
seed  1  323_collatz_conjecture   ok
seed  1  324_triangle             ok
seed  1  325_secret_handshake     ok
seed  1  326_space_age            ok
seed  1  327_atbash_cipher        ok
seed  1  328_rotational_cipher    ok
seed  1  329_scrabble_score       ok
seed  2  320_etl                  ok
seed  2  321_flatten_array        ok
seed  2  322_grains               ok
seed  2  323_collatz_conjecture   ok
seed  2  324_triangle             ok
seed  2  325_secret_handshake     ok
seed  2  326_space_age            ok
seed  2  327_atbash_cipher        ok
seed  2  328_rotational_cipher    ok
seed  2  329_scrabble_score       ok
seed 42  320_etl                  ok
seed 42  321_flatten_array        ok
seed 42  322_grains               ok
seed 42  323_collatz_conjecture   ok
seed 42  324_triangle             ok
seed 42  325_secret_handshake     ok
seed 42  326_space_age            ok
seed 42  327_atbash_cipher        ok
seed 42  328_rotational_cipher    ok
seed 42  329_scrabble_score       ok
failures: 0
```

Additionally stressed over `STUDY_SEED` 1–300 for all ten drills (3000 runs) to shake out generator
edge cases — `stress failures: 0`.

### `uv run study selfcheck`

```
$ uv run study selfcheck
155/155 ok
```

(153/153 when this batch was first checked in isolation; the count rose as sibling implementers
added their folders. All ten of this batch's slugs are in the ok set — `selfcheck` fails the whole
run otherwise.)

### Catalogue

```
$ uv run python -c "from study.catalogue import exercises; ..."
320_etl                  topic=320  minutes=10  hints=3 tags=['exercism', 'dicts', 'data-structures'] prereqs=[236]
321_flatten_array        topic=321  minutes=10  hints=3 tags=['exercism', 'core'] prereqs=[200, 209, 215, 221, 224, 227]
322_grains               topic=322  minutes=10  hints=3 tags=['exercism', 'numbers', 'core'] prereqs=[200, 206]
323_collatz_conjecture   topic=323  minutes=10  hints=3 tags=['exercism', 'numbers', 'core'] prereqs=[200, 206]
324_triangle             topic=324  minutes=10  hints=3 tags=['exercism', 'bools', 'core'] prereqs=[200, 203, 206]
325_secret_handshake     topic=325  minutes=10  hints=3 tags=['exercism', 'list-methods', 'core'] prereqs=[200, 203, 206, 209, 215, 218, 221, 224, 227]
326_space_age            topic=326  minutes=10  hints=3 tags=['exercism', 'dicts', 'data-structures'] prereqs=[200, 203, 206, 221, 224, 227, 236]
327_atbash_cipher        topic=327  minutes=15  hints=3 tags=['exercism', 'string-methods', 'core'] prereqs=[200, 209, 215, 218, 221, 224, 227]
328_rotational_cipher    topic=328  minutes=10  hints=3 tags=['exercism', 'strings', 'core'] prereqs=[200, 206, 209, 215]
329_scrabble_score       topic=329  minutes=15  hints=3 tags=['exercism', 'regular-expressions', 'files-text'] prereqs=[200, 215, 218, 221, 227, 236]
```

Every one parses, carries `source:`, has exactly 3 hints, and its `spec_md` contains
`## Why`, `## Instructions`, `## You get`, `## You return`, `## Rules`, `## Read first`.

### Format checks

- The `# ══ machinery …` marker line in all ten `drill.py` files is byte-identical to
  `exercises/303_bob/drill.py`'s.
- No module docstring, no docstring on `solve`; stub body is exactly `raise NotImplementedError`.
- All README fences balanced; no raw HTML (the three `<…>` sequences that a naive regex flags —
  `on_<planet name>`, `ROT + <key>` — are inside Exercism's own code spans).
- Batch-F lesson honoured: no heading demotion inside a fenced block; no Hint 2 contains the
  reference expression written with the drill's own parameter names (all ten Hint 2s are prose that
  names the tools, not the answer).

## Concerns

- `329_scrabble_score`'s section tag is `files-text`, because its only `practices` entry is
  `regular-expressions` and the contract map sends that to `files-text`. It is the map's answer, not
  a judgement call, but a scrabble scorer filed under "files & text" may read oddly in the catalogue.
  Flagging rather than overriding.
- `326_space_age` compares floats produced by `round(..., 2)`. Learner and reference perform the same
  single division and single `round`, so results are bit-identical; a learner who divides in two
  steps (`seconds / 31557600 / period`) could in principle land on the other side of a rounding
  boundary. The README pins the exact expression, and 3000 stress runs found no such case.

---

## Controller notes (added after review, 2026-08-26)

- **`329_scrabble_score` section tag**: the concern above was ruled on — the map's `files-text`
  answer was overridden to `core`. The drill file carries `tags: [exercism, regular-expressions,
  core]`. The table at the top of this report and the catalogue paste under Verification predate
  that override and are left as-written (they are the record of what was run).
- **Review outcome**: Needs fixes — one Important finding, `325_secret_handshake/README.md` Rules
  table gave the 4th-from-right character of `"10011"` as `1`, contradicting the drill's own
  `solve("10011") # -> ["double blink", "wink"]` example and the canonical Exercism case. Corrected
  to `0` by the controller. Review report: `phaseb-G-review.md`.
