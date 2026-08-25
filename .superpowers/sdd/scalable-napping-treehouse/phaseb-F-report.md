# Phase B — batch F report (practice exercises, topics 310–319)

Ten drill folders under `exercises/`, one Exercism practice exercise each, in the folder format
(`README.md` + `drill.py`). Nothing outside these ten folders and this report was touched; no git
state was changed.

## Drills

| folder | title | minutes | tags | prereqs |
| --- | --- | --- | --- | --- |
| `310_word_count` | word-count — tally the words in a subtitle | 15 | `exercism, dicts, data-structures` | `[200, 215, 218, 227, 236]` |
| `311_acronym` | acronym — squeeze a long name down to its initials | 15 | `exercism, regular-expressions, files-text` | `[200, 215, 218, 227]` |
| `312_run_length_encoding` | run-length-encoding — compress runs, and put them back | 15 | `exercism, iteration, regular-expressions, data-structures` | `[200, 203, 206, 209, 215, 218, 221, 224, 227]` |
| `313_roman_numerals` | roman-numerals — write a number the way Rome would | 15 | `exercism, tuples, core` | `[200, 206, 209, 215, 218, 221, 224, 227, 233]` |
| `314_luhn` | luhn — the checksum that catches a mistyped card number | 15 | `exercism, classes, core` | `[200, 203, 206, 209, 215, 218, 221, 224, 227, 248]` |
| `315_isbn_verifier` | isbn-verifier — is this book number real, or a typo? | 10 | `exercism, strings, core` | `[200, 203, 209, 215]` |
| `316_phone_number` | phone-number — clean a NANP number or say exactly why you cannot | 15 | `exercism, raising-and-handling-errors, string-formatting, errors` | `[200, 206, 215, 218, 221, 227, 248]` |
| `317_matching_brackets` | matching-brackets — are the brackets balanced and nested right? | 15 | `exercism, conditionals, core` | `[200, 203, 209, 215, 221, 224, 227]` |
| `318_series` | series — every window of n digits, in order | 15 | `exercism, sequences, data-structures` | `[200, 206, 209, 215, 221, 227]` |
| `319_sum_of_multiples` | sum-of-multiples — award energy points for a finished level | 10 | `exercism, sets, data-structures` | `[200, 206, 209, 221, 227, 245]` |

`minutes` from `/tmp/exercism-python/config.json` difficulty (d1→10, d2→15); every one of these is d2
except `isbn-verifier` and `sum-of-multiples` (d1). Tags = `exercism` + the slug's `practices` list
kebab-case + one section tag. `prereqs` = the slug's `prerequisites` mapped through the
concept→topic table; every prerequisite in this batch mapped (nothing was dropped).

## Entry points

| folder | `solve` |
| --- | --- |
| 310 | `solve(subtitle)` → `dict` |
| 311 | `solve(phrase)` → `str` |
| 312 | `solve()` → `{"encode": fn, "decode": fn}` (two required functions) |
| 313 | `solve(number)` → `str` |
| 314 | `solve()` → the `Luhn` class (`Luhn(card_num).valid()`) |
| 315 | `solve(isbn)` → `bool` |
| 316 | `solve()` → the `PhoneNumber` class (`.number`, `.area_code`, `.pretty()`) |
| 317 | `solve(text)` → `bool` |
| 318 | `solve(series, length)` → `list[str]`, raises `ValueError` |
| 319 | `solve(level, base_values)` → `int` |

## Source handling / deviations

- Exercism `introduction.md`, `instructions.md`, `instructions.append.md` and `hints.md` were
  spliced into the READMEs by script (`/tmp/phasebF/splice.py`), not retyped, so the text is
  verbatim. Transformations applied: the file's own top-level `#` title dropped, remaining headings
  demoted one level (`##`→`###`, `###`→`####`; a mid-file `#` becomes `###`), `~~~~exercism/note`
  blocks turned into `> [!NOTE]` callouts.
- Only `word-count` has a `hints.md`; it is reproduced verbatim under `## Exercism hints`. Only
  `word-count`, `roman-numerals`, `luhn`, `matching-brackets`, `phone-number` and
  `sum-of-multiples` have an `introduction.md`; the other four READMEs have no `## Introduction`.
- `roman-numerals/.docs/instructions.md` is titled `# Introduction` upstream (Exercism's own
  mislabelling). The title line was dropped like any other file title; the body sits under
  `## Instructions`.
- **acronym**: the exemplar uses the regex `[A-Z]+['a-z]*|['a-z]+`, which returns `'` as the initial
  for a word that *starts* with an apostrophe (`'Twas` → `'`). `_reference` implements the
  instructions instead — hyphens are separators, every other punctuation mark is removed, and an
  apostrophe is deleted so `Halley's` stays one word. The two agree on all nine canonical cases;
  they differ only on leading apostrophes, which `_gen` does not produce.
- **phone-number**: the exemplar strips `[() +-.]`, which as a regex character class is a range
  covering `+ , - .` and therefore also removes commas. `_reference` uses an explicit set of
  formatting characters (`(`, `)`, `+`, `-`, `.` and whitespace); a comma is treated as punctuation
  and raises `punctuations not permitted`. All twenty canonical cases pass either way. The
  exemplar's `return None` fall-through (a valid-length number that somehow passes every guard)
  is unreachable and was not reproduced. The check *order* is the exemplar's, because the tests
  depend on it (`"523-abc-7890"` is too short *and* has letters, and must say `letters not
  permitted`).
- **word-count**: `_reference` returns a plain `dict`; a `Counter` from the learner compares equal
  and is accepted (stated in `## You return`).
- **sum-of-multiples**: canonical case copied verbatim as `solve(4, [3, 0])` even though the
  track's `instructions.append.md` promises sorted factors; `_gen` produces sorted, unique lists.
- Error-raising drills (316, 318) assert canonical failures with
  `pytest.raises(ValueError, match=r"^<exact message>$")`; the messages are the ones in the
  Exercism test files.
- `_gen` variety: 310 random subtitle lines built from a word pool and 14 different separator
  styles with random casing; 311 random phrases with space/hyphen/comma/underscore joins;
  312 random run structures including the empty string; 313 random 1–3999 plus a pool of the
  awkward values (4, 9, 40, 90, 400, 900, 3999); 314 random lengths 1–20, ~45% repaired to a valid
  checksum, random spaces, occasional injected letter/symbol; 315 random 9-digit bodies with a
  correct or wrong check character, random dashes, wrong lengths, injected letters; 316 random
  NANP numbers with random formatting, plus bad area/exchange codes, wrong lengths, letters and
  punctuation; 317 recursively generated balanced strings with filler, then mutated; 318 random
  digit strings with valid and all four invalid `length` values; 319 random levels 0–3000 and
  sorted unique base-value lists, sometimes empty, sometimes containing `0`.

## Verification

`uv run ruff check` on the ten `drill.py` files:

```
All checks passed!
```

Stub run per drill (`uv run pytest exercises/<slug> -q -p no:cacheprovider`) — all ten fail with
`NotImplementedError`:

```
FAILED exercises/310_word_count/drill.py::test_solve - NotImplementedError
FAILED exercises/311_acronym/drill.py::test_solve - NotImplementedError
FAILED exercises/312_run_length_encoding/drill.py::test_solve - NotImplemente...
FAILED exercises/313_roman_numerals/drill.py::test_solve - NotImplementedError
FAILED exercises/314_luhn/drill.py::test_solve - NotImplementedError
FAILED exercises/315_isbn_verifier/drill.py::test_solve - NotImplementedError
FAILED exercises/316_phone_number/drill.py::test_solve - NotImplementedError
FAILED exercises/317_matching_brackets/drill.py::test_solve - NotImplementedE...
FAILED exercises/318_series/drill.py::test_solve - NotImplementedError
FAILED exercises/319_sum_of_multiples/drill.py::test_solve - NotImplementedError
```

Reference run (import `drill.py` via importlib, `solve = _reference`, `test_solve()` under
`STUDY_SEED` 1, 2, 42):

```
310_word_count seed=1 ok
310_word_count seed=2 ok
310_word_count seed=42 ok
311_acronym seed=1 ok
311_acronym seed=2 ok
311_acronym seed=42 ok
312_run_length_encoding seed=1 ok
312_run_length_encoding seed=2 ok
312_run_length_encoding seed=42 ok
313_roman_numerals seed=1 ok
313_roman_numerals seed=2 ok
313_roman_numerals seed=42 ok
314_luhn seed=1 ok
314_luhn seed=2 ok
314_luhn seed=42 ok
315_isbn_verifier seed=1 ok
315_isbn_verifier seed=2 ok
315_isbn_verifier seed=42 ok
316_phone_number seed=1 ok
316_phone_number seed=2 ok
316_phone_number seed=42 ok
317_matching_brackets seed=1 ok
317_matching_brackets seed=2 ok
317_matching_brackets seed=42 ok
318_series seed=1 ok
318_series seed=2 ok
318_series seed=42 ok
319_sum_of_multiples seed=1 ok
319_sum_of_multiples seed=2 ok
319_sum_of_multiples seed=42 ok
```

`uv run study selfcheck`:

```
122/122 ok
```

(122 = the 104 migrated drills plus the folders other Phase B batches had landed at the time this
ran; all ten of batch F are in the ok set.)

Catalogue:

```
310_word_count             topic=310 minutes=15 hints=3 tags=['exercism', 'dicts', 'data-structures'] prereqs=[200, 215, 218, 227, 236]
311_acronym                topic=311 minutes=15 hints=3 tags=['exercism', 'regular-expressions', 'files-text'] prereqs=[200, 215, 218, 227]
312_run_length_encoding    topic=312 minutes=15 hints=3 tags=['exercism', 'iteration', 'regular-expressions', 'data-structures'] prereqs=[200, 203, 206, 209, 215, 218, 221, 224, 227]
313_roman_numerals         topic=313 minutes=15 hints=3 tags=['exercism', 'tuples', 'core'] prereqs=[200, 206, 209, 215, 218, 221, 224, 227, 233]
314_luhn                   topic=314 minutes=15 hints=3 tags=['exercism', 'classes', 'core'] prereqs=[200, 203, 206, 209, 215, 218, 221, 224, 227, 248]
315_isbn_verifier          topic=315 minutes=10 hints=3 tags=['exercism', 'strings', 'core'] prereqs=[200, 203, 209, 215]
316_phone_number           topic=316 minutes=15 hints=3 tags=['exercism', 'raising-and-handling-errors', 'string-formatting', 'errors'] prereqs=[200, 206, 215, 218, 221, 227, 248]
317_matching_brackets      topic=317 minutes=15 hints=3 tags=['exercism', 'conditionals', 'core'] prereqs=[200, 203, 209, 215, 221, 224, 227]
318_series                 topic=318 minutes=15 hints=3 tags=['exercism', 'sequences', 'data-structures'] prereqs=[200, 206, 209, 215, 221, 227]
319_sum_of_multiples       topic=319 minutes=10 hints=3 tags=['exercism', 'sets', 'data-structures'] prereqs=[200, 206, 209, 221, 227, 245]
```

Also checked mechanically for all ten: the `# ══ machinery …` marker line is byte-identical to the
one in `exercises/303_bob/drill.py`, README fences are balanced, no raw HTML outside code fences,
nothing follows `### Hint 3`, and every hint-3 snippet was executed to confirm the `# ->` results.

## Concerns

- Two `practices` lists map to two different section tags (`312` iteration + regular-expressions,
  `316` raising-and-handling-errors + string-formatting). The contract says "one section tag"; I
  took the tag of the first practice listed in `config.json` (`data-structures` and `errors`
  respectively). If the controller prefers a different tie-break, it is a one-word edit in the
  frontmatter.
- `311_acronym` and `316_phone_number` deviate from their exemplars as described above; both are
  deliberate, both follow the written instructions, and both pass every canonical case.
