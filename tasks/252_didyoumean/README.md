---
title: edit distance — did you mean this command?
difficulty: medium
tier: advanced
minutes: 22
prereqs: [55, 188]
tags: [dynamic-programming, strings]
---
# edit distance — did you mean this command?

*Counting the single-character edits between what someone typed and what your tool understands, and only suggesting the nearest one when it is actually near.*

## Read first
- [String indexing](https://devdocs.io/python~3.14/library/stdtypes#text-sequence-type-str) — a string is a sequence of characters, and this whole task is comparing two of them position by position
- [`min()`](https://devdocs.io/python~3.14/library/functions#min) — the cheapest of several candidate edits
- [`enumerate()`](https://devdocs.io/python~3.14/library/functions#enumerate) — walking one string while keeping the index into the table you are filling

## Why
Somebody types `stauts` and your tool prints `unknown command`. That is a true statement and a useless one: the tool knows all fourteen commands it accepts, and one of them is a single transposition away. The suggestion has to be earned, though. A tool that answers `git push` when you typed `ls` is worse than one that says nothing, because now you distrust the suggestions you would otherwise have followed. So you need a number — how many single-character edits turn what they typed into a command you know — and a line past which you keep quiet.

## You get
- `typed` — what the user typed, a non-empty `str` of lowercase letters, e.g. `"stauts"`.
- `commands` — the commands your tool accepts, a list of non-empty lowercase `str`, in the order they are declared, e.g. `["status", "start", "stop"]`. It is never empty, and the same command is never listed twice.

## You return
the `str` from `commands` that is closest to `typed`, or `None` when nothing is close enough.

## Rules
The distance between two strings is the fewest single-character edits that turn one into the other. There are exactly three edits, each costing 1:

- **insert** a character, **delete** a character, **substitute** one character for another.

- Return the command with the smallest distance to `typed`.
- Ties go to the command listed **earliest** in `commands`.
- If the smallest distance is greater than `3`, return `None` — the user meant something you do not have.
- An exact match has distance `0` and is returned as itself.

```python
solve("stauts", ["status", "start", "stop"])   # -> 'status'
solve("cat", ["car", "cast"])                  # -> 'car'    (both are 1 away; 'car' is listed first)
solve("zzzzzzzz", ["status", "start"])         # -> None
solve("start", ["status", "start"])            # -> 'start'
```

> [!WARNING]
> Substitution is one edit, not two. Count a substitution as a delete followed by an insert — which is what you get if you only ever match or skip characters — and every distance involving a changed letter comes out too big. It does not merely inflate the numbers; it changes the winner. `"cat"` is one substitution from `"car"` and one insertion from `"cast"`, so `"car"` wins on the listed order. Charge two for the substitution and `"cast"` wins instead, and the test says so.

> [!NOTE]
> There is no need to remember the whole table. Each row of it only ever reads the row above and the cell to its left, so two rows — or one row and a saved corner value — is enough.

## Hints
### Hint 1
Solve one pair of strings first and worry about picking a winner afterwards. `distance(a, b)` is a table with `len(a) + 1` rows and `len(b) + 1` columns, where the cell at `(i, j)` is the distance between the first `i` characters of `a` and the first `j` characters of `b`.
### Hint 2
The edges are free: turning `""` into the first `j` characters costs `j` insertions, and the first `i` characters into `""` costs `i` deletions. Every other cell is `min(above + 1, left + 1, diagonal + cost)`, where `cost` is `0` when the two characters match and `1` when they do not — those three are exactly delete, insert and substitute.
### Hint 3
The small version, one row at a time:

```python
def distance(a, b):
    row = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        corner, row[0] = row[0], i
        for j, cb in enumerate(b, 1):
            corner, row[j] = row[j], min(row[j] + 1, row[j - 1] + 1, corner + (ca != cb))
        # `corner` holds the diagonal cell — the value `row[j]` had before this row overwrote it
    return row[-1]

distance("kitten", "sitting")   # 3
distance("stauts", "status")    # 2
```

`ca != cb` is a `bool`, and `True + 1` is `2`, so it doubles as the substitution cost. Picking the winner is then one pass over `commands` keeping the smallest distance seen, and `<` rather than `<=` in that comparison is what makes ties go to the earlier command.
