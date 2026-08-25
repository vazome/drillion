---
title: numbers — whole bills, leftovers and the booth's cut
minutes: 15
prereqs: [200, 206]
tags: [exercism, numbers, core]
source: exercism/python concept/currency-exchange (MIT, adapted)
---
# numbers — whole bills, leftovers and the booth's cut

*Floor division and modulo — whole bills out, the booth keeps the remainder.*

## Why
Chandler's exchange calculator now has to face the counter clerk. A booth pays out in notes, not in exact amounts: ask for 127.50 in 20s and you get six notes — 120 — and the booth quietly keeps the 7.50. On top of that the booth adds a "spread", a percentage on the exchange rate that is its fee. Chandler wants to see, before he hands over any cash, exactly how many notes come back, exactly how much the booth pockets, and the final figure once the spread is in. Everything below is floor division and remainders, which is the same arithmetic as pagination, batch sizes and disk blocks.

## Introduction
### Numbers

There are three different kinds of built-in numbers in Python : `ints`, `floats`, and `complex`. However, in this exercise you'll be dealing only with `ints` and `floats`.

#### ints

`ints` are whole numbers. e.g. `1234`, `-10`, `20201278`.

Integers in Python have [arbitrary precision][arbitrary-precision] -- the number of digits is limited only by the available memory of the host system.

#### floats

`floats` are numbers containing a decimal point. e.g. `0.0`,`3.14`,`-9.01`.

Floating point numbers are usually implemented in Python using a `double` in C (_15 decimal places of precision_), but will vary in representation based on the host system and other implementation details. This can create some surprises when working with floats, but is "good enough" for most situations.

You can see more details and discussions in the following resources:

- [Python numeric type documentation][numeric-type-docs]
- [The Python Tutorial][floating point math]
- [Documentation for `int()` built in][`int()` built in]
- [Documentation for `float()` built in][`float()` built in]
- [0.30000000000000004.com][0.30000000000000004.com]

### Arithmetic

Python fully supports arithmetic between `ints` and `floats`. It will convert narrower numbers to match their less narrow counterparts when used with the binary arithmetic operators (`+`, `-`, `*`, `/`, `//`, and `%`).

Python considers `ints` narrower than `floats`. So, using a float in an expression ensures the result will be a float too. However, when doing division, the result will always be a float, even if only integers are used.

```python
# The int is widened to a float here, and a float type is returned.
>>> 3 + 4.0
7.0
>>> 3 * 4.0
12.0
>>> 3 - 2.0
1.0
# Division always returns a float.
>>> 6 / 2
3.0
>>> 7 / 4
1.75
# Calculating remainders.
>>> 7 % 4
3
>>> 2 % 4
2
>>> 12.75 % 3
0.75
```

If an int result is needed, you can use `//` to truncate the result.

```python
>>> 6 // 2
3
>>> 7 // 4
1
```

To convert a float to an integer, you can use `int()`. To convert an integer to a float, you can use `float()`.

```python
>>> int(6 / 2)
3
>>> float(1 + 2)
3.0
```

[0.30000000000000004.com]: https://0.30000000000000004.com/
[`float()` built in]: https://docs.python.org/3/library/functions.html#float
[`int()` built in]: https://docs.python.org/3/library/functions.html#int
[arbitrary-precision]: https://en.wikipedia.org/wiki/Arbitrary-precision_arithmetic#:~:text=In%20computer%20science%2C%20arbitrary%2Dprecision,memory%20of%20the%20host%20system.
[floating point math]: https://docs.python.org/3.9/tutorial/floatingpoint.html
[numeric-type-docs]: https://docs.python.org/3/library/stdtypes.html#typesnumeric

## Instructions
Your friend Chandler plans to visit exotic countries all around the world. Sadly, Chandler's math skills aren't good. He's pretty worried about being scammed by currency exchanges during his trip - and he wants you to make a currency calculator for him. Here are his specifications for the app:

### 1. Estimate value after exchange

Create the `exchange_money()` function, taking 2 parameters:

1. `budget` : The amount of money you are planning to exchange.
2. `exchange_rate` : The amount of domestic currency equal to one unit of foreign currency.

This function should return the value of the exchanged currency.

**Note:** If your currency is USD and you want to exchange USD for EUR with an exchange rate of `1.20`, then `1.20 USD == 1 EUR`.

```python
>>> exchange_money(127.5, 1.2)
106.25
```

### 2. Calculate currency left after an exchange

Create the `get_change()` function, taking 2 parameters:

1. `budget` : Amount of money before exchange.
2. `exchanging_value` : Amount of money that is *taken* from the budget to be exchanged.

This function should return the amount of money that *is left* from the budget.

```python
>>> get_change(127.5, 120)
7.5
```

### 3. Calculate value of bills

Create the `get_value_of_bills()` function, taking 2 parameters:

1. `denomination` : The value of a single bill.
2. `number_of_bills` : The total number of bills.

This exchanging booth only deals in cash of certain increments.
The total you receive must be divisible by the value of one "bill" or unit, which can leave behind a fraction or remainder.
Your function should return only the total value of the bills (_excluding fractional amounts_) the booth would give back.
Unfortunately, the booth gets to keep the remainder/change as an added bonus.

```python
>>> get_value_of_bills(5, 128)
640
```

### 4. Calculate number of bills

Create the `get_number_of_bills()` function, taking `amount` and `denomination`.

This function should return the _number of currency bills_ that you can receive within the given _amount_.
In other words:  How many _whole bills_ of currency fit into the starting amount?
Remember -- you can only receive _whole bills_, not fractions of bills, so remember to divide accordingly.
Effectively, you are rounding _down_ to the nearest whole bill/denomination.

```python
>>> get_number_of_bills(127.5, 5)
25
```

### 5. Calculate leftover after exchanging into bills

Create the `get_leftover_of_bills()` function, taking `amount` and `denomination`.

This function should return the _leftover amount_ that cannot be returned from your starting _amount_ given the denomination of bills.
It is very important to know exactly how much the booth gets to keep.

```python
>>> get_leftover_of_bills(127.5, 20)
7.5
```

### 6. Calculate value after exchange

Create the `exchangeable_value()` function, taking `budget`, `exchange_rate`, `spread`, and `denomination`.

Parameter `spread` is the *percentage taken* as an exchange fee, written as an integer.
It needs to be converted to decimal by dividing it by 100.
If `1.00 EUR == 1.20 USD` and the *spread* is `10`, the actual exchange rate will be: `1.00 EUR == 1.32 USD` because 10% of 1.20 is 0.12, and this additional fee is added to the exchange.

This function should return the maximum value of the new currency after calculating the *exchange rate* plus the *spread*.
Remember that the currency *denomination* is a whole number, and cannot be sub-divided.

**Note:** Returned value should be `int` type.

```python
>>> exchangeable_value(127.25, 1.20, 10, 20)
80
>>> exchangeable_value(127.25, 1.20, 10, 5)
95
```

## You get
Nothing. Every number arrives as an argument to one of your functions.

> [!NOTE]
> Exercism asks for all six functions in one `exchange.py`. Here the exercise is split in two: tasks 1–3 are drill `206_currency_exchange`, and **this drill covers tasks 4–6**. And there is one entry point: `solve()` takes **no arguments** and returns a dict that hands your three functions to the grader, keyed by name.

## You return
A dict with these three functions.

| key | parameters | returns |
| --- | --- | --- |
| `"get_number_of_bills"` | `amount` (what is being paid out, e.g. `127.5`), `denomination` (the face value of one note, a whole number, e.g. `5`) | how many whole notes fit inside that amount — fractions of a note do not exist |
| `"get_leftover_of_bills"` | the same `amount` and `denomination` | the part of the amount that cannot be paid out in whole notes — the booth's bonus |
| `"exchangeable_value"` | `budget` (his money, e.g. `127.25`), `exchange_rate` (how much of his money one unit of theirs costs, e.g. `1.20`), `spread` (the booth's fee as a whole-number percentage of the rate, e.g. `10`), `denomination` (e.g. `20`) | the largest amount of foreign currency he can actually walk away with, in whole notes |

```python
booth = solve()
booth["get_number_of_bills"](127.5, 5)             # -> 25    (25 notes of 5 = 125)
booth["get_leftover_of_bills"](127.5, 20)          # -> 7.5   (6 notes of 20 = 120)
booth["exchangeable_value"](127.25, 1.20, 10, 20)  # -> 80
# 127.25 at the real rate of 1.32 is 96.4; in notes of 20 that is
# four notes, so 80 — the rest stays behind the counter
booth["exchangeable_value"](127.25, 1.20, 10, 5)   # -> 95
# same 96.4, but notes of 5 waste far less
```

## Rules
- this drill implements **Exercism tasks 4, 5 and 6 only** — `exchange_money`, `get_change` and `get_value_of_bills` belong to drill `206_currency_exchange`
- the dict keys are exactly the three strings above, and each value is the function itself — no parentheses
- amounts are never negative, `denomination` is a whole number of at least 1, and the rate plus its spread is never zero

The spread is a percentage OF THE RATE, added to it: rate 1.20 with a spread of 10 means 10% of 1.20 is 0.12, so the real rate Chandler pays is 1.32.

> [!WARNING]
> Types are graded. `get_number_of_bills` and `exchangeable_value` must return an `int` — the tests compare them with `==`, not approximately. `get_leftover_of_bills` keeps the fraction, so it stays a float when the amount is a float.

## Exercism hints

### General

- [The Python Numbers Tutorial][python-numbers-tutorial] and [Python numeric types][python-numeric-types] can be a great introduction.

### 1. Estimate value after exchange

- You can use the [division operator][division-operator] to get the value of exchanged currency.

### 2. Calculate currency left after an exchange

- You can use the [subtraction operator][subtraction-operator] to get the amount of change.

### 3. Calculate value of bills

- You can use the [multiplication operator][multiplication-operator] to get the value of bills.

### 4. Calculate number of bills

- You need to divide `amount` into `denomination`.
- You need to use type casting to `int` to get the exact number of bills.
- To remove decimal places from a `float`, you can convert it to `int`.

  **Note:** The `//` operator also does floor division. But, if the operand has `float`, the result is still `float`.

### 5. Calculate leftover after exchanging into bills

- You need to find the remainder of `amount` that does not equal a whole `denomination`.
- The Modulo operator `%` can help find the remainder.

### 6. Calculate value after exchange

- You need to calculate `spread` percent of `exchange_rate` using multiplication operator and add it to `exchange_rate` to get the exchanged currency.
- The actual rate needs to be computed. Remember to add exchange _rate_ and exchange _fee_.
- You can get exchanged money affected by commission by using divide operation and type casting to `int`.


[division-operator]: https://docs.python.org/3/tutorial/introduction.html#numbers
[multiplication-operator]: https://docs.python.org/3/tutorial/introduction.html#numbers
[python-numbers-tutorial]: https://docs.python.org/3/tutorial/introduction.html#numbers
[python-numeric-types]: https://docs.python.org/3.9/library/stdtypes.html#numeric-types-int-float-complex
[subtraction-operator]: https://docs.python.org/3/tutorial/introduction.html#numbers

## Read first
- [Arithmetic Operations](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex) — the operator table again, this time for `//` (floor division) and `%` (remainder)
- [integers](https://docs.python.org/3/library/functions.html#int) — `int()` truncates towards zero, which is NOT the same thing as rounding
- [floats](https://docs.python.org/3/library/functions.html#float) — mixing int and float in one expression: `//` on a float still hands back a float, so the type you get out depends on what you put in
- [Operator Precedence](https://docs.python.org/3/reference/expressions.html#operator-precedence) — `*` and `/` before `+`, so the spread needs its own parentheses or its own line
- [Decimals](https://docs.python.org/3/library/decimal.html#module-decimal) — the grown-up answer to money arithmetic
- [fractions](https://docs.python.org/3/library/fractions.html) — exact rational arithmetic
- [Python's numerical and mathematical modules](https://docs.python.org/3/library/numeric.html) — the wider shelf

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Hints
### Hint 1
Two operators do the whole first half. One tells you how many times a size fits completely inside an amount; the other tells you what is left over when it no longer fits. In Python they are two characters each (`//` and `%`), and they are neighbours in the operator table. The third function does not need new arithmetic — it is the exchange sum you already know, then the first two.

To remove the decimal places from a `float`, you can convert it to `int`. **Note:** the `//` operator also does floor division, but if either operand is a `float`, the result is still a `float`.
### Hint 2
Order for `exchangeable_value`: calculate `spread` percent of `exchange_rate` and add it to `exchange_rate` to get the actual rate; convert the budget at that rate; then reduce that figure to whole notes and turn the note count back into money. Notice the answer is a count times a face value, so it comes out as a whole number even though the budget and the rate were not. Watch the type: `//` on a float still gives a float, so if the spec asks for an `int`, one `int()` in the right place settles it.

For the leftover, you need the remainder of `amount` that does not make up a whole `denomination` — the modulo operator `%` finds it.
### Hint 3
Different data, same shape. Shipping 1000 items in boxes of 48:

```python
full_boxes = 1000 // 48      # -> 20   whole boxes
left_on_pallet = 1000 % 48   # -> 40   items with no box
shipped = full_boxes * 48    # -> 960  what actually leaves the warehouse
```

The booth is the warehouse: notes are boxes, the leftover never ships.
