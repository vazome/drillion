---
title: generators — the biggest product of adjacent digits
difficulty: medium
tier: advanced
minutes: 25
prereqs: [88, 90, 92, 97, 99, 101]
tags: [generators]
source: exercism/python practice/largest-series-product (MIT, adapted)
---
# generators — the biggest product of adjacent digits

*largest-series-product — slide a fixed window along the digits and keep the best product.*

## Why
A fixed window sliding along a stream is one of the three or four shapes that turn up constantly in monitoring: the five-minute rolling error rate, the busiest hour in a day of traffic, the worst run of latency in a trace. The sliding itself is easy. What actually breaks in production is the boundaries — a window wider than the data you have, a window width that arrived as a negative number out of a config file, an empty stream on the first morning. This task is a sliding window with every one of those questions asked out loud and given an exact answer, which is more than most of the code you will inherit does.

## Introduction
You work for a government agency that has intercepted a series of encrypted communication signals from a group of bank robbers.
The signals contain a long sequence of digits.
Your team needs to use various digital signal processing techniques to analyze the signals and identify any patterns that may indicate the planning of a heist.

## Instructions
Your task is to look for patterns in the long sequence of digits in the encrypted signal.

The technique you're going to use here is called the largest series product.

Let's define a few terms, first.

- **input**: the sequence of digits that you need to analyze
- **series**: a sequence of adjacent digits (those that are next to each other) that is contained within the input
- **span**: how many digits long each series is
- **product**: what you get when you multiply numbers together

Let's work through an example, with the input `"63915"`.

- To form a series, take adjacent digits in the original input.
- If you are working with a span of `3`, there will be three possible series:
  - `"639"`
  - `"391"`
  - `"915"`
- Then we need to calculate the product of each series:
  - The product of the series `"639"` is 162 (`6 × 3 × 9 = 162`)
  - The product of the series `"391"` is 27 (`3 × 9 × 1 = 27`)
  - The product of the series `"915"` is 45 (`9 × 1 × 5 = 45`)
- 162 is bigger than both 27 and 45, so the largest series product of `"63915"` is from the series `"639"`.
  So the answer is **162**.

### Exception messages

Sometimes it is necessary to [raise an exception](https://docs.python.org/3/tutorial/errors.html#raising-exceptions). When you do this, you should always include a **meaningful error message** to indicate what the source of the error is. This makes your code more readable and helps significantly with debugging. For situations where you know that the error source will be a certain type, you can choose to raise one of the [built in error types](https://docs.python.org/3/library/exceptions.html#base-classes), but should still include a meaningful message.

This particular exercise requires that you use the [raise statement](https://docs.python.org/3/reference/simple_stmts.html#the-raise-statement) to "throw" a `ValueError` when your `largest_product()` function receives invalid input. The tests will only pass if you both `raise` the `exception` and include a message with it.  Feel free to reuse your code from the `series` exercise!

To raise a `ValueError` with a message, write the message as an argument to the `exception` type:

```python
# span of numbers is longer than number series
raise ValueError("span must not exceed string length")

# span of number is negative
raise ValueError("span must not be negative")

# series includes non-number input
raise ValueError("digits input must only contain digits")
```

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

## Read first
- [`str.isdigit()`](https://docs.python.org/3/library/stdtypes.html#str.isdigit) — true when every character is a digit, so it answers for a whole string in one call
- [`math.prod()`](https://docs.python.org/3/library/math.html#math.prod) — multiply an iterable of numbers together, the way `sum()` adds them
- [Slicing](https://docs.python.org/3/reference/expressions.html#slicings) — `digits[start:start + span]` *is* the window; the only real question is how many starts there are

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

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
