---
title: loops — break a number into the primes it is built from
difficulty: hard
tier: core
minutes: 15
prereqs: [3, 18]
tags: [loops, numbers]
source: exercism/python practice/prime-factors (MIT, adapted)
---
# loops — break a number into the primes it is built from

*prime-factors — divide out each factor as often as it goes in, then move to the next candidate.*

## Read first
- [while statements](https://devdocs.io/python~3.14/reference/compound_stmts#the-while-statement) — the outer and inner loops here both run "until it stops working", not a fixed number of times
- [Floor division and modulo](https://devdocs.io/python~3.14/library/stdtypes#numeric-types-int-float-complex) — `%` asks "does it divide?", `//` does the dividing without turning the number into a float
- [math.isqrt()](https://devdocs.io/python~3.14/library/math#math.isqrt) — the exact integer square root, with none of the rounding surprises of `value ** 0.5`
- [list.append()](https://devdocs.io/python~3.14/library/stdtypes#mutable-sequence-types) — building the answer as you go

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
Two habits come out of this one, and both outlive the maths. The first is the nested loop where the inner loop keeps applying the *same* step until it stops working, and only then does the outer loop move on — the same shape as draining a queue before switching partitions, or retrying one host until it fails permanently. The second is knowing when a search can stop: a straightforward version of this function tests every divisor up to the number itself and takes minutes on a ten-digit input, while the same function with one extra condition finishes instantly. That gap between "correct" and "usable" is what an interviewer is probing when they ask about complexity.

## You get
`value` — one natural number, `1` or larger:

```python
solve(901255)
```

It can be as large as a few hundred billion, so the number of steps you take matters.

> [!NOTE]
> Exercism's stub is `def factors(value)`. Here the function is `solve(value)`; nothing else about the task changes.

## You return
A `list` of `int`, in ascending order, with repeats — multiply them all together and you get `value` back.

```python
solve(12)   # -> [2, 2, 3]
solve(1)    # -> []
```

## Rules
- every entry is a prime; a factor that divides several times appears several times
- the list is sorted ascending, which falls out for free if you try divisors in increasing order
- `1` has no prime factors, so `solve(1)` is the empty list
- a prime input returns a single-element list: `solve(2)` is `[2]`

```python
solve(2)       # -> [2]
solve(9)       # -> [3, 3]
solve(8)       # -> [2, 2, 2]
solve(625)     # -> [5, 5, 5, 5]
solve(901255)  # -> [5, 17, 23, 461]
```

> [!WARNING]
> One of the graded cases is `solve(93819012551)`, whose largest factor is `894119`. A loop that walks every candidate up to `value` will not finish before the runner gives up. Once no candidate up to the square root of what is left divides it, whatever is left is itself prime — that single check is the difference between a hundred thousand steps and a hundred billion.

## Hints
### Hint 1
Work the example for 60 on paper, writing down the two variables that change: the number still left to factor, and the divisor you are currently trying. Notice that you never have to check whether a divisor is prime — by the time you reach 4, every factor of 2 is already gone, so 4 cannot divide what remains. That is why the answer comes out prime without a primality test.
### Hint 2
Outer loop over candidate divisors starting at 2; inner loop that appends the divisor and shrinks the number *while* it divides evenly. Use `//=` and not `/=`, or you will be doing modulo on a float by the third iteration. Stop the outer loop as soon as the divisor squared is bigger than what is left; if what is left is still greater than 1 at that point, it is prime, so append it and finish. The trade is one extra `if` after the loop in exchange for a search that runs to the square root instead of to the number.
### Hint 3
Different data, same inner loop — pulling out every factor of two before doing anything else:

```python
def power_of_two_part(number):
    count = 0
    while number % 2 == 0:
        number //= 2
        count += 1
    return count, number

power_of_two_part(48)   # -> (4, 3)
power_of_two_part(7)    # -> (0, 7)
```

"Keep applying the same divisor until it no longer fits, then hand on what is left" is the whole inner loop. The task wraps this in an outer loop that tries 2, then 3, then 4, and so on — and each pass hands the shrunken number to the next.
