---
title: lists — Black Joe hand averages
difficulty: medium
tier: core
minutes: 15
prereqs: [13]
tags: [lists]
source: exercism/python concept/card-games (MIT, adapted)
---
# lists — Black Joe hand averages

*`sum`, `len`, indexing and a slice with a step — four ways to interrogate a hand.*

## Read first
- [common sequence operations](https://devdocs.io/python~3.14/library/stdtypes#common-sequence-operations) — indexing, `s[i:j:k]` slicing with a step, and `len(s)`
- [the `list` type](https://devdocs.io/python~3.14/library/stdtypes#list) — the reference page for the type you are slicing
- [sequence types — `list`, `tuple`, `range`](https://devdocs.io/python~3.14/library/stdtypes#sequence-types-list-tuple-range) — where negative indexing is defined
- [`sum()`](https://devdocs.io/python~3.14/library/functions#sum) — adds an iterable of numbers; the other half of an average
- [lists (Python tutorial)](https://devdocs.io/python~3.14/tutorial/datastructures) — the tour, including what mutability means in practice
- [lists and tuples in Python (Real Python)](https://realpython.com/python-lists-tuples/) — slicing explained slowly, with diagrams

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
A "hand" here is a list of numbers, and every question Elyse asks of it is a question you will ask of latency samples, of a batch of billing rows, of a week of daily costs. What is the average? Is the cheap estimate as good as the real one? Do the odd and even positions agree? Does the last item need special treatment? `sum(xs) / len(xs)`, `xs[0]`, `xs[-1]`, `xs[::2]` — four bits of notation that replace most of the loops a beginner writes, plus one reminder that a list is mutable, so changing its last element changes it for whoever handed it to you.

## You get
Nothing. `solve()` takes **no arguments**; the grader calls your functions with the hands. A hand is a list of ints, one per card, never empty. Jacks are the value `11`.

> [!NOTE]
> Exercism asks for all seven functions in one `lists.py`. Here the task is split in two: **this task covers tasks 4–7**, and tasks 1–3 are task `013_card_games`. There is one entry point — `solve()` returns a dict that hands your four functions to the grader, keyed by name.

## You return
A dict with these four functions.

| key | parameters | returns |
| --- | --- | --- |
| `"card_average"` | `hand` — the card values, e.g. `[5, 6, 7]` | the mean as a `float`: the sum of the cards divided by how many there are |
| `"approx_average_is_average"` | `hand` — an odd number of cards, so "the middle one" is well defined | `True` when the average of the first and last card **or** the value of the middle card equals the real average; `False` when neither does |
| `"average_even_is_average_odd"` | `hand` — at least two cards | `True` when the average of the cards at even indexes equals the average of the cards at odd indexes |
| `"maybe_double_last"` | `hand` | the hand with its last card doubled when that card is a Jack (`11`), and otherwise exactly as it arrived |

```python
cards = solve()
cards["card_average"]([5, 6, 7])                        # -> 6.0
cards["card_average"]([1, 2, 3, 4])                     # -> 2.5
cards["approx_average_is_average"]([2, 3, 4, 8, 8])     # -> True
cards["approx_average_is_average"]([1, 2, 3, 5, 9])     # -> False
cards["average_even_is_average_odd"]([1, 3, 5, 7, 9])   # -> True
cards["average_even_is_average_odd"]([1, 2, 3, 4])      # -> False
cards["maybe_double_last"]([5, 9, 11])                  # -> [5, 9, 22]
cards["maybe_double_last"]([5, 9, 10])                  # -> [5, 9, 10]
```

## Rules
- this task implements **Exercism tasks 4, 5, 6 and 7 only** — `get_rounds`, `concatenate_rounds` and `list_contains_round` belong to task `013_card_games`
- the dict keys are exactly the four strings above, and each value is the function itself — no parentheses
- `card_average` divides with `/`, so `[1, 2, 3, 4]` averages to `2.5` and not `2` — the result is a `float` even when it comes out whole
- "the middle card" is the element at index `len(hand) // 2`, and the second strategy compares that card's **value** with the real average, not an average of anything
- either strategy matching is enough: the check is an `or`
- even indexes are `0, 2, 4, …`, so the first card sits at an even index; odd indexes are `1, 3, 5, …`
- `maybe_double_last` looks at the last card only, and only the value `11` counts

> [!WARNING]
> The two comparison functions are compared with `is True` / `is False`, so return real booleans. And the averages are compared with plain `==` on floats — do not round, do not use `int()`; hand back exactly what the division gives you.

## Hints
### Hint 1
Write the average first: count how many items are in the list, sum up their values, and return the sum divided by the count. Both of those are one built-in call each. Then notice that the next two functions are *comparisons between averages* — so once the first function exists, you can call it instead of doing arithmetic again. Think about how you can reuse the code you have already written.
### Hint 2
To reach a single element, use the square bracket notation. The first element of a list is at index 0 counting from the **left**; negative indexing starts at -1 from the **right**, so the last element is always `<list>[-1]` no matter how long the list is.

For the "approximate average" task you need two candidate numbers and one real one. The first candidate is the average of a two-element list you build from the ends. The second is a single element — the middle one, which for an odd-length list sits at `len(hand) // 2`.

For the even/odd task, the slice syntax supports a *step value*: `<list>[<start>:<stop>:<step>]`. Leave `start` and `stop` empty and set the step to 2 and you get every other element; start at 1 instead and you get the others. Then it is one comparison between two averages.

For the last task, lists are *mutable* — once a list exists you can change any element in place. Look at the final card, and change it only if it is worth 11.
### Hint 3
Different data, same moves — a week of daily costs:

```python
costs = [12.0, 14.0, 16.0, 18.0, 20.0]
sum(costs) / len(costs)          # -> 16.0
(costs[0] + costs[-1]) / 2       # -> 16.0    the ends agree with the real mean
costs[len(costs) // 2]           # -> 16.0    so does the middle day

costs[::2]                       # -> [12.0, 16.0, 20.0]
costs[1::2]                      # -> [14.0, 18.0]

budget = [100, 100, 250]
budget[-1] *= 2
budget                           # -> [100, 100, 500]
```

The last two lines are the mutation to be careful with: `budget` changed, and so did every other name pointing at that same list.
