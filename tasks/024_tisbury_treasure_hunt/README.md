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

## Introduction
In Python, a [tuple][tuple] is an _immutable_ collection of items in _sequence_.
Like most collections, `tuples` can hold any (or multiple) data type(s) -- including other `tuples`.
Tuples support all [common sequence operations][common sequence operations], but **do not** support [mutable sequence operations][mutable sequence operations].

The elements of a tuple can be iterated over using the `for item in <tuple>` construct.
If both element index and value are needed, `for index, item in enumerate(<tuple>)` can be used.
Like any sequence, elements within `tuples` can be accessed via _bracket notation_ using a `0-based index` number from the left or a `-1-based index` number from the right.
Tuples can also be copied in whole or in part using slice notation (_`<tuple>[<start>:<stop>:<step>]`_).

### Tuple Construction

Tuples can be formed in multiple ways, using either the `tuple(<iterable>)` class constructor or the `tuple` literal declaration.

#### Using the `tuple()` constructor empty or with an _iterable_:

```python
>>> no_elements = tuple()
()

# The constructor *requires* an iterable, so single elements must be passed in a list or another tuple.
>>> one_element = tuple([16])
(16,)
```

Strings are iterable, so using a single `str` as an argument to the `tuple()` constructor can have surprising results:

```python
# String elements (characters) are iterated through and added to the tuple
>>> multiple_elements_string = tuple("Timbuktu")
('T', 'i', 'm', 'b', 'u', 'k', 't', 'u')
```

Single iterables have their elements added one by one:

```python
>>> multiple_elements_list = tuple(["Parrot", "Bird", 334782])
("Parrot", "Bird", 334782)

>>> multiple_elements_set = tuple({2, 3, 5, 7, 11})
(2,3,5,7,11)
```

##### Declaring a tuple as a _literal_ :

Because the `tuple(<iterable>)` constructor only takes _iterables_ (or nothing) as arguments, it is much easier to create
 a one-tuple via the literal method.

```python
>>> no_elements = ()
()

>>> one_element = ("Guava",)
("Guava",)
```

Nested data structures can be included as `tuple` elements, including other `tuples`:

```python
>>> nested_data_structures = ({"fish": "gold", "monkey": "brown", "parrot" : "grey"}, ("fish", "mammal", "bird"))
({"fish": "gold", "monkey": "brown", "parrot" : "grey"}, ("fish", "mammal", "bird"))

>>> nested_data_structures_1 = (["fish", "gold", "monkey", "brown", "parrot", "grey"], ("fish", "mammal", "bird"))
(["fish", "gold", "monkey", "brown", "parrot", "grey"], ("fish", "mammal", "bird"))
```

### Tuple Concatenation

Tuples can be concatenated using plus `+` operator, which unpacks each `tuple` creating a new, combined `tuple`.

```python
>>> new_via_concatenate = ("George", 5) + ("cat", "Tabby")
("George", 5, "cat", "Tabby")

#likewise, using the multiplication operator * is the equivalent of using + n times
>>> first_group = ("cat", "dog", "elephant")

>>> multiplied_group = first_group * 3
('cat', 'dog', 'elephant', 'cat', 'dog', 'elephant', 'cat', 'dog', 'elephant')
```

### Accessing Elements Inside a Tuple

Elements within a `tuple` can be accessed via _bracket notation_ using a `0-based index` number from the left or a `-1-based index` number from the right.

```python
student_info = ("Alyssa", "grade 3", "female", 8 )

#gender is at index 2 or index -2
>>> student_gender = student_info[2]
'female'

>>> student_gender = student_info[-2]
'female'

#name is at index 0 or index -4
>>> student_name = student_info[0]
Alyssa

>>> student_name = student_info[-4]
Alyssa
```

### Iterating Over a Tuples Elements

Elements inside a `tuple` can be _iterated over_ in a loop using `for item in <tuple>` syntax.
If both indexes and values are needed, `for index, item in enumerate(<tuple>)` can be used.

```python
>>> student_info = ("Alyssa", "grade 3", "female", 8 )
>>> for item in student_info:
...   print(item)

...
Alyssa
grade 3
female
8

>>> for index, item in enumerate(student_info):
...  print("Index is: " + str(index) + ", value is: " + str(item) +".")

...
Index is: 0, value is: Alyssa.
Index is: 1, value is: grade 3.
Index is: 2, value is: female.
Index is: 3, value is: 8.
```

### Checking Membership in a Tuple

The `in` operator can be used to check membership in a `tuple`.

```python
>>> multiple_elements_list = tuple(["Parrot", "Bird", 334782])
("Parrot", "Bird", 334782)

>>> "Parrot" in multiple_elements_list
True
```

[common sequence operations]: https://devdocs.io/python~3.14/library/stdtypes#common-sequence-operations
[mutable sequence operations]: https://devdocs.io/python~3.14/library/stdtypes#mutable-sequence-types
[tuple]: https://devdocs.io/python~3.14/library/stdtypes#tuple

## Instructions
Azara and Rui are teammates competing in a pirate-themed treasure hunt.
One has a list of treasures with map coordinates, the other a list of location names with map coordinates.
They've also been given blank maps with a starting place marked YOU ARE HERE.

**Azara's List**

| Treasure                    | Coordinates |
| --------------------------- | ----------- |
| Amethyst Octopus            | 1F          |
| Angry Monkey Figurine       | 5B          |
| Antique Glass Fishnet Float | 3D          |
| Brass Spyglass              | 4B          |
| Carved Wooden Elephant      | 8C          |
| Crystal Crab                | 6A          |
| Glass Starfish              | 6D          |
| Model Ship in Large Bottle  | 8A          |
| Pirate Flag                 | 7F          |
| Robot Parrot                | 1C          |
| Scrimshawed Whale Tooth     | 2A          |
| Silver Seahorse             | 4E          |
| Vintage Pirate Hat          | 7E          |

**Rui's List**

| Location Name                         | Coordinates | Quadrant  |
| ------------------------------------- | ----------- | --------- |
| Seaside Cottages                      | ("1", "C")  | Blue      |
| Aqua Lagoon (Island of Mystery)       | ("1", "F")  | Yellow    |
| Deserted Docks                        | ("2", "A")  | Blue      |
| Spiky Rocks                           | ("3", "D")  | Yellow    |
| Abandoned Lighthouse                  | ("4", "B")  | Blue      |
| Hidden Spring (Island of Mystery)     | ("4", "E")  | Yellow    |
| Stormy Breakwater                     | ("5", "B")  | Purple    |
| Old Schooner                          | ("6", "A")  | Purple    |
| Tangled Seaweed Patch                 | ("6", "D")  | Orange    |
| Quiet Inlet (Island of Mystery)       | ("7", "E")  | Orange    |
| Windswept Hilltop (Island of Mystery) | ("7", "F")  | Orange    |
| Harbor Managers Office                | ("8", "A")  | Purple    |
| Foggy Seacave                         | ("8", "C")  | Purple    |

But things are a bit disorganized: Azara's coordinates appear to be formatted and sorted differently from Rui's, and they have to keep looking from one list to the other to figure out which treasures go with which locations.
Being budding pythonistas, they have come to you for help in writing a small program (a set of functions, really) to better organize their hunt information.

### 1. Extract coordinates

Implement the `get_coordinate()` function that takes a `(treasure, coordinate)` pair from Azara's list and returns only the extracted map coordinate.

```python
>>> get_coordinate(('Scrimshawed Whale Tooth', '2A'))
2A
```

### 2. Format coordinates

Implement the `convert_coordinate()` function that takes a coordinate in the format "2A" and returns a tuple in the format `("2", "A")`.

```python
>>> convert_coordinate("2A")
("2", "A")
```

### 3. Match coordinates

Implement the `compare_records()` function that takes a `(treasure, coordinate)` pair and a `(location, coordinate, quadrant)` record and compares coordinates from each.
Return **`True`** if the coordinates "match", and return **`False`** if they do not.
Re-format coordinates as needed for accurate comparison.

```python
>>> compare_records(('Brass Spyglass', '4B'), ('Seaside Cottages', ('1', 'C'), 'blue'))
False

>>> compare_records(('Model Ship in Large Bottle', '8A'), ('Harbor Managers Office', ('8', 'A'), 'purple'))
True
```

### 4. Combine matched records

Implement the `create_record()` function that takes a `(treasure, coordinate)` pair from Azara's list and a `(location, coordinate, quadrant)` record from Rui's list and returns `(treasure, coordinate, location, coordinate, quadrant)` **if the coordinates match**.
If the coordinates _do not_ match, return the string **"not a match"**.
Re-format the coordinate as needed for accurate comparison.

```python
>>> create_record(('Brass Spyglass', '4B'), ('Abandoned Lighthouse', ('4', 'B'), 'Blue'))
('Brass Spyglass', '4B', 'Abandoned Lighthouse', ('4', 'B'), 'Blue')

>>> create_record(('Brass Spyglass', '4B'), ('Seaside Cottages', ('1', 'C'), 'blue'))
"not a match"
```

### 5. "Clean up" & make a report of all records

Clean up the combined records from Azara and Rui so that there's only one set of coordinates per record. Make a report so they can see one list of everything they need to put on their maps.
Implement the `clean_up()` function that takes a tuple of tuples (_everything from both lists_), looping through the _outer_ tuple, dropping the unwanted coordinates from each _inner_ tuple and adding each to a 'report'.
Format and return the 'report' so that there is one cleaned record on each line.

```python
>>> clean_up((('Brass Spyglass', '4B', 'Abandoned Lighthouse', ('4', 'B'), 'Blue'), ('Vintage Pirate Hat', '7E', 'Quiet Inlet (Island of Mystery)', ('7', 'E'), 'Orange'), ('Crystal Crab', '6A', 'Old Schooner', ('6', 'A'), 'Purple')))

"""
('Brass Spyglass', 'Abandoned Lighthouse', ('4', 'B'), 'Blue')\n
('Vintage Pirate Hat', 'Quiet Inlet (Island of Mystery)', ('7', 'E'), 'Orange')\n
('Crystal Crab', 'Old Schooner', ('6', 'A'), 'Purple')\n
"""
```

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

## Exercism hints
### General

- [Tuples][tuples] are immutable [sequence types][sequence types] that can contain any data type.
- Tuples are [iterable][iterable].  If you need indexes as well as values, use [`enumerate()`][enumerate]
- Elements within tuples can be accessed via [bracket notation][bracket notation], using a zero-based index from the left, or -1 from the right. Other [Common Sequence Operations][common sequence operations] can also be used when working with tuples.

### 1. Extract coordinates

- Remember: tuples allow access via _index_, using _brackets_. Indexes start from the left at zero.

### 2. Format coordinates

- Check [`class tuple`][class tuple] for more details on tuples.
- Check [`class str`][class str] for more details on strings.

### 3. Match coordinates

- What methods could be used here for for [testing membership][testing membership]?.
- Check [`class tuple`][class tuple] for more details on tuples.
- Could you re-use your `convert_coordinate()` function?

### 4. Combine matched records

- Remember that tuples support all [common sequence operations][common sequence operations].
- Could you re-use your `compare_records()` function here?

### 5. "Clean up" & make a report of all records

- Remember: tuples are _immutable_, but the contents can be accessed via _index_ using _bracket notation_.
- Tuples don't have to use parentheses unless there is _ambiguity_.
- Python has multiple methods of string formatting. [`str.format()`][str.format] and [`f-strings`][f-strings] are two very common ones.
- There are multiple textual formatting options available via Python's [`format specification mini-language`][format specification mini-language].

[bracket notation]: https://stackoverflow.com/questions/30250282/whats-the-difference-between-the-square-bracket-and-dot-notations-in-python
[class str]: https://devdocs.io/python~3.14/library/stdtypes#text-sequence-type-str
[class tuple]: https://devdocs.io/python~3.14/library/stdtypes#tuple
[common sequence operations]: https://devdocs.io/python~3.14/library/stdtypes#common-sequence-operations
[enumerate]: https://devdocs.io/python~3.14/library/functions#enumerate
[f-strings]: https://devdocs.io/python~3.14/tutorial/inputoutput#formatted-string-literals
[format specification mini-language]: https://devdocs.io/python~3.14/library/string#format-specification-mini-language
[iterable]: https://devdocs.io/python~3.14/glossary#term-iterable
[sequence types]: https://devdocs.io/python~3.14/library/stdtypes#typesseq
[str.format]: https://devdocs.io/python~3.14/library/stdtypes#str.format
[testing membership]: https://devdocs.io/python~3.14/reference/expressions#membership-test-operations
[tuples]: https://devdocs.io/python~3.14/tutorial/datastructures#tuples-and-sequences

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
