# Phase B — batch H review (practice 330–339)

Reviewer pass over the ten uncommitted folders `exercises/330_pig_latin` … `339_high_scores`.
Every claim in `phaseb-H-report.md` was re-derived independently rather than trusted, per the
provenance warning (330–337 inherited from an implementer that never self-verified them).

**Verdict: 8 of 10 approved as written. 2 Important findings, both one-edit fixes.**

| drill | verdict |
| --- | --- |
| 330_pig_latin | **needs fix** — wrong string in the `## Rules` WARNING (finding I-1) |
| 331_protein_translation | approved |
| 332_transpose | approved |
| 333_sublist | approved (one minor note) |
| 334_prime_factors | approved |
| 335_nth_prime | approved **once concern 2 is applied** (ruling below) |
| 336_sieve | approved |
| 337_saddle_points | approved |
| 338_clock | **needs fix** — the non-mutation assert is unreachable (finding I-2) |
| 339_high_scores | approved |

---

## Findings

### Important

**I-1 — `exercises/330_pig_latin/README.md:115`: the WARNING states an output that the mistake it
describes does not produce.**

> Checking "is the first letter a vowel?" before checking `xr`/`yt` is fine, but checking the plain
> consonant run before the `qu` rule is not: `square` would become `quaresay` instead of `aresquay`.

Measured:

```
rule-2-first (run = leading consonants, u is a vowel): uaresqay
move only the first consonant                        : quaresay
README claims                                        : quaresay
correct answer                                       : aresquay
```

"Checking the plain consonant run before the `qu` rule" moves `sq` and yields **`uaresqay`**.
`quaresay` is what you get from moving only the *first* consonant — a different mistake from the one
the sentence names. A learner who writes the bug the warning describes sees `uaresqay`, does not
recognise the warning, and is left without the signpost the warning exists to give.

Fix: change `quaresay` → `uaresqay` (leaves the sentence's cause and cure correct), or rewrite the
clause to describe the single-consonant bug. This is the only defect found by reading prose rather
than by script — the batch G lesson applied. Every other prose table and per-position claim in the
batch was checked and is correct (see "Prose and table audit").

**I-2 — `exercises/338_clock/drill.py:53–55`: the non-mutation assert never runs for a mutating
solution; the failure is blamed on subtraction instead.**

The batch's headline deviation (see concern 1) is justified in the report on the grounds that the
rule "is stated in `## Rules` and in a `> [!WARNING]`, so it is not a gotcha", and `test_solve:55`
carries the explanatory message `"+ and - must not change Clock(h, m) itself"`. As shipped it *is*
a gotcha. Running Exercism's own mutating exemplar against `test_solve`:

```
exemplar FAILS at drill.py:54 -> Clock(25, 2117) - 868
```

Why: line 53 mutates `mine` to `T + shift` (the mutating `__add__` returns `self`), so line 54
compares `mine - shift` (= `T`) against `theirs - shift` (= `T - shift`) and fails there — with the
message `f"Clock({hour}, {minute}) - {shift}"`, which points the learner at `__sub__`. Line 55, the
one assert whose message explains the actual rule, is unreachable.

The verdict is still correct (a mutating solution is rejected), only the diagnosis is wrong — and
"a learner must never be left to brute-force something they are unaware of" (AGENTS.md, UX) applies
to opaque failure messages just as much as to timeouts.

Fix (one line moved): put the non-mutation check between the `+` check and the `-` check —

```python
        assert str(mine + shift) == str(theirs + shift), f"Clock({hour}, {minute}) + {shift}"
        assert str(mine) == str(theirs), f"+ and - must not change Clock({hour}, {minute}) itself"
        assert str(mine - shift) == str(theirs - shift), f"Clock({hour}, {minute}) - {shift}"
        assert str(mine) == str(theirs), f"+ and - must not change Clock({hour}, {minute}) itself"
```

or rebuild `mine` before line 54. Either way `_reference` still passes at all three seeds.

### Minor (deferrable)

- **`333_sublist/README.md:99`** — hint 2 ends with `the range ends at len(big) - len(small) + 1`.
  It is the exact off-by-one the hint exists to head off, `big`/`small` are introduced by the hint's
  own sentence and are not `solve`'s parameter names (`list_one`/`list_two`), and hint 3 gives the
  same expression on deploy-log data, which is what hint 3 is for. Inside the bar; the closest call
  in the batch, and the implementer flagged it themselves. **No change needed.**
- **`338_clock/drill.py:13–14`** — `r.choice([r.randint(0, 23), r.randint(-120, 120), r.randint(24, 300)])`
  evaluates all three `randint` calls and discards two. Harmless (variety measured at 295/300
  distinct), just three RNG draws where one would do.
- **`335_nth_prime/README.md:68`** — `solve(10001)  # -> 104743` hands over a graded answer verbatim.
  Consistent with how 334 lists `solve(901255)`, and the generated cases + the first-20 sequence
  make hardcoding useless as a strategy, so this is fine as-is. If the controller prefers, the
  concern-2 warning can name the case without repeating the value.
- **`334_prime_factors/README.md:86`** — "a hundred thousand steps" is loose (the real outer loop for
  `93819012551` runs ~9,539 iterations; √n is ~306,300). Order-of-magnitude rhetoric against "a
  hundred billion"; not worth changing.

### Not findings (checked and cleared)

- `335_nth_prime/README.md:31` and `337_saddle_points/README.md:62, 99` contain `#`-prefixed lines,
  but all three are **inside** ```` ```python ```` fences and are code, exactly as upstream has
  them. The batch F defect (a fence comment promoted to a heading) does **not** occur anywhere in
  this batch — proven by the fidelity diff below, which is fence-aware.
- `330_pig_latin/drill.py:11–12` — `_VOWEL_SOUND` treats any `y` + consonant as a vowel sound
  (broader than the `yt` the instructions state) and `_CONSONANT_RUN` allows at most one consonant
  before `qu` (narrower than "zero or more"). Both are Exercism's `.meta/example.py` **verbatim**,
  both pass the full upstream suite, and a learner implementing the README's stated rules literally
  agrees with `_reference` on all 37 words in `_WORDS` (checked). Not a deviation to report.
- `338`/`339` hint 3 blocks are the answer's shape in different clothes (`Bearing`, `Latencies`).
  This is the established model — `326_space_age`'s hint 3 is a full `Duration` class mirroring the
  answer, and it was approved. Consistent, not a leak.

---

## Rulings on the three concerns

### 1. `338_clock` non-mutation — **KEEP the rule and both statements of it.** Fix I-2 alongside.

- Exercism's `.meta/example.py` `__add__`/`__sub__` mutate `self` and return `self`, and its
  `__eq__` compares `repr()` strings. `c + 3` silently changing `c` is a latent bug in a value
  object, and the standing ruling explicitly permits implementing the **instructions** over a buggy
  exemplar provided the choice is stated in the README and the report. Both are.
- The instructions' own append (the `__repr__`/`__str__` essay, README:27–102) pushes value-object
  semantics throughout; a value type whose `+` mutates contradicts it.
- The drill's `## Why` and its hint 3 (`Bearing`) are both built on "never touch `self`". Dropping
  the rule would leave the `## Why` promising something the grader does not check.
- Stating it twice is right, and they are not redundant: `## Rules:136` is the **contract** ("`+`
  and `-` … return a new Clock"); the second `> [!WARNING]` (:150–151) is the **consequence** plus
  the honest disclosure that Exercism's own cases would not notice. That disclosure is what stops
  it being a gotcha — provided the assert reports it, which is finding I-2.
- Confirmed empirically that Exercism's tests do not notice: `_reference` passes all **55** upstream
  `clock_test.py` tests, and so does the mutating exemplar.

### 2. `335_nth_prime` grades `solve(10001)` — **option (b): keep the case, add the `> [!WARNING]`.**

Measured on this machine:

```
naive solve(1500)  = 12553  in  0.6s
naive solve(10001) = 104743 in 32.6s      # all(cand % d for d in range(2, cand))
```

`src/study/runner.py:30` runs `pytest … -x --timeout=10`, and pytest-timeout 2.4.0 is installed, so
that is a hard per-test kill at 10 s. A learner whose solution is **correct but naive** is killed at
10 s with no assertion output — and the generated cases (up to 1500 ≈ 0.6 s each, ~2.7 of 6 draws
in that band) have already eaten part of the budget before `solve(10001)` is reached.

Why (b) rather than (a) or (c):

- (a) leaves a correct learner staring at an opaque kill. AGENTS.md's UX principle is explicit:
  "you can't bruteforce something you are unaware of." A stated requirement is the whole remedy.
- (c) loses `test_big_prime`, and with it the only pressure that teaches the √n bound — which is
  what `## Why` (README:13), the `math.isqrt` entry in `## Read first` (:80) and hint 2 (:89) are
  all built around. It would gut the drill to hide a warning-shaped problem.
- **The decisive argument is internal consistency:** `334_prime_factors/README.md:86`, in this same
  batch, already does exactly (b) for exactly this failure mode — it names the graded case
  `solve(93819012551)`, says a walk-every-candidate loop "will not finish before the runner gives
  up", and points at the square-root cut-off. 335's current mitigation is one clause in `## You get`
  (:42), "so brute force has to be at least reasonable", which does not tell the learner that the
  run will be **killed** rather than fail. Two sibling drills, same trap, one warned and one not.

Suggested placement: a `> [!WARNING]` at the end of `## Rules` (after the fence at :65–71), saying
that the grader includes the 10001st prime and that testing every divisor below the candidate will
not finish inside the runner's limit — test divisors only up to √n.

### 3. `336_sieve` primes-below-1000 literal — **closed, no action.**

Confirmed: the literal is `drill.py:44–57`, the marker is `drill.py:5`, so it is below the marker
and invisible to the learner.

```
$ grep -rln "971, 977, 983, 991, 997" exercises/336_sieve/
exercises/336_sieve/drill.py
```

It appears nowhere in `README.md` and in no hint. The only README hit for "primes" is prose in
`## Why:13`.

---

## Verification actually run (reviewer's own, not the report's)

### ruff

```
$ uv run ruff check exercises/330_pig_latin/drill.py … exercises/339_high_scores/drill.py
All checks passed!
```

### stub run — every drill must fail with NotImplementedError

```
$ uv run pytest exercises/330_pig_latin … exercises/339_high_scores -q -p no:cacheprovider
FAILED exercises/330_pig_latin/drill.py::test_solve - NotImplementedError
FAILED exercises/331_protein_translation/drill.py::test_solve - NotImplemente...
FAILED exercises/332_transpose/drill.py::test_solve - NotImplementedError
FAILED exercises/333_sublist/drill.py::test_solve - NotImplementedError
FAILED exercises/334_prime_factors/drill.py::test_solve - NotImplementedError
FAILED exercises/335_nth_prime/drill.py::test_solve - NotImplementedError
FAILED exercises/336_sieve/drill.py::test_solve - NotImplementedError
FAILED exercises/337_saddle_points/drill.py::test_solve - NotImplementedError
FAILED exercises/338_clock/drill.py::test_solve - NotImplementedError
FAILED exercises/339_high_scores/drill.py::test_solve - NotImplementedError
10 failed in 0.11s
```

### reference run — importlib-load, `solve = _reference`, `test_solve()` at STUDY_SEED 1, 2, 42

```
seed 1  330:0.00s OK 331:0.00s OK 332:0.00s OK 333:0.00s OK 334:0.00s OK
        335:0.05s OK 336:0.00s OK 337:0.00s OK 338:0.00s OK 339:0.00s OK
seed 2  … all ten OK (335 0.06s)
seed 42 … all ten OK (335 0.05s)
```

### selfcheck

```
$ uv run study selfcheck
161/161 ok
```

### verbatim fidelity — my own fence-aware differ against `/tmp/exercism-python`

Transformations allowed: top `#` heading dropped, `##`→`###` **outside fences only**,
`~~~~exercism/note` → `> [!NOTE]` blockquote, `<br>` dropped, blank lines ignored.

```
330_pig_latin              Introduction  OK (5 lines)     Instructions  OK (27 lines)
331_protein_translation    Introduction  ABSENT-OK        Instructions  OK (27 lines)
332_transpose              Introduction  ABSENT-OK        Instructions  OK (42 lines)
333_sublist                Introduction  ABSENT-OK        Instructions  OK (19 lines)
334_prime_factors          Introduction  ABSENT-OK        Instructions  OK (25 lines)
335_nth_prime              Introduction  ABSENT-OK        Instructions  OK (11 lines)
336_sieve                  Introduction  OK (4 lines)     Instructions  OK (69 lines)*
337_saddle_points          Introduction  OK (6 lines)     Instructions  OK (26 lines)
338_clock                  Introduction  ABSENT-OK        Instructions  OK (64 lines)
339_high_scores            Introduction  ABSENT-OK        Instructions  OK (9 lines)
```

**0 missing or changed lines across all ten.** (*336's single reported line was my differ not
emitting the `> [!NOTE]` marker itself; the README's marker at :39 is the sanctioned rendering of
`~~~~exercism/note` at `sieve/.docs/instructions.md:19`. Inspected by hand and correct.)
`instructions.append.md` is folded in for the four exercises that have one (335, 337, 338, 339) and
is included in the counts above. No exercise in this batch has a `hints.md`, so the absent
`## Exercism hints` section is correct in all ten. The report's claim of 0 changed lines is
**verified**.

### structural pass

Fence balance, `## ` section order against `Why · Introduction · Instructions · You get · You return ·
Rules · Exercism hints · Read first · Hints`, one H1 matching frontmatter `title`, exactly one
attribution line, three `### Hint N` with nothing after Hint 3, no raw HTML, marker byte-identical
to `exercises/303_bob/drill.py`'s and appearing exactly once, no docstring in the learner region,
stub body `raise NotImplementedError`:

```
330 … 339   all OK   (only flags were `# comment` lines inside python fences — see "Not findings")
```

`marker_line` per the catalogue: 5 for nine drills, 12 for `333_sublist` (it has the four given
constants above `solve`, with the required `# given — do not edit` comment at :1).

### frontmatter re-derived from `/tmp/exercism-python/config.json` (not taken from the report)

| drill | difficulty→minutes | prerequisites→prereqs | practices→tags | verdict |
| --- | --- | --- | --- | --- |
| 330 pig-latin | 2 → 15 | basics,bools,conditionals → 200,203,209 | [conditionals] + core | ✔ |
| 331 protein-translation | 2 → 15 | 200,209,215,218,221,227 | [] → core | ✔ |
| 332 transpose | 2 → 15 | 200,203,206,209,215,218,221,224,227,242 | [unpacking-…] + core | ✔ |
| 333 sublist | 2 → 15 | 200,203,209,212,221 | [comparisons] + core | ✔ |
| 334 prime-factors | 2 → 15 | 200,206,209,221,224,227 | [] → core | ✔ |
| 335 nth-prime | 2 → 15 | 200,203,206,209,212,215,221,224,227 | [generators] + data-structures | ✔ |
| 336 sieve | 3 → 20 | 200,206,209,221,224,227,245 | [sets] + data-structures | ✔ |
| 337 saddle-points | 3 → 20 | 200,209,221,224,227,245 | [loops] + core | ✔ |
| 338 clock | 3 → 20 | 200,206,215,248 | [class-composition, rich-comparisons, string-formatting] + core¹ | ✔ |
| 339 high-scores | 3 → 20 | 200,221,224,248 | [classes] + core | ✔ |

¹ section tag from the **first** listed practice (`class-composition` → `class-*` → `core`), per the
standing ruling. All ten match the folders exactly; `source:` lines all present and correct.

### each `_reference` against the ENTIRE upstream canonical test file (re-run, all ten)

Shimmed `pig_latin.translate` → `_reference` etc. into a temp package and ran Exercism's own
`*_test.py` unmodified:

```
330_pig_latin              23 passed in 0.03s
331_protein_translation    26 passed in 0.03s
332_transpose              12 passed in 0.02s
333_sublist                22 passed in 0.53s
334_prime_factors          12 passed in 0.02s
335_nth_prime               6 passed in 0.06s
336_sieve                   5 passed in 0.01s
337_saddle_points          10 passed in 0.02s
338_clock                  55 passed in 0.06s
339_high_scores            12 passed in 0.02s
```

**183 upstream tests, all passing** — the report's headline claim reproduced exactly, including the
116 across the inherited eight. The inherited eight's `_reference`s are correct.

### every README example executed against `_reference` (`Why` / `You get` / `You return` / `Rules`)

```
330:7  331:6  332:6  333:8  334:7  335:7  336:6  337:7  338:10  339:8
TOTAL 72 examples, 0 mismatches
```

Includes the `# raises ValueError(...)` forms (335, 337), the two-line example at
`337_saddle_points/README.md:98–99`, and the `Clock = solve()` / `HighScores = solve()` class forms.

### every hint code block executed

All ten hint-3 blocks exec cleanly and every `# ->` in them is the value Python produces —
including `336_sieve`'s free-ports block (`[8001, 8002, 8004, 8005, 8007, 8008]`) and
`337_saddle_points`'s latency grid (`[120, 120]`, `[70, 120, 60]`, `[(1, 2), (2, 2)]`).

### prose and table audit (the batch G lesson — read, don't just run)

- **330 `## Rules` table (:94–100) and bullets (:102–104)** — all 16 stated word→translation pairs
  executed against `_reference`: **all correct**. Additionally, a literal implementation of the
  README's *stated* rules (vowel or `xr`/`yt` first, then `qu`, then `y`) agrees with `_reference`
  on every one of the 37 words in `_WORDS`. The WARNING at :115 is the exception — finding I-1.
- **331 codon table (:26–35)** — parsed out of the README and compared to `_CODONS`: 17 codons,
  **exact match**, including the four `Serine` rows and the three `STOP` rows.
- **332 triangle table (:111–120)** — `T/EE/AAA/SSSS/EEEEE/RRRRRR` → the six output rows with `_`
  standing for a real space: **matches `_reference` character for character**.
- **332 WARNING (:123)**, **331 WARNING (:87)** (`"AUGAUG"`, `UGA` on a codon boundary),
  **333 WARNING (:85)** (run starts at index 1, fails at `3`, a later start at index 4 works),
  **336 WARNING (:156)** (`marked[0] = marked[1] = False` at `limit == 0` → `IndexError`),
  **337 WARNING (:108)**, **338 WARNING (:148)** (`08:00` vs `Clock(6, 45)`),
  **339 WARNING (:71)** (grader calls `personal_top_three()` first — confirmed at `drill.py:45`):
  all checked by hand and by execution, **all correct**.
- **333 `## Rules` order table (:65–70)** matches `_reference`'s EQUAL → SUPERLIST → SUBLIST →
  UNEQUAL branch order. **338 and 339 member tables** match their `_reference` classes.

### `_gen` variety — 300 draws each, independent seed (the inherited eight specifically)

```
330_pig_latin              277/300 distinct   {normal: 300}
331_protein_translation    288/300 distinct   {normal: 278, empty result: 22}
332_transpose              300/300 distinct   {normal: 300}
333_sublist                283/300 distinct   {sublist: 85, unequal: 84, superlist: 72, equal: 59}
334_prime_factors          226/300 distinct   {normal: 273, solve(1)→[]: 27}
335_nth_prime              181/300 distinct   {normal: 250, ValueError: 50}
336_sieve                  229/300 distinct   {normal: 295, limit<2→[]: 5}
337_saddle_points          269/300 distinct   {normal: 167, no saddle point: 113, ValueError: 20}
338_clock                  295/300 distinct   {normal: 300}
339_high_scores            292/300 distinct   {normal: 300}
```

Genuinely varied; both error branches and every degenerate branch are reached; 333 produces all
four verdicts in workable proportions. The report's variety claims reproduce.

### canonical cases and error messages

Every canonical literal spot-checked against the upstream test files (`6, 45` / `1723` /
`-25, -160` / `34, 37` in `clock_test.py`; `40, 20, 40, 30` and `100, 0, 90, 30` in
`high_scores_test.py`; `93819012551`; `2, 5, 3, 5`; `1000`; `FRACTURE`; `1, 0, 1`;
`UGGUGUUAUUAAUGGUUU`; `quick fast run`; `10001`) — **all present upstream**. Error messages are
verbatim:

```
nth_prime_test.py:34        err.exception.args[0] == "there is no zeroth prime"
saddle_points_test.py:97    err.exception.args[0] == "irregular matrix"
```

matching `335/drill.py:62` `match=r"^there is no zeroth prime$"` and `337/drill.py:69`
`match=r"^irregular matrix$"`. Neither message contains regex metacharacters, so the anchored
patterns are exact.

### catalogue

All ten load with 3 hints, correct topic/minutes/prereqs/tags/source; `161/161` total drills.

### class-drill shape (338, 339)

Both match `exercises/096_async_cm/` and `exercises/326_space_age/` exactly: `def solve():` with no
arguments, `raise NotImplementedError`, `import inspect` below the marker, `_reference()` returning
an equivalent class, `assert inspect.isclass(...)` as the first assertion, and the README's
`## You get` "Nothing to start — you return a **class**" + NOTE + `## You return` member-table shape
lifted from 326. Consistent.

---

## Deviations from Exercism — judged

| drill | deviation | in report? | in README? | verdict |
| --- | --- | --- | --- | --- |
| all ten | `solve(...)` instead of the Exercism function/class name | yes | yes, a `> [!NOTE]` in `## You get` | correct |
| 333 | the four constants are given with fixed values instead of chosen by the learner | yes | yes, `## You get:47` + NOTE | correct — the grader has to agree on them |
| 338 | `+`/`-` return a new `Clock`; `__eq__` compares the normalised pair, not `repr()` | yes | yes, `## Rules:136` + WARNING :150 | **keep** (concern 1), fix I-2 |
| 339 | none — `_reference` is `.meta/example.py` unchanged | — | — | confirmed by diff against the exemplar |
| 330, 337 | `_reference` is `.meta/example.py`, verbatim in structure | — | — | confirmed |

No undocumented deviation found in the inherited eight.

---

## Bottom line on the provenance warning

The second implementer's "I changed nothing in 330–337 and it all passed" is **substantially
correct**: frontmatter re-derived from `config.json` matches on all eight, fidelity is 0 changed
lines, all 116 upstream tests pass against the eight `_reference`s, all 54 README examples in the
eight evaluate correctly, `_gen` variety holds, and the canonical blocks are genuine. The one defect
that survived the audit (I-1) is a prose sentence in a WARNING — script-invisible, exactly the class
of defect batch G's review was created to catch. The second defect (I-2) is in the second
implementer's own new drill, `338_clock`.
