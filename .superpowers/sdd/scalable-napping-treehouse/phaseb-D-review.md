# Phase B — batch D review (concept exercises k=15..19, topics 245–259)

Reviewer pass over the ten uncommitted drill folders
`exercises/{245,246,247}_cater_waiter`, `{248,249}_ellens_alien_game`, `251_plane_tickets`,
`254_log_levels`, `{257,258,259}_restaurant_rozalynn`, against
`.superpowers/sdd/scalable-napping-treehouse/content-format-spec.md`,
`phase-b-exercism.md`, `/tmp/phaseb-common.md`, `/tmp/task11-common.md` and the Exercism sources
in `/tmp/exercism-python`.

**Verdict: Needs fixes.** One Important finding (Hint 2 leaks the literal solution in three
drills), plus five minor items. Everything else — fidelity, structure, data, machinery, frontmatter,
all four verification runs — is clean, and all three of the implementer's concerns are resolved in
the implementer's favour.

## Verdict per drill

| drill | verdict |
| --- | --- |
| `245_cater_waiter` | approve (minor: dead Read-first link inherited from Exercism) |
| `246_cater_waiter` | approve |
| `247_cater_waiter` | approve after Hint 2 fix (minor) |
| `248_ellens_alien_game` | approve |
| `249_ellens_alien_game` | **fix Hint 2** — it is a fenced copy of the whole solution |
| `251_plane_tickets` | approve after Hint 2 fix (minor) |
| `254_log_levels` | approve after two Read-first anchors + one Rules clause (minor) |
| `257_restaurant_rozalynn` | approve |
| `258_restaurant_rozalynn` | **fix Hint 2** — both function bodies given literally |
| `259_restaurant_rozalynn` | **fix Hint 2** — both function bodies given literally |

The unused topic numbers 250, 252, 253, 255, 256 are correct, not missing files: plane-tickets has
4 required functions and log-levels has 4 functions plus the enum, so both sit inside the ≤4
splitting rule as single drills.

---

## Rulings on the three raised concerns

### 1. `categorize_dish` signature change (247) — **accepted, and adequately documented.**

Passing `categories` as a tuple of `(name, ingredient_set)` pairs instead of importing five
constants is the right trade. `sets_categories_data.py` is 120+ lines of ingredient literals; putting
them in the learner region would bury a 6-line exercise, and none of the five constants is
*material* to the concept being drilled (the subset test is). The signature change is stated twice
in the README where the learner will actually hit it —
`exercises/247_cater_waiter/README.md:` `## You get` note ("One change to Exercism's signature:
`categorize_dish` takes the categories as a **third argument** instead of importing five constants
from `sets_categories_data.py`") and again in `## Rules` ("The `categories` tuple is already in the
order Exercism uses (vegan, vegetarian, keto, paleo, omnivore)"), and the `## You return` table
spells the parameter out. The verbatim `## Instructions` section still shows Exercism's 2-argument
form, but the `## You get` note sits directly beneath it and names the difference, which is the
contract's requirement.

Verified independently: 247's embedded `_VEGAN` and `_OMNIVORE` are **byte-equal** to Exercism's
`VEGAN` / `OMNIVORE` sets, so the two canonical examples are graded against genuine data:

```
VEGAN EQ
OMNIVORE EQ
```

### 2. plane-tickets exemplar bug (251) — **accepted; the claim checks out exactly.**

`/tmp/exercism-python/exercises/concept/plane-tickets/.meta/exemplar.py` opens `generate_seats` with

```python
number = number + 4 if number >= 13 else number
```

then skips row 13 inside the loop. Row 13 is only *reached* when the adjusted count is ≥ 49, i.e.
when the asked-for `number` is ≥ 45, so for `13 <= number < 45` nothing is ever skipped and the
generator yields `number + 4` seats — `generate_seats(13)` yields 17. `instructions.md` says only
"accepts an `int` that holds how many seats to be generated", which is unambiguous: the drill's
`_reference` (yield exactly `number`, step row 12 → 14) is the faithful reading.

Exercism's own coverage confirmed from `generators_test.py`: `test_generate_seats` uses
`test_data = [1, 2, 3, 4, 5]` and `test_generate_seats_skips_row_13` uses `test_data = [14 * 4]`
(= 56). At 1–5 nothing is adjusted; at 56 the adjusted count is 60 and exactly one row is skipped, so
both implementations produce the same 56 seats. **Every** canonical expectation is therefore ported
unchanged and none is dropped. The rule is stated in `exercises/251_plane_tickets/README.md`
`## Rules`: "asking for `number` seats gives exactly `number` seats — the skipped row does not
shorten the answer". No README note about the exemplar is needed here because Exercism's prose never
documents the buggy behaviour — there is nothing for the learner to see contradicting the grader.

### 3. restaurant-rozalynn exemplar bug (257) — **accepted; the disagreement is real and the note is present.**

`/tmp/exercism-python/exercises/concept/restaurant-rozalynn/.meta/exemplar.py`:

```python
for seat_number in range(1, len(guests)):
    seats[seat_number] = guests[seat_number]
```

which drops `guests[0]` entirely and seats the rest one place early. `none_test.py`
`test_arrange_reservations_1` encodes that:

```python
expected_results = {1: 'Frank', 2: 'Jenny', 3: 'Carol', 4: 'Alice', 5: 'George', 6: None, ...}
```

while `.docs/instructions.md` prints
`{1: 'Walter', 2: 'Frank', 3: 'Jenny', 4: 'Carol', 5: 'Alice', 6: 'George', 7: None, ...}`.
The two genuinely contradict. Following the instructions is the right call (the standing rulings
permit it, and it is the only reading that makes the exercise sensible), and this is the one place
where the learner *can* see the contradiction, because the verbatim `## Instructions` section carries
the "Walter" example. `exercises/257_restaurant_rozalynn/README.md` carries the required callout at
the end of `## Rules`:

> [!NOTE]
> Exercism's own test file for task 2 disagrees with its instructions here: the test expects the
> first guest to be dropped (`{1: 'Frank', ...}`), which is an off-by-one in Exercism's example
> solution. This drill grades the behaviour the **instructions** describe — `{1: 'Walter',
> 2: 'Frank', ...}`.

The other five canonical expectations from `none_test.py` are all ported verbatim (verified below).

---

## Other items the batch brief asked me to verify

- **246 given constants.** `ALCOHOLS` and `SPECIAL_INGREDIENTS` are in the learner region under
  `# given — do not edit: the two reference lists Exercism keeps in sets_categories_data.py`, and
  their values are set-equal to Exercism's: `ALCOHOLS src 22 drill 22 EQUAL`,
  `SPECIAL_INGREDIENTS src 85 drill 85 EQUAL`. The README's "22 spirits" / "85 allergens" counts are
  right. ✅
- **247 real data below the marker.** `_VEGAN` / `_OMNIVORE` equal Exercism's; the six `_EX*` sets
  are element-for-element Exercism's `example_dishes` (which really does contain the 30-item dish
  twice — `[_EX1, _EX2, _EX3, _EX4, _EX5, _EX5]` is not a typo); `_EXAMPLE_INTERSECTION` equals
  `EXAMPLE_INTERSECTION`; `_EXAMPLE_SINGLETONS` equals both the ground-truth "appears in exactly one
  dish" computation and the 28-element set printed in `instructions.md`. `_FOUR_OVERLAP` /
  `_FOUR_SINGLETONS` recomputed correct. ✅
- **245/246/247 canonical values.** Re-derived each drill's `_reference` against the literals parsed
  out of Exercism's own `instructions.md` blocks:
  ```
  clean_ingredients: True
  compile_ingredients: True
  separate_appetizers: True 4
  check_drinks Honeydew Cucumber True
  check_drinks Shirley Tonic True
  tag_special Ginger Glazed Tofu Cutlets -> True
  tag_special Arugula and Roasted Pork Salad -> True
  singleton_ingredients (28 items, instructions.md) -> True
  ```
  Using instructions.md instead of `sets_test.py` is correct here — that test file only zips over the
  separate 458-line `sets_test_data.py` fixture. ✅
- **254 log-levels.** `LogLevelInt` correctly not required: `.docs/hints.md` §3 says "multiple
  solutions are possible: if statements, another enum or any other solution". `enums_test.py` uses
  UPPER member names (`LogLevel.INFO`, `LogLevel.WARNING`, `LogLevel.UNKNOWN`, `LogLevel.WARN`) while
  `instructions.md` writes `LogLevel.Info` — the README pins the UPPER spelling and `UNKNOWN = "UKN"`
  in the `## You get` note and the `## Rules` table. `# noqa: PIE796` sits on `WARN = "WRN"` in
  `_reference`. ✅
- **248 `hit()` ambiguity.** Confirmed: `classes_test.py::test_alien_hit_method` carries the
  docstring "There are two valid interpretations for this method/task. `self.health -= 1` and
  `self.health = max(0, self.health - 1)`" with
  `result_data = [(2,), (1,), (0,), (0, -1), (0, -2), (0, -3)]`. The drill mirrors this exactly
  (`assert target.health in expected`) and separately pins `is_alive()` to agree
  (`assert alien.is_alive() == (alien.health > 0)`). ✅
- **249 earns its place — yes, marginally.** It is the thinnest drill in the batch, but it is the
  only drill in the whole 200-range that drills the "data from outside → objects the rest of the code
  talks to" seam, and it carries two distinct traps (tuple-into-two-parameters, and list-not-
  generator) that the grader actually checks (`isinstance(got, list)`, and the identity check
  `len({id(alien) for alien in got}) == len(positions)`). 12 minutes is the floor of the concept band
  and is fine. Keep it — but see the Important finding: as written, Hint 2 hands the learner the
  answer, which is what would actually make it worthless.
- **248/249 prereq lists.** Read from the files, not the report's abbreviated row.
  248 = `[200, 203, 206, 212, 215, 221, 227, 233, 236, 245]`; 249 = the same plus `248`. Both are the
  exact mapping of `ellens-alien-game`'s `prerequisites` (`basics, bools, comparisons, loops, dicts,
  lists, numbers, sets, strings, tuples`) through the concept→topic table, plus the previous
  sub-drill — the same convention as `213_black_jack` and `243_locomotive_engineer`. ✅

Frontmatter across the batch (all read from the files): every `minutes` is inside the 12–15 concept
band; every `tags` list is `exercism` + the concept slug + the correct section tag (`sets`,
`generators`, `enums` → `data-structures`; `classes`, `none` → `core`); every `prereqs` list matches
`config.json` `prerequisites` mapped through the table with unknowns (`comprehensions`, `sequences`,
`functions`) dropped; every `source:` line is present and correct.

---

## Findings

### Important

**I-1 · Hint 2 gives the literal solution in 249, 258 and 259** (same defect, lower intensity, in
247, 251 and 254). This is the batch F ruling ("Hint 2 must not contain the reference body written
with the drill's own parameter names") applied to concept drills, and the precedent for the fix is
commit `af68f83` on `319_sum_of_multiples`.

`exercises/249_ellens_alien_game/README.md`, `### Hint 2` — the worst case, because 249 has exactly
one function and this fence is all of it, in the drill's own parameter name:

```python
aliens = []
for position in positions:
    aliens.append(Alien(position[0], position[1]))
return aliens
```

`_reference` is `[Alien(position[0], position[1]) for position in positions]`. Nothing is left for
the learner and nothing is left for Hint 3. For calibration, Exercism's own `hints.md` §7 stops at
"A `tuple` would be a _single_ parameter. / The Alien constructor takes _2 parameters_. / Unpacking
what is _inside_ the tuple would yield two parameters." — that is the level Hint 2 should sit at.

`exercises/258_restaurant_rozalynn/README.md`, `### Hint 2` — both functions of the drill, complete,
with the drill's parameter name `seats`:

> The comprehension form is `[number for number, guest in seats.items() if guest is None]`.
> … `sum(1 for guest in seats.values() if guest is None)` does the counting in one expression.

`exercises/259_restaurant_rozalynn/README.md`, `### Hint 2` — likewise:

> `[number for number, guest in seats.items() if guest is None]` … `for index, guest in
> enumerate(guests): seats[empty[index]] = guest` … `for seat in seat_numbers: seats[seat] = None`,
> then `return seats`.

In all three, Hint 3 already does the right thing (same move, different data, fenced) — which makes
Hint 2 strictly redundant and collapses the 1→2→3 escalation the format exists for. Fix: keep the
routing and the naming of the operator/builtin, drop the working expression. Lower-intensity
instances of the same thing, worth fixing in the same pass:

- `247_cater_waiter` `### Hint 2`: `for name, ingredients in categories:` plus
  `set(dish_ingredients) <= ingredients` is the `categorize_dish` body.
- `251_plane_tickets` `### Hint 2`: `zip(passengers, generate_seats(len(passengers)))` and
  `"0" * (12 - len(base))` are the bodies of `assign_seats` and `generate_codes`.
- `254_log_levels` `### Hint 2`: `[level.value for level in LogLevel]` and
  `LogLevelInt[log_level.name].value` are lifted straight from the exemplar.

(245 and 246 are on the right side of the line — they name the operator and the shape in prose.
248's Hint 2 is close to the line but a class-definition task cannot be hinted without naming the
attributes, and Exercism's own hints already say `Alien.<class attribute name>`.)

### minor

**m-1 · `254_log_levels/README.md` `## Read first`: two anchors point at the wrong page.**
`https://docs.python.org/3/library/enum.html#using-auto` and
`.../library/enum.html#functional-api` — both fragments 404 against `library/enum.html`; they live
on `howto/enum.html` (verified: `id="using-auto"` and `id="functional-api"` both present there).
The links load, but land the reader at the top of a 155 KB page. Every other docs anchor in the
batch resolves (34/36 checked OK).

**m-2 · `245_cater_waiter/README.md` `## Read first`: dead link.**
`https://towardsdatascience.com/5-pythons-sets-problems-to-solve-before-your-coding-interview-41bb1d14ac25`
returns 404. It is inherited verbatim from `/tmp/exercism-python/concepts/sets/links.json`, so the
implementer followed the contract; still worth dropping, since a dead link in *our* section reads as
ours. (The realpython / stackoverflow / pybit.es 403–406 responses in the same lists are bot
blocking, not rot — those pages are fine.)

**m-3 · Undocumented (but correct) heading transformation in the cater-waiter Introduction.**
`/tmp/exercism-python/exercises/concept/cater-waiter/.docs/introduction.md:342` is
`# Set Symmetric Difference` — a level-1 heading where every sibling section is `##`, i.e. an
Exercism typo. All three cater-waiter READMEs demote it **two** levels to `### Set Symmetric
Difference` rather than the one level the rule specifies. This is the right call — a `##` there would
have become a top-level README section and broken the `Why · Introduction · Instructions · …`
contract — but it is a deviation from "verbatim + permitted transformations" and does not appear in
the report's deviation list. Worth one line in the report; no file change needed.

**m-4 · Consecutive blank lines collapsed throughout the verbatim sections.** Every fidelity
difference I found other than m-3 is a run of two blank lines in the Exercism source rendered as one
in the README (21 such places in the cater-waiter Introduction, 10 in the restaurant-rozalynn
Instructions, 7 in the plane-tickets Introduction, 3 in the ellens-alien-game Introduction). It is
rendering-neutral in GFM and consistent across the batch, so I am not asking for a change — but
"line for line" is the stated bar, and the controller should know this is the only systematic
departure from it. Trailing whitespace inside fences *is* preserved (39 such lines in the
cater-waiter files).

**m-5 · `254_log_levels`: the README never says WARNING must be declared before WARN.**
`## Rules` says "`WARN` is an **alias**: another name declared with the value `"WRN"`", and the
member table lists `WARNING`. A learner who writes `WARN = "WRN"` above `WARNING = "WRN"` still
passes `get_warn_alias()` (both resolve to the same object) but fails the canonical
`get_members()` assertion in `exercises/254_log_levels/drill.py`, which expects `("WARNING", "WRN")`
— and that assertion carries no message, so the failure is cryptic. One clause in `## Rules`
("declare `WARNING` first; `WARN` is the second name") closes it.

---

## Verification (run by me, not copied from the report)

**ruff** — `uv run ruff check` over all ten `drill.py`:

```
All checks passed!
```

**Stub run** — `uv run pytest exercises/245_cater_waiter … exercises/259_restaurant_rozalynn -q -p no:cacheprovider`:

```
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

**Reference run** — importlib-load each `drill.py`, `solve = _reference`, `test_solve()` under
`STUDY_SEED` 1 / 2 / 42 (30 runs):

```
245_cater_waiter           STUDY_SEED=1  test_solve() PASSED
245_cater_waiter           STUDY_SEED=2  test_solve() PASSED
245_cater_waiter           STUDY_SEED=42 test_solve() PASSED
246_cater_waiter           STUDY_SEED=1  test_solve() PASSED
246_cater_waiter           STUDY_SEED=2  test_solve() PASSED
246_cater_waiter           STUDY_SEED=42 test_solve() PASSED
247_cater_waiter           STUDY_SEED=1  test_solve() PASSED
247_cater_waiter           STUDY_SEED=2  test_solve() PASSED
247_cater_waiter           STUDY_SEED=42 test_solve() PASSED
248_ellens_alien_game      STUDY_SEED=1  test_solve() PASSED
248_ellens_alien_game      STUDY_SEED=2  test_solve() PASSED
248_ellens_alien_game      STUDY_SEED=42 test_solve() PASSED
249_ellens_alien_game      STUDY_SEED=1  test_solve() PASSED
249_ellens_alien_game      STUDY_SEED=2  test_solve() PASSED
249_ellens_alien_game      STUDY_SEED=42 test_solve() PASSED
251_plane_tickets          STUDY_SEED=1  test_solve() PASSED
251_plane_tickets          STUDY_SEED=2  test_solve() PASSED
251_plane_tickets          STUDY_SEED=42 test_solve() PASSED
254_log_levels             STUDY_SEED=1  test_solve() PASSED
254_log_levels             STUDY_SEED=2  test_solve() PASSED
254_log_levels             STUDY_SEED=42 test_solve() PASSED
257_restaurant_rozalynn    STUDY_SEED=1  test_solve() PASSED
257_restaurant_rozalynn    STUDY_SEED=2  test_solve() PASSED
257_restaurant_rozalynn    STUDY_SEED=42 test_solve() PASSED
258_restaurant_rozalynn    STUDY_SEED=1  test_solve() PASSED
258_restaurant_rozalynn    STUDY_SEED=2  test_solve() PASSED
258_restaurant_rozalynn    STUDY_SEED=42 test_solve() PASSED
259_restaurant_rozalynn    STUDY_SEED=1  test_solve() PASSED
259_restaurant_rozalynn    STUDY_SEED=2  test_solve() PASSED
259_restaurant_rozalynn    STUDY_SEED=42 test_solve() PASSED
failures: 0
```

**selfcheck**:

```
$ uv run study selfcheck
159/159 ok
```

**Catalogue**:

```
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
total in catalogue: 161
```

(`sections_ok` here = all of `## Why`, `## Introduction`, `## Instructions`, `## You get`,
`## You return`, `## Rules`, `## Exercism hints`, `## Read first` present in `spec_md`.)

**Scripted verbatim-fidelity diff** — README `## Introduction` / `## Instructions` /
`## Exercism hints` vs the Exercism source with only the permitted transformations applied
(top `#` dropped, headings demoted outside fences, `~~~~exercism/note` → `> [!NOTE]` blockquote,
`<br>` dropped, trailing whitespace ignored):

```
245_cater_waiter           Introduction     src= 420 readme= 400 changed_lines=21
245_cater_waiter           Instructions     src= 141 readme= 139 changed_lines=2
245_cater_waiter           Exercism hints   src=  61 readme=  60 changed_lines=1
246_cater_waiter           Introduction     src= 420 readme= 400 changed_lines=21
246_cater_waiter           Instructions     src= 141 readme= 139 changed_lines=2
246_cater_waiter           Exercism hints   src=  61 readme=  60 changed_lines=1
247_cater_waiter           Introduction     src= 420 readme= 400 changed_lines=21
247_cater_waiter           Instructions     src= 141 readme= 139 changed_lines=2
247_cater_waiter           Exercism hints   src=  61 readme=  60 changed_lines=1
248_ellens_alien_game      Introduction     src= 267 readme= 264 changed_lines=3
248_ellens_alien_game      Instructions     src= 124 readme= 123 changed_lines=1
248_ellens_alien_game      Exercism hints   src=  40 readme=  40 changed_lines=0
249_ellens_alien_game      Introduction     src= 267 readme= 264 changed_lines=3
249_ellens_alien_game      Instructions     src= 124 readme= 123 changed_lines=1
249_ellens_alien_game      Exercism hints   src=  40 readme=  40 changed_lines=0
251_plane_tickets          Introduction     src= 144 readme= 137 changed_lines=7
251_plane_tickets          Instructions     src=  93 readme=  93 changed_lines=0
251_plane_tickets          Exercism hints   src=  22 readme=  22 changed_lines=0
254_log_levels             Introduction     src=  63 readme=  63 changed_lines=0
254_log_levels             Instructions     src=  85 readme=  85 changed_lines=0
254_log_levels             Exercism hints   src=  31 readme=  31 changed_lines=0
257_restaurant_rozalynn    Introduction     src=  27 readme=  27 changed_lines=0
257_restaurant_rozalynn    Instructions     src= 100 readme=  90 changed_lines=10
257_restaurant_rozalynn    Exercism hints   src=  27 readme=  27 changed_lines=0
258_restaurant_rozalynn    Introduction     src=  27 readme=  27 changed_lines=0
258_restaurant_rozalynn    Instructions     src= 100 readme=  90 changed_lines=10
258_restaurant_rozalynn    Exercism hints   src=  27 readme=  27 changed_lines=0
259_restaurant_rozalynn    Introduction     src=  27 readme=  27 changed_lines=0
259_restaurant_rozalynn    Instructions     src= 100 readme=  90 changed_lines=10
259_restaurant_rozalynn    Exercism hints   src=  27 readme=  27 changed_lines=0
```

Every non-zero count above was inspected line by line: **all of them are collapsed double blank
lines (m-4), except the single `# Set Symmetric Difference` heading (m-3)**. Effective content
fidelity is 0 changed lines across all thirty sections. In particular there is **no** batch F
regression — no `# comment` inside a ```python fence was demoted into a heading anywhere in the
batch; if one had been, it would have shown up as a diff here.

**Scripted structural pass** (fence balance counting inside blockquotes, `#` count, section order,
attribution lines, hint block, raw HTML outside code spans):

```
== 245_cater_waiter … == 259_restaurant_rozalynn   (all ten identical)
   fence_balance_ok=True h1_count=1 attribution_lines=1 hint_headings=3 hints_blocks=1
   sections=['Why', 'Introduction', 'Instructions', 'You get', 'You return', 'Rules',
             'Exercism hints', 'Read first', 'Hints']
   order_ok=True
   nothing after Hint 3
   no raw HTML outside code spans
```

**drill.py shape** (AST):

```
245_cater_waiter           moddoc=None solvedoc=None stub=True
246_cater_waiter           moddoc=None solvedoc=None stub=True
247_cater_waiter           moddoc=None solvedoc=None stub=True
248_ellens_alien_game      moddoc=None solvedoc=None stub=True
249_ellens_alien_game      moddoc=None solvedoc=None stub=True   (given `Alien` class above solve)
251_plane_tickets          moddoc=None solvedoc=None stub=True
254_log_levels             moddoc=None solvedoc=None stub=True
257_restaurant_rozalynn    moddoc=None solvedoc=None stub=True
258_restaurant_rozalynn    moddoc=None solvedoc=None stub=True
259_restaurant_rozalynn    moddoc=None solvedoc=None stub=True
```

**Marker line** — byte-compared against `exercises/303_bob/drill.py`:

```
245_cater_waiter count=1 OK      248_ellens_alien_game count=1 OK   254_log_levels count=1 OK
246_cater_waiter count=1 OK      249_ellens_alien_game count=1 OK   257_restaurant_rozalynn count=1 OK
247_cater_waiter count=1 OK      251_plane_tickets count=1 OK       258_restaurant_rozalynn count=1 OK
                                                                    259_restaurant_rozalynn count=1 OK
```

**`_gen` variety and canonical counts** — read individually, all pass:
245 (5–16 ingredients with injected duplicates, 0–5 dishes, 4–10 menu names, 1–6 appetizers; 6
generated + 5 canonical) · 246 (alcohol injected 50 % of the time, ingredients as list *or* set; 6 +
5) · 247 (five randomly-sized category sets with a guaranteed-fitting dish, 2–6 dishes with a
correctly derived `overlapping`; 6 + 5) · 248 (random coordinates and 1–6 hits, exercising the
clamp/negative fork; 5 generated + a full canonical block) · 249 (0–6 positions, duplicates injected
40 % of the time; 6 + 4) · 251 (`seat_count` deliberately drawn from the 1–12 / 13–60 / multiple-of-4
regimes; 6 + 6) · 254 (25 % bogus level codes, all seven member names; 6 + 8) · 257 (`guests` is
`None` / `[]` / a real list; 6 + 5) · 258 (**seeds `0` and `""` into the chart** so a truthiness test
fails and only `is None` passes — nice; 6 + 5) · 259 (walk-in count drawn around the exact capacity
boundary so both the fits and does-not-fit branches fire; 6 + 4). No drill in this batch raises, so
there are no `pytest.raises(..., match=...)` patterns to check.
