# Phase B — batch C report (concept exercises k=10..14, topics 230–244)

Nine drill folders written under `exercises/`. Nothing outside them was touched; no git state changed.

## Drills

| topic | folder | title | tags | prereqs | minutes | Exercism tasks |
|---|---|---|---|---|---|---|
| 230 | `230_pretty_leaflet` | string-formatting — Erin's event leaflet | `[exercism, string-formatting, core]` | `[215, 221, 227]` | 15 | 1–4 (all) |
| 233 | `233_tisbury_treasure_hunt` | tuples — reading the treasure coordinates | `[exercism, tuples, core]` | `[203, 206, 209, 227]` | 12 | 1–2 |
| 234 | `234_tisbury_treasure_hunt` | tuples — matching records and printing the report | `[exercism, tuples, core]` | `[203, 206, 209, 227, 233]` | 15 | 3–5 |
| 236 | `236_inventory_management` | dicts — building and topping up an inventory | `[exercism, dicts, data-structures]` | `[221, 227, 233]` | 14 | 1–3 |
| 237 | `237_inventory_management` | dicts — removing items and reporting stock | `[exercism, dicts, data-structures]` | `[221, 227, 233, 236]` | 12 | 4–5 |
| 239 | `239_mecha_munch_management` | dict-methods — filling the shopping cart | `[exercism, dict-methods, data-structures]` | `[236]` | 14 | 1–3 |
| 240 | `240_mecha_munch_management` | dict-methods — sorting the cart and updating the shelves | `[exercism, dict-methods, data-structures]` | `[236, 239]` | 15 | 4–6 |
| 242 | `242_locomotive_engineer` | unpacking-and-multiple-assignment — packing and reordering wagons | `[exercism, unpacking-and-multiple-assignment, core]` | `[221, 227, 233, 236]` | 13 | 1–2 |
| 243 | `243_locomotive_engineer` | unpacking-and-multiple-assignment — routes and the wagon depot grid | `[exercism, unpacking-and-multiple-assignment, core]` | `[221, 227, 233, 236, 242]` | 15 | 3–5 |

Splitting: `pretty-leaflet` has exactly 4 required functions, so it stays one drill (topics 231–232 unused,
as are 235, 238, 241, 244). The other four exercises have 5 or 6 functions and are split in two, grouped by
sub-concept: extract/convert vs. compare/combine/report (tisbury); build/increment/decrement vs. delete/report
(inventory); `setdefault`/`fromkeys`/`update` vs. views + `sorted()` (mecha-munch); `*` packing/unpacking vs.
`**` packing/merging + `zip(*rows)` (locomotive). Prereqs use the concept→first-sub-drill map from the common
instructions; each `i>0` sub-drill also lists its `i-1` topic. Section tags: `dicts`/`dict-methods` →
`data-structures`, the rest → `core`.

All nine are multi-function drills, so `solve()` takes no arguments and returns `{"name": fn, ...}`;
`_reference()` returns the same dict; `test_solve()` calls `solve()[name](...)`.

## Deviations from the sources

- **`~~~~exercism/note` / `~~~~exercism/caution`** blocks (locomotive-engineer introduction and instructions)
  became `> [!NOTE]` / `> [!WARNING]` callouts, per the common instructions. Content unchanged.
- **Heading demotion**: the leading H1 of every `introduction.md` / `instructions.md` / `hints.md` is dropped
  and the remaining headings are shifted so the shallowest becomes `###`. `pretty-leaflet`'s introduction uses
  three H1s (`# string-formatting`, `# literal string interpolation. f-string`, `# str.format() method`); the
  first is the document title and was dropped, the other two became `###`.
- **Raw HTML in `tisbury-treasure-hunt/instructions.md`**: the two Markdown tables are wrapped in an HTML
  `<table>/<tr>/<td>` layout, which the format spec forbids. The wrapper tags and `<br>` were dropped and the
  header cell text kept as the bold labels `**Azara's List**` and `**Rui's List**` above the two tables. Every
  other line of the file is verbatim (verified line-by-line against the source, see below).
- **`240_mecha_munch_management` `_reference`**: the exemplar's `for key in cart.keys():` was written as
  `for key, quantity in cart.items():` — ruff `SIM118` rejects the exemplar form. Same behaviour.
- **`230_pretty_leaflet` `_reference`**: the exemplar's `'{} {}, {}'.format(...)` and `'{}'.format(icon)`
  were written as f-strings (the exemplar carries `# pylint: disable=consider-using-f-string` on both).
  `calendar.month_name` is kept, as in the exemplar. Same behaviour.
- Exemplars and `instructions.md` agreed everywhere else; no case of implementing the instructions over the
  exemplar.

## Notes on the generated cases

- `_gen` varies sizes and values, not rules: leaflets get 1–4 artists with 0..n icons and an optional date
  (the "fewer icons than artists" and "no date" branches are both exercised); inventories/carts vary in size
  and in which items overlap; tisbury coordinates match about half the time; the locomotive train varies in
  length and the missing-wagon list may be empty.
- Functions that mutate their argument (`add_items`, `decrement_items`, `remove_item`, `add_item`,
  `update_recipes`, `update_store_inventory`, `fix_wagon_depot`) are called on `deepcopy`-ed inputs so
  `solve` and `_reference` each see fresh data.
- `sort_entries` and `send_to_store` are compared as `list(result.items())`, because two dicts with the same
  entries in different orders compare equal — the Exercism tests use `OrderedDict` for the same reason.

## Verification

```
$ uv run ruff check exercises/230_pretty_leaflet/drill.py exercises/233_tisbury_treasure_hunt/drill.py \
    exercises/234_tisbury_treasure_hunt/drill.py exercises/236_inventory_management/drill.py \
    exercises/237_inventory_management/drill.py exercises/239_mecha_munch_management/drill.py \
    exercises/240_mecha_munch_management/drill.py exercises/242_locomotive_engineer/drill.py \
    exercises/243_locomotive_engineer/drill.py
All checks passed!
```

Stub run, one per drill (`uv run pytest exercises/<slug> -q -p no:cacheprovider`):

```
exercises/230_pretty_leaflet/drill.py:2: NotImplementedError
FAILED exercises/230_pretty_leaflet/drill.py::test_solve - NotImplementedError
1 failed in 0.07s
exercises/233_tisbury_treasure_hunt/drill.py:2: NotImplementedError
FAILED exercises/233_tisbury_treasure_hunt/drill.py::test_solve - NotImplemen...
1 failed in 0.05s
exercises/234_tisbury_treasure_hunt/drill.py:2: NotImplementedError
FAILED exercises/234_tisbury_treasure_hunt/drill.py::test_solve - NotImplemen...
1 failed in 0.06s
exercises/236_inventory_management/drill.py:2: NotImplementedError
FAILED exercises/236_inventory_management/drill.py::test_solve - NotImplement...
1 failed in 0.06s
exercises/237_inventory_management/drill.py:2: NotImplementedError
FAILED exercises/237_inventory_management/drill.py::test_solve - NotImplement...
1 failed in 0.06s
exercises/239_mecha_munch_management/drill.py:2: NotImplementedError
FAILED exercises/239_mecha_munch_management/drill.py::test_solve - NotImpleme...
1 failed in 0.06s
exercises/240_mecha_munch_management/drill.py:2: NotImplementedError
FAILED exercises/240_mecha_munch_management/drill.py::test_solve - NotImpleme...
1 failed in 0.06s
exercises/242_locomotive_engineer/drill.py:2: NotImplementedError
FAILED exercises/242_locomotive_engineer/drill.py::test_solve - NotImplemente...
1 failed in 0.06s
exercises/243_locomotive_engineer/drill.py:2: NotImplementedError
FAILED exercises/243_locomotive_engineer/drill.py::test_solve - NotImplemente...
1 failed in 0.06s
```

Reference run (importlib, `solve = _reference`, `STUDY_SEED` 1 / 2 / 42):

```
$ uv run python /tmp/refrun.py 230_pretty_leaflet 233_tisbury_treasure_hunt 234_tisbury_treasure_hunt \
    236_inventory_management 237_inventory_management 239_mecha_munch_management \
    240_mecha_munch_management 242_locomotive_engineer 243_locomotive_engineer
230_pretty_leaflet seed=1 OK
230_pretty_leaflet seed=2 OK
230_pretty_leaflet seed=42 OK
233_tisbury_treasure_hunt seed=1 OK
233_tisbury_treasure_hunt seed=2 OK
233_tisbury_treasure_hunt seed=42 OK
234_tisbury_treasure_hunt seed=1 OK
234_tisbury_treasure_hunt seed=2 OK
234_tisbury_treasure_hunt seed=42 OK
236_inventory_management seed=1 OK
236_inventory_management seed=2 OK
236_inventory_management seed=42 OK
237_inventory_management seed=1 OK
237_inventory_management seed=2 OK
237_inventory_management seed=42 OK
239_mecha_munch_management seed=1 OK
239_mecha_munch_management seed=2 OK
239_mecha_munch_management seed=42 OK
240_mecha_munch_management seed=1 OK
240_mecha_munch_management seed=2 OK
240_mecha_munch_management seed=42 OK
242_locomotive_engineer seed=1 OK
242_locomotive_engineer seed=2 OK
242_locomotive_engineer seed=42 OK
243_locomotive_engineer seed=1 OK
243_locomotive_engineer seed=2 OK
243_locomotive_engineer seed=42 OK
```

```
$ uv run study selfcheck
131/131 ok
```

(131, not 104 — batches B/F and others had already landed their folders when this ran. All nine batch C
drills are in the ok set; the catalogue check below reads them back.)

Catalogue:

```
$ uv run python -c "from study.catalogue import exercises; ..."
230_pretty_leaflet               topic=230 minutes=15 prereqs=[215, 221, 227] tags=['exercism', 'string-formatting', 'core'] hints=3 why=True
233_tisbury_treasure_hunt        topic=233 minutes=12 prereqs=[203, 206, 209, 227] tags=['exercism', 'tuples', 'core'] hints=3 why=True
234_tisbury_treasure_hunt        topic=234 minutes=15 prereqs=[203, 206, 209, 227, 233] tags=['exercism', 'tuples', 'core'] hints=3 why=True
236_inventory_management         topic=236 minutes=14 prereqs=[221, 227, 233] tags=['exercism', 'dicts', 'data-structures'] hints=3 why=True
237_inventory_management         topic=237 minutes=12 prereqs=[221, 227, 233, 236] tags=['exercism', 'dicts', 'data-structures'] hints=3 why=True
239_mecha_munch_management       topic=239 minutes=14 prereqs=[236] tags=['exercism', 'dict-methods', 'data-structures'] hints=3 why=True
240_mecha_munch_management       topic=240 minutes=15 prereqs=[236, 239] tags=['exercism', 'dict-methods', 'data-structures'] hints=3 why=True
242_locomotive_engineer          topic=242 minutes=13 prereqs=[221, 227, 233, 236] tags=['exercism', 'unpacking-and-multiple-assignment', 'core'] hints=3 why=True
243_locomotive_engineer          topic=243 minutes=15 prereqs=[221, 227, 233, 236, 242] tags=['exercism', 'unpacking-and-multiple-assignment', 'core'] hints=3 why=True
```

Extra checks run (not required, but they caught things):

- **Marker line byte-identical to `exercises/303_bob/drill.py`** — all nine OK.
- **Fences balanced, no raw HTML, section order** — all nine: even fence count, zero `<table>/<tr>/<td>/<br>/<div>`
  matches, headings in the order `Why · Introduction · Instructions · You get · You return · Rules ·
  Exercism hints · Read first · Hints`, exactly three `### Hint N`, nothing after Hint 3.
- **Verbatim check**: every non-blank line of each source `introduction.md` / `instructions.md` / `hints.md`
  (minus the dropped H1) appears in the corresponding README section, and the only lines the README adds are
  the callout markers and the two tisbury table labels listed under Deviations.
- **Every `# ->` example in the hints and in `## You return` was executed** and its printed output pasted back
  into the README (receipt box, parcel manifest, status tally, feature flags, `dict.fromkeys`/`update`,
  seat sell-out, header-row reorder, server tags + transpose).

## Concerns

- `230_pretty_leaflet` is Exercism `status: "wip"` in `config.json` (the others are `beta`). Its
  `instructions.md` is inconsistent with its own tests in two places, and I followed the **tests + exemplar**:
  task 1 says "create the class" and task 2 shows `convert_date(...)` / `leaflet.set_date(...)` method calls,
  but the test file imports four plain module-level functions (`capitalize_header`, `format_date`,
  `display_icons`, `print_leaflet`) and there is no class anywhere. The README carries Exercism's wording
  verbatim as instructed, so a learner reads "method"/"class" in `## Instructions` and "function" in
  `## You get`; the `## You get` note and the `## Rules` list are explicit about which is binding.
- `230`'s leaflet rows are 20 columns wide *on screen* but the artist rows are 19 Python characters when they
  carry an emoji (one code point, two terminal columns). The tests compare exact strings, so this is correct —
  the README's `> [!WARNING]` calls it out so it does not read as an off-by-one bug.
- `_reference` for `format_date` uses `calendar.month_name`, which is locale-sensitive in principle. CPython
  does not call `setlocale` at startup, so it is English under the default "C" locale, and the canonical
  `February 21, 2021` case pins it. Worth knowing if the grader ever runs under an explicit locale.
- Topics 231–232, 235, 238, 241 and 244 are unused; the batch reserved three topics per exercise and only one
  or two were needed.
