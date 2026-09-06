---
title: collections — a roster that stays sorted by grade, then by name
difficulty: hard
tier: core
minutes: 20
prereqs: [35]
tags: [collections, dict-methods]
source: exercism/python practice/grade-school (MIT, adapted)
---
# collections — a roster that stays sorted by grade, then by name

*grade-school — store each enrolment once, and let every view do its own sorting on the way out.*

## Read first
- [A first look at classes](https://devdocs.io/python~3.14/tutorial/classes#a-first-look-at-classes) — `__init__`, `self`, and giving each instance its own storage
- [`dict`](https://devdocs.io/python~3.14/library/stdtypes#mapping-types-dict) — `name in mapping` is the membership test that decides whether an enrolment is refused
- [`sorted()`](https://devdocs.io/python~3.14/library/functions#sorted) — sorting tuples compares the first item, then the second, which is exactly "grade first, then name"
- [`collections.defaultdict`](https://devdocs.io/python~3.14/library/collections#collections.defaultdict) — one way to group names under a grade without checking whether the key exists yet

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
A school office enrols a child on one screen, and three other screens then ask that same record different questions: who is in year 2, who is enrolled at all, and did that last enrolment actually take. The mistake that costs the office a morning is keeping a separate list behind each screen — a name typed twice lands in two of them, and the printed register stops agreeing with the class list. Keep one fact per student, decide the ordering at the moment you *read*, and the three screens can never disagree. Tenant directories, on-call rotas and feature-flag audiences are all this shape: one write path, several sorted views.

## You get
Nothing to start — you return a **class**. The grader builds it with no arguments, `School()`, and then drives it with the four members below. Names are plain strings with no spaces, e.g. `"Aimee"`; grades are plain `int`s from `1` upwards, e.g. `2`.

> [!NOTE]
> Exercism's stub is a `class School` in `grade_school.py`. Here the entry point is `solve()`, which takes **no arguments** and returns the class itself — not an instance.

## You return
The class. The grader uses it like this:

```python
School = solve()
school = School()
school.add_student(name="Aimee", grade=2)
school.added()        # -> [True]
school.roster()       # -> ["Aimee"]
school.grade(2)       # -> ["Aimee"]
school.grade(1)       # -> []
```

| member | is | behaviour |
| --- | --- | --- |
| `add_student(name, grade)` | method | try to enrol `name` in `grade`; returns nothing |
| `added()` | method | a `list[bool]`, one entry per `add_student` call since the previous `added()` — `True` if that call enrolled someone, `False` if it was refused |
| `roster()` | method | a `list[str]` of every enrolled name, sorted by grade first and by name within a grade |
| `grade(number)` | method | a `list[str]` of the names in that grade, sorted by name; `[]` when nobody is in it |

## Rules
- a name may be enrolled **once in the whole school**, not once per grade: after `add_student("James", 2)`, a later `add_student("James", 3)` is refused and James stays in grade 2
- `add_student` never raises and never returns anything — the refusal shows up as a `False` in `added()`
- `added()` is a **drain**: it hands back the outcomes recorded since the previous call and then starts a fresh list, so calling it twice in a row gives `[]` the second time
- `roster()` sorts by `(grade, name)`, so a grade-1 student comes before every grade-2 student regardless of the alphabet; within one grade it is plain alphabetical order
- `grade(number)` is alphabetical only — a grade holds one year group, so there is nothing else to sort by
- `add_student` is called with keyword arguments in some grader cases (`add_student(name="Aimee", grade=2)`), so keep those two parameter names
- `roster()` and `grade(number)` each return a **new list** every call; the grader calls both of them more than once on the same school and expects the same answer both times

```python
School = solve()
school = School()
for name, grade in [("Peter", 2), ("Anna", 1), ("Barb", 1), ("Zoe", 2), ("Alex", 2), ("Jim", 3)]:
    school.add_student(name=name, grade=grade)
school.roster()   # -> ["Anna", "Barb", "Alex", "Peter", "Zoe", "Jim"]
school.grade(2)   # -> ["Alex", "Peter", "Zoe"]
school.added()    # -> [True, True, True, True, True, True]
school.added()    # -> []
```

> [!WARNING]
> Sorting as the names arrive is not enough. Insert `Anna` in grade 1 *after* `Jim` in grade 3 and a list you keep in arrival order can never recover — sort when you read, not when you write.

## Hints
### Hint 1
Three of the four members are questions about the same handful of facts, and only one of them changes anything. Write down what the *smallest* record of the school is — the least you could store and still answer all three questions — before you write a line. `added()` is the odd one out: it is not a question about the school at all, it is a question about what happened since you last asked.

### Hint 2
"A student may be enrolled once in the whole school" is a hint about the shape of your storage: if a student's name is the thing that must be unique, let the name be the key and the grade be the value, and the uniqueness check becomes a single membership test. The two read methods then both start from the same mapping — one filters it, one sorts it. For the sort, remember that comparing tuples compares position by position, so building a `(grade, name)` pair per student and sorting the pairs gets the grade-then-name order without a custom key function. `added()` needs two lines: hand back what you have collected, then replace it with an empty list.

### Hint 3
Different data, same shape — a seating plan where each guest sits at exactly one table:

```python
class Seating:
    def __init__(self):
        self.table_of = {}

    def seat(self, guest, table):
        if guest in self.table_of:
            return False
        self.table_of[guest] = table
        return True

    def running_order(self):
        return [guest for _, guest in sorted((t, g) for g, t in self.table_of.items())]

seating = Seating()
seating.seat("Rae", 3)
seating.seat("Ada", 9)
seating.seat("Rae", 1)     # -> False, Rae keeps table 3
seating.running_order()    # -> ["Rae", "Ada"]
```

Note what `running_order` does *not* do: it keeps no sorted list of its own. The one mapping is the truth, and the order is computed fresh every time it is asked for. `School` is this with a second read method and with the `True`/`False` outcomes collected instead of returned.
