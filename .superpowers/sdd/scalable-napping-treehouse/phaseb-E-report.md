# Phase B — batch E report (practice topics 300–309)

Worktree: `/home/daniel/study-exercism` (branch `exercism-drills`). 10 files written, nothing else
touched. No git state-changing commands were run.

## Files

| file | topic | title | minutes | prereqs | tags |
|---|---|---|---|---|---|
| `exercises/ex_300_two_fer.py` | 300 | two-fer — the bakery's one-for-you line | 10 | 200, 245 | exercism, function-arguments, core |
| `exercises/ex_301_leap.py` | 301 | leap — does this year have a 29 February? | 10 | 200, 203, 206 | exercism, bools, core |
| `exercises/ex_302_raindrops.py` | 302 | raindrops — sounds for the factors 3, 5 and 7 | 10 | 200, 203, 206, 209 | exercism, conditionals, core |
| `exercises/ex_303_bob.py` | 303 | bob — classify a message into one of five replies | 10 | 200, 209 | exercism, conditionals, core |
| `exercises/ex_304_reverse_string.py` | 304 | reverse-string — read the text back to front | 10 | 200, 203, 209, 215 | exercism, sequences, data-structures |
| `exercises/ex_305_isogram.py` | 305 | isogram — a word with no repeated letter | 10 | 215 | exercism, strings, core |
| `exercises/ex_306_pangram.py` | 306 | pangram — a sentence that uses every letter | 10 | 200, 203, 209, 215 | exercism, strings, core |
| `exercises/ex_307_anagram.py` | 307 | anagram — pick the rearrangements out of a word list | 10 | 200, 203, 209, 215, 218, 221, 224, 227 | exercism, list-methods, core |
| `exercises/ex_308_hamming.py` | 308 | hamming — how many positions do two strands differ in? | 10 | 200, 206, 209, 221, 227 | exercism, generator-expressions, raising-and-handling-errors, sequences, data-structures |
| `exercises/ex_309_rna_transcription.py` | 309 | rna-transcription — turn a DNA strand into its RNA partner | 10 | 200, 203, 209, 215, 218, 227 | exercism, string-methods, core |

All ten are Exercism difficulty 1 → `minutes: 10`. `prereqs` are each slug's `prerequisites` from
`/tmp/exercism-python/config.json` mapped through the concept→topic table, unknown concepts
dropped, then sorted ascending. `tags` = `exercism` + the slug's `practices` (kebab-case, as-is) +
one section tag.

## Decisions / deviations

1. **`solve(name="you")` in ex_300.** Exercism's stub is `def two_fer(name)` with no default, but
   its own tests call `two_fer()` and its exemplar has `name='you'`. The default has to be in the
   signature here, because `study.py::_reference_call` rebuilds the call from `solve`'s signature —
   `def solve(name)` would make the canonical `solve()` case a TypeError under `selfcheck`. The
   docstring and hints still make the default-argument mechanic the point of the drill.
2. **Section tag for a multi-practice exercise (ex_308 hamming).** Rule applied: the *first* listed
   practice decides the section tag — `generator-expressions` → `data-structures`. The error side
   of the drill is still tagged via `raising-and-handling-errors`. If the reviewer prefers "the
   most characteristic practice decides", hamming would move to `errors`; flagging so all batches
   stay consistent.
3. **READ FIRST links for concepts whose `links.json` is a TODO placeholder** (`sequences`,
   `generator-expressions`, `raising-and-handling-errors` all contain four `http://example.com/`
   entries). For ex_304 and ex_308 I substituted the matching docs.python.org sections
   (slicings / common sequence operations, zip, raising exceptions, generator expressions) plus
   one Real Python page. Every other file's links come from the practiced concept's `links.json`.
4. **Generated cases never trigger the error path** in ex_308 — `_gen` only produces equal-length
   strands, since `solve(...) == _reference(...)` cannot express "both raise". The unequal-length
   rule is covered by two canonical `pytest.raises(ValueError, match="Strands must be of equal
   length.")` cases copied from Exercism's test file.
5. **`zip(..., strict=True)`** in ex_308's `_reference` — reached only after the length guard, so
   it can never fire; it is there so the reference cannot silently drift.
6. Canonical cases are copied verbatim from each `*_test.py` (3–6 per file, 6 where the canonical
   suite had interesting edge cases: empty input, unicode, mixed case). Boolean-returning drills
   (leap, isogram, pangram) assert with `is True` / `is False`, mirroring Exercism's `assertIs`,
   so a truthy non-bool does not pass.

## Verification (run from `/home/daniel/study-exercism`)

```
$ uv run ruff check exercises/ex_300_two_fer.py exercises/ex_301_leap.py \
    exercises/ex_302_raindrops.py exercises/ex_303_bob.py exercises/ex_304_reverse_string.py \
    exercises/ex_305_isogram.py exercises/ex_306_pangram.py exercises/ex_307_anagram.py \
    exercises/ex_308_hamming.py exercises/ex_309_rna_transcription.py
All checks passed!
```

Stub runs — `uv run pytest exercises/<file> -q -p no:cacheprovider`, last lines:

```
ex_300_two_fer:            FAILED exercises/ex_300_two_fer.py::test_solve - NotImplementedError
ex_301_leap:               FAILED exercises/ex_301_leap.py::test_solve - NotImplementedError
ex_302_raindrops:          FAILED exercises/ex_302_raindrops.py::test_solve - NotImplementedError
ex_303_bob:                FAILED exercises/ex_303_bob.py::test_solve - NotImplementedError
ex_304_reverse_string:     FAILED exercises/ex_304_reverse_string.py::test_solve - NotImplementedError
ex_305_isogram:            FAILED exercises/ex_305_isogram.py::test_solve - NotImplementedError
ex_306_pangram:            FAILED exercises/ex_306_pangram.py::test_solve - NotImplementedError
ex_307_anagram:            FAILED exercises/ex_307_anagram.py::test_solve - NotImplementedError
ex_308_hamming:            FAILED exercises/ex_308_hamming.py::test_solve - NotImplementedError
ex_309_rna_transcription:  FAILED exercises/ex_309_rna_transcription.py::test_solve - NotImplementedError
```

```
$ uv run study.py selfcheck
104/104 ok
```
(104 = the catalogue as it stood while other batches were landing; no failures, mine included.)

```
$ uv run python -c "import study; print(len(study.exercises()))"
104
```
`study.exercises()` keys include `ex_300_two_fer, ex_301_leap, ex_302_raindrops, ex_303_bob,
ex_304_reverse_string, ex_305_isogram, ex_306_pangram, ex_307_anagram, ex_308_hamming,
ex_309_rna_transcription`, each reporting `hints: 3` and the topic/minutes/prereqs/tags above.

Extra: the reference was run against six different seeds (`STUDY_SEED=1 2 3 42 99 12345`, with
`solve = _reference`) — all ten files pass every time, so `_gen`'s edge cases (empty strand, empty
phrase, zero-length sample) are safe.

## Open concerns

1. **`study.read_first()` returns `[]` for every Exercism drill.** The contract puts the
   `# SOURCE:` line before the `# READ FIRST:` block, but `study.py::read_first` only accepts the
   comment block when its *first* line starts with `READ FIRST`. Verified:
   `study.exercises()['ex_300_two_fer']['read_first'] == []` — and the same is true of the
   `ex_2xx` concept drills other batches have already written, so the UI will show no links for any
   of the ~80 new files. Two one-line fixes are available to the controller: skip a leading
   `SOURCE:` line in `read_first`, or move the SOURCE line to the end of the block. I followed the
   contract as written rather than deviating unilaterally.
2. While I ran verification, another implementer's `selfcheck` had 104 `exercises/_selfcheck_*.py`
   temp files on disk (that command writes then deletes them). They are not mine and they clean
   themselves up; just make sure none survive before the controller stages the commit.
