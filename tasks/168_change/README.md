---
title: loops — hand back the fewest coins that add up
difficulty: hard
tier: core
minutes: 25
prereqs: [3, 18]
tags: [loops]
source: exercism/python practice/change (MIT, adapted)
---
# loops — hand back the fewest coins that add up

*change — the greedy answer is the wrong answer; build up from the small amounts instead.*

## Read first
- [`range()`](https://devdocs.io/python~3.14/library/functions#func-range) — walking `1` up to `target` in order, so that every smaller amount is already answered by the time you need it
- [`min()`](https://devdocs.io/python~3.14/library/functions#min) — the smallest of several candidates, and the `key=` argument for when "smallest" means "shortest list"
- [Raising exceptions](https://devdocs.io/python~3.14/tutorial/errors#raising-exceptions) — `raise ValueError("…")`, and why the message has to match exactly

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
A till, a vending machine, a payouts service, a scheduler handing out quota in fixed chunks — all of them have to hit an exact total out of fixed denominations, and all of them want to hand over as few pieces as possible. The instinct is to grab the biggest denomination that still fits and repeat. That works for the coins in your pocket, because those were designed so it would, and it quietly fails everywhere else: with 1, 10 and 11 available, the greedy answer for 20 is 11 plus nine 1s, and the right answer is two 10s. In a payout system that is real money, and it is invisible until somebody audits it.

## You get
- `coins` — the denominations available, a list of positive `int`s in ascending order, e.g. `[1, 5, 10, 25, 100]`. Each one is available in unlimited supply.
- `target` — the total to make, an `int`, e.g. `15`. It may be `0` and it may be negative.

> [!NOTE]
> Exercism's stub is `def find_fewest_coins(coins, target)`. Here it is `solve(coins, target)` — same two arguments, same order.

## You return
A `list` of `int` — the coins that add up to exactly `target` using as few coins as possible, **smallest first**. A `target` of `0` returns the empty list.

## Rules
- fewest coins wins; two answers with the same number of coins are equally good, but yours must still be sorted ascending and add up exactly
- every coin you return has to come from `coins`, and you may use any coin as many times as you like
- `target` of `0` returns `[]`
- `target < 0` raises `ValueError("target can't be negative")`, and this is checked before anything else
- if no combination of the coins reaches `target`, raise `ValueError("can't make target with given coins")`

```python
solve([1, 5, 10, 25, 100], 15)  # -> [5, 10]
solve([1, 4, 15, 20, 50], 23)   # -> [4, 4, 15]
solve([1, 10, 11], 20)          # -> [10, 10]
solve([2, 5, 10, 20, 50], 21)   # -> [2, 2, 2, 5, 10]
solve([1, 5, 10, 21, 25], 0)    # -> []
```

> [!WARNING]
> "Take the biggest coin that still fits, then repeat" is wrong, and the tests are chosen to prove it. On `[1, 10, 11]` with a target of 20 it pays ten coins where two will do, and on `[2, 5, 10, 20, 50]` with a target of 21 it takes the 20 and then strands itself with 1 left and nothing small enough to pay it.

## Hints
### Hint 1
The greedy instinct is the trap; this task exists because of it. So do not ask "which coin do I take first?". Ask a smaller question instead: *if I already knew the best answer for every amount below the target, how would I get the target's answer in one step?*

### Hint 2
Work upwards rather than downwards. Answer amount 1, then 2, then 3, all the way up to the target, keeping each answer as you go. For any amount, the best answer is one coin plus the best answer for whatever is left after that coin — so you try each denomination once and keep whichever result came out shortest. Amounts you cannot reach at all have to be marked as *unreachable*, which is not the same as "zero coins": treat an unreachable amount as free and it starts looking like a bargain to everything above it. When you finally reach the target you either have a stored answer or you have your second `ValueError`. Sort before returning, and remember the negative check runs before any of this.

### Hint 3
Different data, same shape — parcels that must be filled exactly, using 3 kg, 7 kg and 8 kg boxes:

| weight | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fewest boxes | 0 | — | — | 1 | — | — | 2 | 1 | 1 | 3 | 2 | 2 |

Every entry is read off entries to its left. 10 is one 3 kg box on top of the answer for 7 (which is 1), or one 7 kg box on top of the answer for 3 (also 1) — either way, 2. And 4 stays `—` because 4 − 3 = 1 is itself `—` and the other two boxes are too big; that dash is emphatically not 0, and treating it as 0 is the bug that makes the whole table wrong.

Why bother building the table at all? Ask it for 14 kg. Greedy packs 8 + 3 + 3 and calls it three boxes. The table says 7 + 7.
