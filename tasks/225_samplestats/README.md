---
title: statistics — a latency sample described by its middle, its quartiles and its spread
difficulty: medium
tier: core
minutes: 15
prereqs: [66]
tags: [numbers]
---
# statistics — a latency sample described by its middle, its quartiles and its spread

*The `statistics` module already knows the definitions; the work is choosing which of them the number on your dashboard is supposed to be.*

## Read first
- [`statistics`](https://devdocs.io/python~3.14/library/statistics) — the module and what each function assumes about its input
- [`quantiles`](https://devdocs.io/python~3.14/library/statistics#statistics.quantiles) — `n=` for how many cuts, `method=` for how the cuts are placed
- [`stdev` and `pstdev`](https://devdocs.io/python~3.14/library/statistics#statistics.stdev) — a sample against a whole population

## Why
A weekly report describes yesterday's response times in four numbers so the on-call engineer can see the shape of the day without reading ten thousand rows. The middle value says what a typical request felt like, the first and third quartiles say how wide the ordinary half of the traffic was, and the spread says whether the day was steady or lumpy. Three of those are one function call each. The fourth has two functions with almost the same name, and the one that matches "these are the requests we happened to measure" is not the one whose name is shorter.

## You get
`samples` — a list of response times in milliseconds, floats, at least two of them, in the order they were recorded rather than sorted.

## You return
a `dict` with exactly four keys — `"median"`, `"q1"`, `"q3"` and `"stdev"` — each mapped to a float rounded to two decimal places.

## Rules
- `"median"` is the middle value, averaging the two middle ones when the count is even.
- `"q1"` and `"q3"` are the first and third quartiles, cut with the **inclusive** method, which treats the data as the whole of what is being described rather than a sample drawn from something larger.
- `"stdev"` is the **sample** standard deviation, the one that divides by `n - 1`.
- Round each value to two decimal places with `round`, last, after the statistic has been computed.
- Do not sort or otherwise modify the caller's list.

```python
solve([12.0, 4.5, 7.25, 19.0, 3.0, 8.5, 11.0, 6.25])
# -> {"median": 7.88, "q1": 5.81, "q3": 11.25, "stdev": 5.07}
```

> [!WARNING]
> `pstdev` on that same list gives 4.74, and `quantiles` without `method="inclusive"` gives 4.44 and 12.75. All three are correct answers to questions nobody asked here, and all three look plausible next to the right one. The rules above name which definition the report is written against.

> [!NOTE]
> `quantiles(samples, n=4)` returns the three cut points as a list, so the first quartile is index `0` and the third is index `2`. There is no index `3`.

## Hints
### Hint 1
`statistics.median` sorts internally. You do not have to sort first, and doing it in place would modify the caller's list.
### Hint 2
`statistics.quantiles(samples, n=4, method="inclusive")` gives `[q1, q2, q3]` in one call, and `q2` is the median again.
### Hint 3
The difference between the two spread functions is one letter and one denominator:

```python
statistics.stdev(samples)    # divides by n - 1: a sample of a larger population
statistics.pstdev(samples)   # divides by n: the population itself
```

A list of the requests that happened to be measured yesterday is a sample.
