---
title: tuples — matching records and printing the report
difficulty: medium
tier: core
minutes: 15
prereqs: [23]
tags: [tuples]
source: exercism/python concept/tisbury-treasure-hunt (MIT, adapted)
---
# tuples — matching records and printing the report

*Membership, concatenation, and formatting tuples into a report.*

## Read first
- [tuple](https://devdocs.io/python~3.14/library/stdtypes#tuple) — the constructor and the literal, and why a one-element tuple needs its trailing comma
- [Sequence types — list, tuple, range](https://devdocs.io/python~3.14/library/stdtypes#sequence-types-list-tuple-range) — where tuples sit among Python's sequences
- [Common sequence operations](https://devdocs.io/python~3.14/library/stdtypes#common-sequence-operations) — indexing, `in`, `+` and `*`, all shared with strings and lists
- [Ned Batchelder: Lists vs Tuples](https://nedbatchelder.com/blog/201608/lists_vs_tuples.html) — the useful mental model: a list is a collection, a tuple is a record
- [Stack Overflow: what's the difference between lists and tuples?](https://stackoverflow.com/a/626871) — the short answer
- [James Tauber: tuples are not just constant lists](https://jtauber.com/blog/2006/04/15/python_tuples_are_not_just_constant_lists/) — why position means something in a tuple and nothing in a list
- [hashable](https://devdocs.io/python~3.14/glossary#term-hashable) — the property that lets a tuple be a dict key when a list cannot be
- [Membership test operations](https://devdocs.io/python~3.14/reference/expressions#membership-test-operations) — what `in` actually checks when the right-hand side is a tuple
- [f-strings](https://devdocs.io/python~3.14/reference/lexical_analysis#f-strings) — how a tuple gets rendered when you drop it into `{}`

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
Azara's treasures and Rui's locations can now be read in the same shape, so the hunt itself can start: does this treasure sit at that location, and if it does, what does the merged record look like? At the end the pair want one printable report — one line per find, with the duplicated coordinate dropped. That is the tail end of every reconciliation job: compare two feeds, join the rows that agree, and hand a human something readable.

## You get
Nothing. The records arrive as arguments to your functions.

> [!NOTE]
> Exercism asks for five functions in one `tuples.py`. Here the task is split in two: tasks 1–2 are task `023_tisbury_treasure_hunt`, and **this task covers tasks 3–5**. And there is one entry point: `solve()` takes **no arguments** and returns a dict that hands your three functions to the grader, keyed by name. Nothing stops you from writing your own coordinate-conversion helper and calling it from all three.

## You return
A dict with these three functions.

| key | parameters | returns |
| --- | --- | --- |
| `"compare_records"` | `azara_record` — a `(treasure, coordinate)` pair; `rui_record` — a `(location, coordinate, quadrant)` trio | `True` if the two coordinates describe the same square, `False` otherwise |
| `"create_record"` | the same two records | the two records joined into one flat five-item tuple when they match, or the string `"not a match"` when they do not |
| `"clean_up"` | `combined_record_group` — a tuple of the five-item records | one multi-line string: each record with its duplicated coordinate dropped, one per line |

```python
hunt = solve()
hunt["compare_records"](('Brass Spyglass', '4B'),
                        ('Seaside Cottages', ('1', 'C'), 'Blue'))
# -> False
hunt["create_record"](('Brass Spyglass', '4B'),
                      ('Abandoned Lighthouse', ('4', 'B'), 'Blue'))
# -> ('Brass Spyglass', '4B', 'Abandoned Lighthouse', ('4', 'B'), 'Blue')
hunt["create_record"](('Brass Spyglass', '4B'),
                      ('Seaside Cottages', ('1', 'C'), 'blue'))
# -> 'not a match'
hunt["clean_up"](
    (('Brass Spyglass', '4B', 'Abandoned Lighthouse', ('4', 'B'), 'Blue'),
     ('Crystal Crab', '6A', 'Old Schooner', ('6', 'A'), 'Purple')))
# -> "('Brass Spyglass', 'Abandoned Lighthouse', ('4', 'B'), 'Blue')\n('Crystal Crab', 'Old Schooner', ('6', 'A'), 'Purple')\n"
```

## Rules
- this task implements **Exercism tasks 3, 4 and 5 only** — `get_coordinate` and `convert_coordinate` belong to task `023_tisbury_treasure_hunt`
- `compare_records` returns the booleans `True` / `False`, not a truthy value of some other type
- a matched `create_record` result is **one flat tuple of five items**, not a tuple containing two tuples
- when the coordinates disagree, `create_record` returns exactly the string `"not a match"` — lower case, one space either side of "a"
- `clean_up` keeps the records in the order it was given them, and drops **Azara's** coordinate (the `'4B'` string), keeping Rui's `('4', 'B')` tuple
- each cleaned record is rendered the way Python prints a tuple — parentheses, single quotes, `, ` between items

> [!WARNING]
> Every line of the report ends with `\n`, **including the last one**, so the returned string finishes with a newline. Forgetting it is the usual way this test fails.

## Hints
### Hint 1
All three functions rest on the one small conversion from the previous task: Azara's `'4B'` has to become `('4', 'B')` before it can be compared with anything of Rui's. Once it is in that shape, task 3 is a single [membership test](https://devdocs.io/python~3.14/reference/expressions#membership-test-operations) — Rui's record *is* a tuple, and `in` asks whether a value is one of its elements.
### Hint 2
Task 4 is task 3 plus one sequence operation: two tuples joined with `+` produce a single flat tuple, which is exactly the five-item record being asked for. Call your own comparison function rather than repeating the comparison — that is what "could you re-use `compare_records`?" in the Exercism hints is pointing at.

Task 5 loops over the outer tuple and, for each inner record, picks the four items it keeps by index. You do not have to build the text of a tuple yourself: formatting a tuple gives you Python's own rendering, parentheses and quotes included. Append each line to the report as you go, and remember the newline belongs on **every** line.
### Hint 3
Different data, same shape. A parcel manifest, where the scan already carries the bay as a tuple:

```python
scans = (('P-991', 'HUB-3', ('B', '12'), 'night'),
         ('P-704', 'HUB-1', ('A', '02'), 'day'))
report = ""
for parcel, _hub, bay, shift in scans:
    report += f"{(parcel, bay, shift)}\n"
```

`report` is now:

```text
('P-991', ('B', '12'), 'night')
('P-704', ('A', '02'), 'day')
```

Note that nothing in that loop writes a parenthesis or a quote — the f-string renders the tuple for you.
