---
title: sets — find every prime up to a limit by crossing out multiples
difficulty: medium
tier: core
minutes: 20
prereqs: [88, 90, 92, 97, 99, 101, 112]
tags: [sets]
source: exercism/python practice/sieve (MIT, adapted)
---
# sets — find every prime up to a limit by crossing out multiples

*sieve — mark what cannot be, instead of testing what might be.*

## Why
There are two ways to filter a big list: ask a question about every item, or mark the items you already know are out and keep the rest. The second is usually far cheaper, and it is the shape behind bloom filters, blocklists, bitmap indexes and "which of these million IDs have we already processed?". The Sieve of Eratosthenes is the oldest example of it — two thousand years old, still the fastest simple way to get all the primes below a limit — and it is short enough that you can feel exactly where the saving comes from.

## Introduction
You bought a big box of random computer parts at a garage sale.
You've started putting the parts together to build custom computers.

You want to test the performance of different combinations of parts, and decide to create your own benchmarking program to see how your computers compare.
You choose the famous "Sieve of Eratosthenes" algorithm, an ancient algorithm, but one that should push your computers to the limits.

## Instructions
Your task is to create a program that implements the Sieve of Eratosthenes algorithm to find all prime numbers less than or equal to a given number.

A prime number is a number larger than 1 that is only divisible by 1 and itself.
For example, 2, 3, 5, 7, 11, and 13 are prime numbers.
By contrast, 6 is _not_ a prime number as it not only divisible by 1 and itself, but also by 2 and 3.

To use the Sieve of Eratosthenes, first, write out all the numbers from 2 up to and including your given number.
Then, follow these steps:

1. Find the next unmarked number (skipping over marked numbers).
   This is a prime number.
2. Mark all the multiples of that prime number as **not** prime.

Repeat the steps until you've gone through every number.
At the end, all the unmarked numbers are prime.

> [!NOTE]
> The Sieve of Eratosthenes marks off multiples of each prime using addition (repeatedly adding the prime) or multiplication (directly computing its multiples), rather than checking each number for divisibility.
>
> The tests don't check that you've implemented the algorithm, only that you've come up with the correct primes.

### Example

Let's say you're finding the primes less than or equal to 10.

- Write out 2, 3, 4, 5, 6, 7, 8, 9, 10, leaving them all unmarked.

  ```text
  2 3 4 5 6 7 8 9 10
  ```

- 2 is unmarked and is therefore a prime.
  Mark 4, 6, 8 and 10 as "not prime".

  ```text
  2 3 [4] 5 [6] 7 [8] 9 [10]
  ↑
  ```

- 3 is unmarked and is therefore a prime.
  Mark 6 and 9 as not prime _(marking 6 is optional - as it's already been marked)_.

  ```text
  2 3 [4] 5 [6] 7 [8] [9] [10]
    ↑
  ```

- 4 is marked as "not prime", so we skip over it.

  ```text
  2 3 [4] 5 [6] 7 [8] [9] [10]
       ↑
  ```

- 5 is unmarked and is therefore a prime.
  Mark 10 as not prime _(optional - as it's already been marked)_.

  ```text
  2 3 [4] 5 [6] 7 [8] [9] [10]
          ↑
  ```

- 6 is marked as "not prime", so we skip over it.

  ```text
  2 3 [4] 5 [6] 7 [8] [9] [10]
             ↑
  ```

- 7 is unmarked and is therefore a prime.

  ```text
  2 3 [4] 5 [6] 7 [8] [9] [10]
                ↑
  ```

- 8 is marked as "not prime", so we skip over it.

  ```text
  2 3 [4] 5 [6] 7 [8] [9] [10]
                   ↑
  ```

- 9 is marked as "not prime", so we skip over it.

  ```text
  2 3 [4] 5 [6] 7 [8] [9] [10]
                       ↑
  ```

- 10 is marked as "not prime", so we stop as there are no more numbers to check.

  ```text
  2 3 [4] 5 [6] 7 [8] [9] [10]
                           ↑
  ```

You've examined all the numbers and found that 2, 3, 5, and 7 are still unmarked, meaning they're the primes less than or equal to 10.

## You get
`limit` — the largest number to consider, included:

```python
solve(10)
```

It may be as small as `0` or `1` (no primes at all) and as large as a few thousand.

> [!NOTE]
> Exercism's stub is `def primes(limit)`. Here the function is `solve(limit)`; nothing else about the task changes.

## You return
A `list` of `int` in ascending order — every prime `p` with `2 <= p <= limit`.

```python
solve(10)  # -> [2, 3, 5, 7]
solve(1)   # -> []
```

## Rules
- the limit is inclusive: `solve(13)` ends with `13`, because 13 is prime
- the result is ascending, with no duplicates, and it is a `list` — a set is not accepted, because a set has no order
- `limit` below 2 gives `[]`
- neither 0 nor 1 is ever in the result

```python
solve(1)   # -> []
solve(2)   # -> [2]
solve(13)  # -> [2, 3, 5, 7, 11, 13]
solve(30)  # -> [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
```

> [!WARNING]
> `solve(0)` and `solve(1)` must not blow up. A sieve that starts by writing `marked[0] = marked[1] = False` into a list sized `limit + 1` raises `IndexError` when `limit` is 0 — handle the small limits before you build anything.

## Read first
- [Sets](https://docs.python.org/3/tutorial/datastructures.html#sets) — a set of "already crossed out" numbers is one natural way to hold the marks
- [range() with a step](https://docs.python.org/3/library/stdtypes.html#range) — `range(p * p, limit + 1, p)` is every multiple of `p`, produced by addition
- [enumerate()](https://docs.python.org/3/library/functions.html#enumerate) — pairs a flag with the number it belongs to when you collect the survivors
- [Set difference](https://docs.python.org/3/library/stdtypes.html#frozenset.difference) — "everything from 2 to the limit, minus the crossed-out ones", in one expression

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Hints
### Hint 1
Do the limit-10 example by hand with a pen: write 2 to 10 in a row and cross out as the instructions say. Notice what you are *not* doing — you never ask "is 9 divisible by anything?". You only ever cross out multiples of numbers you have already accepted. Decide how you will hold the marks: a set of crossed-out numbers, or a list of booleans indexed by the number itself.
### Hint 2
Walk the numbers upwards from 2. If the current number is still unmarked it is prime, so mark its multiples. Start marking at the number squared rather than at twice the number — everything below that has already been crossed out by a smaller prime — and step by the number itself, so `range` does the multiplication for you. You can stop the outer walk once the number squared passes the limit; from there on nothing new gets marked, and every number still standing is prime. At the end, collect the numbers from 2 to the limit that were never marked, in order.
### Hint 3
Different data, same "mark the impossible, keep the rest" shape — free ports in a range:

```python
allowed = range(8000, 8010)
taken = set()
for service_port in (8000, 8003):
    taken.update(range(service_port, 8010, 3))   # this service reserves every third port

free = [port for port in allowed if port not in taken]
free   # -> [8001, 8002, 8004, 8005, 8007, 8008]
```

No port is ever asked "are you free?" — the reservations are stamped in first, and the answer is whatever survives. `range(start, stop, step)` does the stamping without a multiplication in sight.
