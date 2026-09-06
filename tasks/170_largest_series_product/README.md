---
title: generators — the biggest product of adjacent digits
difficulty: medium
tier: advanced
minutes: 25
prereqs: [3, 18]
tags: [generators]
source: exercism/python practice/largest-series-product (MIT, adapted)
---
# generators — the biggest product of adjacent digits

*largest-series-product — slide a fixed window along the digits and keep the best product.*

## Read first
- [`str.isdigit()`](https://devdocs.io/python~3.14/library/stdtypes#str.isdigit) — true when every character is a digit, so it answers for a whole string in one call
- [`math.prod()`](https://devdocs.io/python~3.14/library/math#math.prod) — multiply an iterable of numbers together, the way `sum()` adds them
- [Slicing](https://devdocs.io/python~3.14/reference/expressions#slicings) — `digits[start:start + span]` *is* the window; the only real question is how many starts there are

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
A fixed window sliding along a stream is one of the three or four shapes that turn up constantly in monitoring: the five-minute rolling error rate, the busiest hour in a day of traffic, the worst run of latency in a trace. The sliding itself is easy. What actually breaks in production is the boundaries — a window wider than the data you have, a window width that arrived as a negative number out of a config file, an empty stream on the first morning. This task is a sliding window with every one of those questions asked out loud and given an exact answer, which is more than most of the code you will inherit does.

## You get
- `digits` — a string of digit characters, e.g. `"63915"`. It may be empty, and it may contain characters that are not digits — which is an error, not something to skip over.
- `span` — how many adjacent digits make up one series, an `int`, e.g. `3`. It may be `0` and it may be negative.

> [!NOTE]
> Exercism's stub is `def largest_product(series, size)`. Here it is `solve(digits, span)` — same two arguments, same order.

## You return
An `int` — the largest product you can make from `span` adjacent digits of `digits`.

## Rules
The four decisions below happen in this order, and the order is part of the task:

1. `span == 0` returns `1`, the empty product, whatever `digits` holds — so `solve("", 0)` is `1` and never raises
2. `span > len(digits)` raises `ValueError("span must not exceed string length")` — this is what covers `solve("", 1)`
3. `span < 0` raises `ValueError("span must not be negative")`
4. any character of `digits` that is not a digit raises `ValueError("digits input must only contain digits")`

Otherwise: every window of `span` adjacent characters counts, windows overlap, and a window containing a zero has a product of zero, which is a perfectly good answer.

```python
solve("63915", 3)       # -> 162
solve("29", 2)          # -> 18
solve("1027839564", 3)  # -> 270
solve("99099", 3)       # -> 0
solve("", 0)            # -> 1
```

> [!WARNING]
> Because the character check comes last, `solve("12a", 4)` complains about the span, not about the `a`. Reorder the guards and you change which message comes out, which the grader notices even though the input was bad either way.

## Hints
### Hint 1
The guards are half of this task and they are order-sensitive: one value of `span` short-circuits everything and returns a number rather than raising, two more are errors with their own messages, and the character check comes last of all. Write those four decisions down, in order, before you write a single line of multiplying.

### Hint 2
Once the input is known good, each window begins at some index and runs `span` characters, so a slice hands you the window and the only thing to work out is how many starting positions exist — one more than the difference between the length and the span. Multiply a window's digits together and keep the largest total you have seen. Two things to watch: the characters are text, so `"9"` and `9` are not the same thing and you have to convert; and `max()` over a generator expression will do the whole search for you, which is why the span check has to happen before you build that generator rather than inside it.

### Hint 3
Different data, same shape — the busiest three-hour stretch in a day of request counts:

```python
counts = [4, 9, 2, 7, 1, 8, 8, 3]
window = 3
starts = range(len(counts) - window + 1)              # 0, 1, 2, 3, 4, 5 — six windows
best = max(sum(counts[i:i + window]) for i in starts)  # -> 19, from [8, 8, 3]
```

Same skeleton, different combining step: `sum` here, a product there. And notice what `starts` is quietly protecting you from — if `window` were 9 that range would be empty, and `max()` over nothing raises. That is the real reason the span check belongs in front of the loop rather than inside it.
