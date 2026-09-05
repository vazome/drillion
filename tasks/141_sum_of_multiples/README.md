---
title: sets — award energy points for a finished level
difficulty: medium
tier: core
minutes: 10
prereqs: [32]
tags: [sets]
source: exercism/python practice/sum-of-multiples (MIT, adapted)
---
# sets — award energy points for a finished level

*sum-of-multiples — count each number once, however many rules match it.*

## Read first
- [Sets](https://devdocs.io/python~3.14/library/stdtypes#set) — a set holds one copy of each item, so "collect then sum" deduplicates for free
- [Set union](https://devdocs.io/python~3.14/library/stdtypes#frozenset.union) — `|` and `update()` merge the multiples of each base value into one collection
- [any()](https://devdocs.io/python~3.14/library/functions#any) — the other route: for each number, ask whether *any* base value divides it
- [range() with a step](https://devdocs.io/python~3.14/library/functions#func-range) — `range(base, level, base)` walks a base value's multiples directly, without testing every number
- [sum()](https://devdocs.io/python~3.14/library/functions#sum) — the last line either way

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
"Sum everything that matches at least one of these rules, but never count anything twice" is a billing question, a scoring question and a reporting question all at once — think of a discount that applies if the customer is in *any* of three campaigns, and must not be applied three times. The moment two rules overlap, the naive "loop over rules, add up their matches" answer is quietly too big. Deduplicating by the *thing* rather than by the *rule* is the fix, and a set is how you say it.

## Introduction
You work for a company that makes an online, fantasy-survival game.

When a player finishes a level, they are awarded energy points.
The amount of energy awarded depends on which magical items the player found while exploring that level.

## Instructions
Your task is to write the code that calculates the energy points that get awarded to players when they complete a level.

The points awarded depend on two things:

- The level (a number) that the player completed.
- The base value of each magical item collected by the player during that level.

The energy points are awarded according to the following rules:

1. For each magical item, take the base value and find all the multiples of that value that are less than the level number.
2. Combine the sets of numbers.
3. Remove any duplicates.
4. Calculate the sum of all the numbers that are left.

Let's look at an example:

**The player completed level 20 and found two magical items with base values of 3 and 5.**

To calculate the energy points earned by the player, we need to find all the unique multiples of these base values that are less than level 20.

- Multiples of 3 less than 20: `{3, 6, 9, 12, 15, 18}`
- Multiples of 5 less than 20: `{5, 10, 15}`
- Combine the sets and remove duplicates: `{3, 5, 6, 9, 10, 12, 15, 18}`
- Sum the unique multiples: `3 + 5 + 6 + 9 + 10 + 12 + 15 + 18 = 78`
- Therefore, the player earns **78** energy points for completing level 20 and finding the two magical items with base values of 3 and 5.

### Notes for this exercise on the Python track

You can make the following assumptions about the test inputs to the
`sum_of_multiples` function:

- All input numbers are **_non-negative `int`s_** (_i.e. natural numbers
including zero_).
- A `list` of factors must be given, and its elements are unique
and sorted in ascending order.

## You get
- `level` — the level number the player completed, e.g. `20`. A non-negative whole number.
- `base_values` — the base values of the magical items found, e.g. `[3, 5]`. A list of non-negative whole numbers, unique and sorted ascending. It may be empty and it may contain `0`.

> [!NOTE]
> Exercism's stub is `def sum_of_multiples(limit, multiples)`. Here the function is `solve(level, base_values)`; nothing else about the task changes.

## You return
An `int`: the total energy points awarded.

## Rules
- a number counts if it is a multiple of **at least one** base value
- multiples must be **strictly less than** `level` — for level 20, the number 20 itself never counts
- each qualifying number is added **once**, no matter how many base values it is a multiple of: for `[3, 5]` at level 20, the number 15 contributes 15, not 30
- an empty `base_values` awards 0 points
- the only multiple of `0` is `0` itself, which adds nothing — so a `0` in the list never changes the answer

```python
solve(20, [3, 5])   # -> 78    3+5+6+9+10+12+15+18
solve(1, [3, 5])    # -> 0     nothing below 1
solve(4, [3, 0])    # -> 3     the 0 contributes nothing
solve(10000, [])    # -> 0
```

> [!WARNING]
> `solve(15, [4, 6])` is `30`, not `42`: 12 is a multiple of both and must be counted once. Any solution that loops over the base values and adds up each one's multiples separately gets this wrong.

## Hints
### Hint 1
There are two ways in and they meet in the middle. Either walk the numbers below `level` and ask each one "does any base value divide you?", or walk the base values and collect their multiples. The second is faster but has a trap — write out the multiples of 3 and of 5 below 20 side by side and look at what appears in both lists.
### Hint 2
Two routes. Collect-first: keep a `set`, and for each base value add every multiple below `level` to it (`range` with a step does the counting), so a number reached from two bases is stored once; then sum the set. Test-each-number: walk every number below `level` and keep it if it is divisible by *any* of the base values. Either way, skip a base value of `0` before you divide by it or step by it — it means "no multiples", not a crash.

### Hint 3
Different data, same "union, then total" move — the machines touched by any of several alert rules:

```python
cpu = {'web-1', 'web-2'}
memory = {'web-2', 'db-1'}
affected = cpu | memory
len(affected)   # -> 3, not 4 — web-2 is one machine, however many rules fired
```

Merge into a set first, count or sum afterwards. If you total the groups separately you are counting overlaps twice, and the overlap is usually the interesting part.
