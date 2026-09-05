---
title: while — fill a batch until the budget is spent
difficulty: easy
tier: core
minutes: 10
prereqs: [101]
tags: [while, loops]
---
# while — fill a batch until the budget is spent

*A `for` loop runs a known number of times. A `while` loop runs until something stops it.*

## Read first
- [The while statement](https://devdocs.io/python~3.14/reference/compound_stmts#the-while-statement) — the loop that asks a question before every pass
- [break and continue](https://devdocs.io/python~3.14/tutorial/controlflow#break-and-continue-statements-and-else-clauses-on-loops) — the other way to leave a loop early, and why a condition is usually clearer
- [len()](https://devdocs.io/python~3.14/library/functions#len) — how many items there are, which is what your condition compares against

## Why
Your log shipper sends messages to an API that refuses any request over a fixed size. Messages arrive in order and must stay in order, so each request takes as many of the waiting messages as fit and leaves the rest for the next one. You do not know how many will fit until you add them up, which is the point: the loop stops when the budget says so, not after a number of turns you could have counted in advance.

## You get
`messages` — a list of strings, oldest first, e.g. `["disk full", "conn reset", "ok"]`. `budget` — a whole number: the most characters one request may carry in total, e.g. `20`. The test creates them and hands them to you; you never build them yourself.

## You return
a pair `(batch, rest)`: the messages that fit, in order, and everything still waiting, in order.

## Rules
Take messages from the front while they still fit.

- A message fits when the batch's total length, counting the message itself, stays at or under `budget`. Length is `len(message)`; nothing is added for separators.
- Stop at the FIRST message that does not fit. Do not skip it and keep looking for a smaller one behind it: order is the whole contract.
- `rest` is everything you did not take, still in order. Together, `batch + rest` is `messages` unchanged.

```python
solve(["disk full", "conn reset", "ok"], 20)
# -> (["disk full", "conn reset"], ["ok"])
```

> [!WARNING]
> When the very first message is already longer than `budget`, nothing fits: return `([], messages)`. A loop that assumes at least one item gets this wrong, and it is the case the test always includes.

## Hints
### Hint 1
Two things change on every pass: where you are in the list, and how much room you have used. Start both at zero and write the condition that has to hold before you take one more message.
### Hint 2
The condition has two halves joined by `and`: there is still a message left (`i < len(messages)`), and taking it keeps you inside the budget (`used + len(messages[i]) <= budget`). Python checks the left half first, so the second half never reads past the end.
### Hint 3
Different data, same shape — take coins while the pocket holds:

```python
coins, used, i = [2, 5, 3, 9], 0, 0
taken = []
while i < len(coins) and used + coins[i] <= 8:
    taken.append(coins[i])
    used += coins[i]
    i += 1
print(taken, coins[i:])   # [2, 5] [3, 9]
```

`messages[i:]` is the rest, with no second loop needed.
