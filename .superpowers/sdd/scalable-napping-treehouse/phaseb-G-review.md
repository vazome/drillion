# Phase B — batch G review (practice exercises, topics 320–329)

Reviewed at commit `6e59f33` on `main`. Ten folders: `320_etl` … `329_scrabble_score`.
Nothing was edited except this report.

**Verdict: needs one fix.** Nine drills approved as-is. `325_secret_handshake` has one wrong
character in its own Rules table, which contradicts both the worked example three lines below it
and the grader.

| drill | verdict |
| --- | --- |
| `320_etl` | approved |
| `321_flatten_array` | approved |
| `322_grains` | approved |
| `323_collatz_conjecture` | approved |
| `324_triangle` | approved |
| `325_secret_handshake` | **1 Important finding** (Rules table cell) |
| `326_space_age` | approved |
| `327_atbash_cipher` | approved |
| `328_rotational_cipher` | approved |
| `329_scrabble_score` | approved |

---

## Important

### 1. `325_secret_handshake/README.md:99` — Rules table gives the wrong bit for the 4th position

```
94:| position from the right | character in `"10011"` | action |
95:| --- | --- | --- |
96:| 1st | `1` | `"wink"` |
97:| 2nd | `1` | `"double blink"` |
98:| 3rd | `0` | `"close your eyes"` |
99:| 4th | `1` | `"jump"` |          ← the 4th character from the right of "10011" is `0`
100:| 5th (leftmost) | `1` | reverse the whole list |
```

`"10011"` read right-to-left is `1, 1, 0, 0, 1`. Row 4 must be `` `0` ``. As written the table says
`jump` fires, so a learner reading it computes `["jump", "double blink", "wink"]`, which contradicts
the example at line 111 of the same file:

```python
solve("10011")  # -> ["double blink", "wink"]
```

and the canonical Exercism case (`secret_handshake_test.py::test_reverse_two_actions`). Rows 1, 2, 3
and 5 are correct; only the middle cell of row 4 is wrong. One-character fix.

Everything else in the drill is correct: `_reference` is byte-for-byte the Exercism exemplar, all 11
canonical cases match the test file, and the `_gen` output is a uniform 5-bit string (32/32 possible
values seen in 200 draws).

## Minor / deferrable

- **`phaseb-G-report.md` drill table is stale for `329_scrabble_score`** — it still lists
  `exercism, regular-expressions, files-text`, while the file now reads
  `tags: [exercism, regular-expressions, core]` after the controller's settled override. Report-only;
  no file change needed. (The override itself is settled and not re-raised.)
- **`326_space_age` float-rounding concern can be closed.** The report flags that a learner who
  divides in two steps could land on the other side of a rounding boundary. I tested 200 000 ages
  drawn from `_gen`'s own distribution × 8 planets = **1 600 000 cases**: `round(s/(E*p), 2)`,
  `round(s/E/p, 2)` and `round(s/(p*E), 2)` gave identical results in every case. Zero divergence.
  The README already pins the exact expression, so nothing to do.
- **`328_rotational_cipher/README.md`, Hint 3** puts `# -> ['w0', 'w1', 'w2', 'w0', 'w1']` on its own
  line rather than as a trailing comment (house style: `expr  # -> result`). Line-length driven and
  cosmetic; `320` does the same thing correctly as a trailing comment on a short expression.
- **Canonical-case counts run above the contract's "3–6"** in several drills (`327` 13, `325` 11,
  `329` 11, `324` 21 spread over three per-function loops). Consistent with already-approved batches
  (`312_run_length_encoding` and `314_luhn` both carry 10), so I treat "3–6" as a floor, not a cap.
  No action.

---

## Verification of the report's specific claims

| claim | verdict |
| --- | --- |
| "0 missing lines" verbatim fidelity, introduction/instructions/instructions.append | **confirmed** by independent script (below) — 0 differing lines in all 20 sections |
| `hints.md` absent for all ten slugs → no `## Exercism hints` anywhere | **confirmed** — no source file exists, no section present |
| no `## Introduction` for triangle / atbash-cipher / rotational-cipher | **confirmed** — `introduction.md` does not exist for those three |
| grains' `# when the square value…` still a comment inside its ```python fence | **confirmed**, `322_grains/README.md:41`; same for collatz at `323/README.md:55` and space-age's `#creating an instance…` |
| `323` uses `//` where the exemplar uses `/`, and the README states it | **confirmed in substance.** The README never names the exemplar, but it pins `//` twice — Read-first bullet ("halving with `//` keeps the value an `int`; `/` turns it into a float") and Hint 2. There is also no learner-visible difference: `solve` returns a step count, and `/` produces the same count for every value the grader uses (all well under 2⁵³), so the verbatim Instructions ("divide it by 2") never contradict the grader. Nothing to fix. |
| `326` implements 31557600, not the exemplar's sidereal 31558149.76, and the README pins the exact expression | **confirmed.** `Rules` states `round(self.seconds / (31557600 * period), 2)`, byte-identical to `_reference`'s `round(self.seconds / (_EARTH_YEAR * _PERIODS[planet]), 2)`. All 8 canonical cases verified to pass with the instructions' constant. No contradiction with the verbatim Instructions, which themselves state 365.25 days / 31,557,600 s. |
| `326` returns a class from `solve()` in the ex_096 shape | **confirmed** — `solve()` no args returning the class, `_reference()` returning the class, `assert inspect.isclass(...)` first in `test_solve`; same shape as `096_async_cm/drill.py`. |

## Frontmatter audit (against `/tmp/exercism-python/config.json` + the concept→topic table)

All ten match exactly — difficulty→minutes, `prerequisites`→`prereqs`, `practices`+section tag→`tags`.

| slug | d | minutes | prereqs expected | tags expected | file |
| --- | --- | --- | --- | --- | --- |
| etl | 1 | 10 | [236] | exercism, dicts, data-structures | ✓ |
| flatten-array | 1 | 10 | [200,209,215,221,224,227] | exercism, core (no practices) | ✓ |
| grains | 1 | 10 | [200,206] | exercism, numbers, core | ✓ |
| collatz-conjecture | 1 | 10 | [200,206] | exercism, numbers, core | ✓ |
| triangle | 1 | 10 | [200,203,206] | exercism, bools, core | ✓ |
| secret-handshake | 1 | 10 | [200,203,206,209,215,218,221,224,227] | exercism, list-methods, core | ✓ |
| space-age | 1 | 10 | [200,203,206,221,224,227,236] | exercism, dicts, data-structures | ✓ |
| atbash-cipher | 2 | 15 | [200,209,215,218,221,224,227] | exercism, string-methods, core | ✓ |
| rotational-cipher | 1 | 10 | [200,206,209,215] | exercism, strings, core | ✓ |
| scrabble-score | 2 | 15 | [200,215,218,221,227,236] | exercism, regular-expressions, **core** (settled override) | ✓ |

`source:` present and correct on all ten; exactly one attribution line each, above `## Hints`.

## Deviations — judged

| drill | deviation | judgement |
| --- | --- | --- |
| `320_etl` | extra assertion that `legacy_data` is not mutated (Exercism does not test it) | fine — stated in Rules and in the report; the reference is a comprehension so it cannot mutate |
| `321_flatten_array` | `_reference`/`_gen` restricted to lists; exemplar flattens any non-str iterable | fine — the canonical tests only pass lists, the README says "a list", and a more general learner solution still passes |
| `323_collatz` | `//` vs exemplar's `/` | fine (see table above) |
| `326_space_age` | instructions' 31557600 vs exemplar's per-planet sidereal constants | correct call — the exemplar contradicts the verbatim Instructions, and following the Instructions is the legitimate choice per the standing ruling; stated in the README and the report; all 8 canonical cases pass |
| `329_scrabble_score` | drops the exemplar's `if not word.isalpha(): return 0` short-circuit | fine — that branch covers input the instructions never define; `_gen` only emits letter-only words and `""`, so reference and exemplar never disagree on anything the grader asks; `You get` pins the input contract |
| `324_triangle` | `len(set(sides))` classification vs exemplar's `zip`/`any` | equivalent; generated cases compare with `is`, matching `assertIs` |
| all | `solve` renamed from Exercism's `transform`/`flatten`/`steps`/`commands`/`rotate`/`score`, multi-function drills return a dict, `space-age` returns the class | each README carries a `> [!NOTE]` stating the Exercism stub name and this repo's entry point |

---

## Verification run (reviewer's own)

### `uv run ruff check` — batch G only

```
$ uv run ruff check exercises/320_etl/drill.py exercises/321_flatten_array/drill.py \
    exercises/322_grains/drill.py exercises/323_collatz_conjecture/drill.py \
    exercises/324_triangle/drill.py exercises/325_secret_handshake/drill.py \
    exercises/326_space_age/drill.py exercises/327_atbash_cipher/drill.py \
    exercises/328_rotational_cipher/drill.py exercises/329_scrabble_score/drill.py
All checks passed!
```

### Stub run — every drill fails `NotImplementedError`

```
$ uv run pytest exercises/320_etl … exercises/329_scrabble_score -q -p no:cacheprovider
FAILED exercises/320_etl/drill.py::test_solve - NotImplementedError
FAILED exercises/321_flatten_array/drill.py::test_solve - NotImplementedError
FAILED exercises/322_grains/drill.py::test_solve - NotImplementedError
FAILED exercises/323_collatz_conjecture/drill.py::test_solve - NotImplemented...
FAILED exercises/324_triangle/drill.py::test_solve - NotImplementedError
FAILED exercises/325_secret_handshake/drill.py::test_solve - NotImplementedError
FAILED exercises/326_space_age/drill.py::test_solve - NotImplementedError
FAILED exercises/327_atbash_cipher/drill.py::test_solve - NotImplementedError
FAILED exercises/328_rotational_cipher/drill.py::test_solve - NotImplementedE...
FAILED exercises/329_scrabble_score/drill.py::test_solve - NotImplementedError
10 failed in 0.13s
```

### Reference run — importlib load, `solve = _reference`, `test_solve()` under `STUDY_SEED` 1, 2, 42

```
seed   1  320_etl … 329_scrabble_score      all ok
seed   2  320_etl … 329_scrabble_score      all ok
seed  42  320_etl … 329_scrabble_score      all ok
failures: 0
```

### `uv run study selfcheck`

```
$ uv run study selfcheck
159/159 ok
```

### Verbatim-fidelity diff (scripted, reviewer's own transform)

Script re-derives each section from `/tmp/exercism-python/exercises/practice/<slug>/.docs/*` applying
only the permitted transformations (drop top `#`, `##`→`###`, `~~~~exercism/note`→`> [!NOTE]` with
`>` prefixes, drop `<br>`, never touch lines inside a fence) and diffs against the README section.

```
320_etl                  Introduction    0 differing lines  (14 lines)
320_etl                  Instructions    0 differing lines  (24 lines)
320_etl                  Exercism hints  source ABSENT, section absent  ok
321_flatten_array        Introduction    0 differing lines  (5 lines)
321_flatten_array        Instructions    0 differing lines  (14 lines)
321_flatten_array        Exercism hints  source ABSENT, section absent  ok
322_grains               Introduction    0 differing lines  (4 lines)
322_grains               Instructions    0 differing lines  (22 lines)
322_grains               Exercism hints  source ABSENT, section absent  ok
323_collatz_conjecture   Introduction    0 differing lines  (26 lines)
323_collatz_conjecture   Instructions    0 differing lines  (14 lines)
323_collatz_conjecture   Exercism hints  source ABSENT, section absent  ok
324_triangle             Introduction    source ABSENT, section absent  ok
324_triangle             Instructions    0 differing lines  (32 lines)
324_triangle             Exercism hints  source ABSENT, section absent  ok
325_secret_handshake     Introduction    0 differing lines  (5 lines)
325_secret_handshake     Instructions    0 differing lines  (52 lines)
325_secret_handshake     Exercism hints  source ABSENT, section absent  ok
326_space_age            Introduction    0 differing lines  (17 lines)
326_space_age            Instructions    0 differing lines  (50 lines)
326_space_age            Exercism hints  source ABSENT, section absent  ok
327_atbash_cipher        Introduction    source ABSENT, section absent  ok
327_atbash_cipher        Instructions    0 differing lines  (25 lines)
327_atbash_cipher        Exercism hints  source ABSENT, section absent  ok
328_rotational_cipher    Introduction    source ABSENT, section absent  ok
328_rotational_cipher    Instructions    0 differing lines  (27 lines)
328_rotational_cipher    Exercism hints  source ABSENT, section absent  ok
329_scrabble_score       Introduction    0 differing lines  (5 lines)
329_scrabble_score       Instructions    0 differing lines  (23 lines)
329_scrabble_score       Exercism hints  source ABSENT, section absent  ok

sections with differences: 0
```

(Only trailing whitespace is normalised — grains' `instructions.append.md:12` carries 8 trailing
spaces after the fenced comment, which the README drops. Immaterial.)

### Structural pass (scripted): fence balance, section order, heading levels, attribution, hints

```
320_etl                  OK
321_flatten_array        OK
322_grains               OK
323_collatz_conjecture   OK
324_triangle             OK
325_secret_handshake     OK
326_space_age            OK
327_atbash_cipher        OK
328_rotational_cipher    OK   (the one flag was my script's own false positive: `# -> [...]`
                               inside Hint 3's ```python fence, verified by hand at line 8 of
                               the Hint 3 block — it is code, not a heading)
329_scrabble_score       OK
```

Checked per file: YAML frontmatter present; section order `Why · Introduction · Instructions ·
You get · You return · Rules · Read first · Hints` with no unexpected `##`; exactly one `# title`;
exactly `### Hint 1/2/3` and nothing after Hint 3; exactly one attribution line, above `## Hints`;
no heading deeper than `###`; no raw HTML outside code spans/fences.

### `drill.py` structural pass

```
303_bob marker (reference): line 5  '# ══ machinery — everything below is the grader's, not yours ══'
320_etl                marker=1 exact  first='def solve(legacy_data):'  moddoc=False solvedoc=False body=[Raise]
321_flatten_array      marker=1 exact  first='def solve(iterable):'     moddoc=False solvedoc=False body=[Raise]
322_grains             marker=1 exact  first='def solve():'             moddoc=False solvedoc=False body=[Raise]
323_collatz_conjecture marker=1 exact  first='def solve(number):'       moddoc=False solvedoc=False body=[Raise]
324_triangle           marker=1 exact  first='def solve():'             moddoc=False solvedoc=False body=[Raise]
325_secret_handshake   marker=1 exact  first='def solve(binary_str):'   moddoc=False solvedoc=False body=[Raise]
326_space_age          marker=1 exact  first='def solve():'             moddoc=False solvedoc=False body=[Raise]
327_atbash_cipher      marker=1 exact  first='def solve():'             moddoc=False solvedoc=False body=[Raise]
328_rotational_cipher  marker=1 exact  first='def solve(text, key):'    moddoc=False solvedoc=False body=[Raise]
329_scrabble_score     marker=1 exact  first='def solve(word):'         moddoc=False solvedoc=False body=[Raise]
```

### `_gen` variety (200 draws each, `STUDY_SEED=1`)

```
320_etl                  unique= 200/200   e.g. {1: ['X','Y','L','K','W']} | {6: ['R','L','C','B','I']}
321_flatten_array        unique= 140/200   e.g. [145, None, None, 70] | [None]
322_grains               unique=  61/200   (64 possible values — saturated)
323_collatz_conjecture   unique= 155/200   e.g. 3 | 16
324_triangle             unique= 172/200   e.g. [1, 12, 12] | [5.0, 3.0, 3.5]
325_secret_handshake     unique=  32/200   (32 possible 5-bit strings — saturated)
326_space_age            unique= 200/200   e.g. 711178002 | 44234785
327_atbash_cipher        unique= 200/200   e.g. "FOX truth; exercism thought'42. deep'yes DOG"
328_rotational_cipher    unique= 200/200   e.g. ('the, eat. the omg dog.', 11)
329_scrabble_score       unique= 122/200   e.g. 'ZYCIDPYOPUMZG' | 'mntyyawoixzhs'
```

No near-constant generator. `322` and `325` saturate their whole input space, which is the correct
behaviour for a 1–64 square number and a 5-bit string. `324` mixes int and 0.5-unit float sides and
covers degenerate/invalid triples. `327`/`328` vary case, punctuation, digits and (for `328`) the
key including the `0` and `26` edge cases.

### Canonical cases cross-checked against the Exercism test files

Every asserted canonical case in all ten `drill.py` files was matched against
`<slug>/<slug>_test.py`. All present and correct. Error messages are verbatim:

- `322_grains`: `pytest.raises(ValueError, match=r"^square must be between 1 and 64$")` —
  matches `err.exception.args[0] == "square must be between 1 and 64"`; no regex metacharacters,
  anchoring is correct.
- `323_collatz_conjecture`: `match=r"^Only positive integers are allowed$"` — matches, capital `O`
  included.

### README example execution (scripted)

Every `expr  # -> value` line inside our own sections (`You get`, `You return`, `Rules`) of all ten
READMEs was evaluated against that drill's `_reference`:

```
320_etl  3   321_flatten_array  2   322_grains  4   323_collatz  4   324_triangle  6
325_secret_handshake  6   326_space_age  7   327_atbash  8   328_rotational  6   329_scrabble  7
mismatches: 0
```

53 examples, all correct. (The Rules **table** in `325` is prose, not an executable example, which
is why the wrong cell survived this check and had to be caught by reading — see the Important
finding.)

### Catalogue

```
320_etl                  topic=320 min=10 hints=3 tags=['exercism','dicts','data-structures'] prereqs=[236] src=ok sections=ok
321_flatten_array        topic=321 min=10 hints=3 tags=['exercism','core'] prereqs=[200,209,215,221,224,227] src=ok sections=ok
322_grains               topic=322 min=10 hints=3 tags=['exercism','numbers','core'] prereqs=[200,206] src=ok sections=ok
323_collatz_conjecture   topic=323 min=10 hints=3 tags=['exercism','numbers','core'] prereqs=[200,206] src=ok sections=ok
324_triangle             topic=324 min=10 hints=3 tags=['exercism','bools','core'] prereqs=[200,203,206] src=ok sections=ok
325_secret_handshake     topic=325 min=10 hints=3 tags=['exercism','list-methods','core'] prereqs=[200,203,206,209,215,218,221,224,227] src=ok sections=ok
326_space_age            topic=326 min=10 hints=3 tags=['exercism','dicts','data-structures'] prereqs=[200,203,206,221,224,227,236] src=ok sections=ok
327_atbash_cipher        topic=327 min=15 hints=3 tags=['exercism','string-methods','core'] prereqs=[200,209,215,218,221,224,227] src=ok sections=ok
328_rotational_cipher    topic=328 min=10 hints=3 tags=['exercism','strings','core'] prereqs=[200,206,209,215] src=ok sections=ok
329_scrabble_score       topic=329 min=15 hints=3 tags=['exercism','regular-expressions','core'] prereqs=[200,215,218,221,227,236] src=ok sections=ok
```

Git tracks exactly 20 files for this batch (10 × README.md + drill.py); no `__pycache__` is tracked.

---

## Content quality notes (no action)

- **`## Why`** is business framing in all ten, never an algorithm restatement: `320` is config
  inversion at load time, `322` is capacity estimates and Python's unbounded ints, `324` is one
  shared precondition behind three questions, `325` is bitmasks and `chmod`, `326` is one stored
  duration rendered in many units, `328` is `%`-wrapping and not eating characters you were not
  asked to touch. Good.
- **Hints escalate correctly** in all ten: Hint 1 nudges (`323`: "do 12 on paper, the answer is 9
  not 10"), Hint 2 is prose strategy naming the tools, Hint 3 works the same shape on genuinely
  different data (retry backoff, cache shrink, deployment classification, permission triads, API
  token chunking, round-robin worker assignment, a basket price list, a `Duration` class). No Hint 2
  contains the reference body written with the drill's parameter names; no hint states an answer for
  this drill's own data.
- `324`'s Hint 2 is the most explicit of the ten ("three distinct means scalene, one means
  equilateral… a set built from the sides tells you that count"), but it is prose strategy with no
  expression and no literal for the drill's data — within the contract.
- `322`'s and `326`'s `Rules` sections state closed-form expressions (`2 ** (n - 1)`, `2 ** 64 - 1`,
  `round(self.seconds / (31557600 * period), 2)`). That matches established, already-approved
  practice in this catalogue (`315_isbn_verifier` spells out the whole weighted-sum algorithm in
  Rules; `313_roman_numerals` gives the full symbol table), and for `326` pinning the expression is
  exactly what the constant conflict requires. Not raised as a finding.
