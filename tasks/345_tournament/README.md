---
title: tournament — tally a league table and print it
minutes: 25
prereqs: [200, 215, 218, 221, 224, 227, 233, 236]
tags: [exercism, tuples, core]
source: exercism/python practice/tournament (MIT, adapted)
---
# tournament — tally a league table and print it

*tournament — fold the results into counters, then sort and pad them into a fixed-width report.*

## Why
Any report that summarises a stream of events is this task wearing a different hat: nightly job outcomes per pipeline, error counts per service, tickets closed per team. You fold the events into per-key counters, then you order and lay out the result. Two things go wrong in practice and both are here. The ordering is compound — best first, with something stable to break ties — because without the tiebreak the same data prints in a different order every run and nobody can diff two reports. And the layout is fixed width, so a column padded by hand drifts the first time a name is longer than you expected.

## Instructions
Tally the results of a small football competition.

Based on an input file containing which team played against which and what the outcome was, create a file with a table like this:

```text
Team                           | MP |  W |  D |  L |  P
Devastating Donkeys            |  3 |  2 |  1 |  0 |  7
Allegoric Alaskans             |  3 |  2 |  0 |  1 |  6
Blithering Badgers             |  3 |  1 |  0 |  2 |  3
Courageous Californians        |  3 |  0 |  1 |  2 |  1
```

What do those abbreviations mean?

- MP: Matches Played
- W: Matches Won
- D: Matches Drawn (Tied)
- L: Matches Lost
- P: Points

A win earns a team 3 points.
A draw earns 1.
A loss earns 0.

The outcome is ordered by points, descending.
In case of a tie, teams are ordered alphabetically.

### Input

Your tallying program will receive input that looks like:

```text
Allegoric Alaskans;Blithering Badgers;win
Devastating Donkeys;Courageous Californians;draw
Devastating Donkeys;Allegoric Alaskans;win
Courageous Californians;Blithering Badgers;loss
Blithering Badgers;Devastating Donkeys;loss
Allegoric Alaskans;Courageous Californians;win
```

The result of the match refers to the first team listed.
So this line:

```text
Allegoric Alaskans;Blithering Badgers;win
```

means that the Allegoric Alaskans beat the Blithering Badgers.

This line:

```text
Courageous Californians;Blithering Badgers;loss
```

means that the Blithering Badgers beat the Courageous Californians.

And this line:

```text
Devastating Donkeys;Courageous Californians;draw
```

means that the Devastating Donkeys and Courageous Californians tied.

## You get
`results` — a list of strings, one match per string:

```python
["Allegoric Alaskans;Blithering Badgers;win",
 "Devastating Donkeys;Courageous Californians;draw"]
```

Each string is `home;away;outcome`, `outcome` is exactly one of `win`, `loss` or `draw`, and it describes the **first** team named. Every line is well formed. The list may be empty.

> [!NOTE]
> Exercism's stub is `def tally(rows)` and its instructions talk about reading and writing files. Here the function is `solve(results)`, and both the input and the output are already in memory.

## You return
A `list` of `str` — one entry per line of the table, the header line first, then one line per team. No newline characters inside the strings.

## Rules
- a win scores 3 points, a draw 1, a loss 0; MP is matches played
- the outcome describes the first team, so `A;B;loss` means B beat A
- every team that appears in any line gets a row
- rows are ordered by points descending, then by team name ascending — a plain string comparison
- the header line is exactly this, spaces included:

```text
Team                           | MP |  W |  D |  L |  P
```

- each row is the team name left-aligned in 30 columns, then ` | `, then MP, W, D, L and P each right-aligned in 2 columns and separated by ` | `
- an empty `results` gives the header line and nothing else

```python
solve(["Allegoric Alaskans;Blithering Badgers;win"])
# -> ['Team                           | MP |  W |  D |  L |  P',
#     'Allegoric Alaskans             |  1 |  1 |  0 |  0 |  3',
#     'Blithering Badgers             |  1 |  0 |  0 |  1 |  0']
```

> [!WARNING]
> Lines are compared character for character. One space too few in a column, or a name padded to 31 instead of 30, fails every case — even though the table still looks fine on screen.

## Read first
- [Format specification mini-language](https://docs.python.org/3/library/string.html#format-specification-mini-language) — `{name:30}` left-aligns text in 30 columns, `{n:2}` right-aligns a number in 2; you never count spaces yourself
- [`dict.setdefault()`](https://docs.python.org/3/library/stdtypes.html#dict.setdefault) — fetch a key's record, creating it the first time you see that key
- [`sorted()`](https://docs.python.org/3/library/functions.html#sorted) — the `key=` argument, and how a tuple key sorts on its first item and falls back to the second

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Hints
### Hint 1
Two jobs, and they do not belong in the same loop. First walk the lines and turn them into per-team counters — every line touches two teams, and what it does to the second is the mirror of what it does to the first. Only once the counters are complete do you start thinking about order and spacing.

### Hint 2
For the tally, a dict keyed by team name whose value holds wins, draws and losses is plenty: matches played and points are both derivable from those three, so do not store them separately and risk them disagreeing. For the order, `sorted` takes a `key` that may return a tuple — the catch is that you want one part descending and the other ascending, and the usual move for a number is to sort on its negative. For the rows, let a format spec do the padding; alignment and width are part of the replacement field.

### Hint 3
Different data, same shape — nightly CI jobs, tallied and then printed:

```python
counts = {}
for line in ["build;pass", "test;fail", "build;fail", "lint;pass"]:
    job, outcome = line.split(";")
    counts.setdefault(job, {"pass": 0, "fail": 0})[outcome] += 1

for job, record in sorted(counts.items(), key=lambda kv: (-kv[1]["fail"], kv[0])):
    print(f"{job:12} | {record['pass']:3} | {record['fail']:3}")
# build        |   1 |   1
# test         |   0 |   1
# lint         |   1 |   0
```

Two ideas worth stealing. `setdefault` means the loop body never has to ask "have I seen this key before". And the tuple returned by `key=` sorts on the first item, falling back to the second when the first ties — with the minus sign turning that first item around, which is why `test` (1 failure) comes before `lint` (0 failures) while `build` and `test` fall back to alphabetical.
