---
title: comparisons — blackjack hand decisions
difficulty: easy
tier: core
minutes: 15
prereqs: [93]
tags: [comparisons]
source: exercism/python concept/black-jack (MIT, adapted)
---
# comparisons — blackjack hand decisions

*Chained comparisons and `in` — the three decisions a blackjack player makes.*

## Read first
- [Comparisons in Python (language reference)](https://devdocs.io/python~3.14/reference/expressions#comparisons) — comparisons CHAIN: `8 < total < 12` is one expression, and the middle is evaluated once
- [Membership test operations](https://devdocs.io/python~3.14/reference/expressions#membership-test-operations) — `in` asks "is this a member of that", which reads better than a pile of `==` joined by `or`
- [Value comparisons](https://devdocs.io/python~3.14/reference/expressions#value-comparisons) — every comparison hands back `True` or `False`, so a function whose whole body is one comparison can simply return it; no `if` statement is needed
- [Comparisons in Python (stdtypes)](https://devdocs.io/python~3.14/library/stdtypes#comparisons) — the operator table
- [Sequence types](https://devdocs.io/python~3.14/library/stdtypes#sequence-types-list-tuple-range) — a tuple is the cheapest thing to ask `in` about
- [Conditional expressions](https://devdocs.io/python~3.14/reference/expressions#conditional-expressions) — `a if test else b`, for when a branch really is needed
- [Python basic operators (Tutorials Point)](https://www.tutorialspoint.com/python/python_basic_operators.htm) — a worked list with output

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
The scoring half of the casino's blackjack table is done — card values and rankings work. Now the table has to answer the three questions a player asks the moment their first two cards land: is this an instant win, may I split these into two hands, and may I double my bet? Each is a rule from the casino's rulebook, each is one line of comparisons, and each is the kind of rule that gets written wrong by summing when it should be checking membership.

## Introduction
### Comparisons

Python supports the following basic comparison operators:

| Operator | Operation                  | Description                                                               |
| -------- | -------------------------- | ------------------------------------------------------------------------- |
| `>`      | "greater than"             | `a > b` is `True` if `a` is **strictly** greater in value than `b`        |
| `<`      | "less than"                | `a < b` is `True` if `a` is **strictly** less in value than `b`           |
| `==`     | "equal to"                 | `a == b` is `True` if `a` is **strictly** equal to `b` in value           |
| `>=`     | "greater than or equal to" | `a >= b` is `True` if `a > b` OR `a == b` in value                        |
| `<=`     | "less than or equal to"    | `a <= b` is `True` if `a < b` or `a == b` in value                        |
| `!=`     | "not equal to"             | `a != b` is `True` if `a == b` is `False`                                 |
| `is`     | "identity"                 | `a is b` is `True` if **_and only if_** `a` and `b` are the same _object_ |
| `is not` | "negated identity"         | `a is not b` is `True` if `a` and `b` are **not** the same _object_       |
| `in`     | "containment test"         | `a in b` is `True` if `a` is member, subset, or element of `b`            |
| `not in` | "negated containment test" | `a not in b` is `True` if `a` is not a member, subset, or element of `b`  |

They all have the same priority (_which is higher than that of [Boolean operations][boolean operations], but lower than that of arithmetic or bitwise operations_).

### Comparison between different data types

Objects that are different types (_except numeric types_) never compare equal by default.
Non-identical instances of a `class` will also _**not**_ compare as equal unless the `class` defines special [rich comparison][rich comparisons] methods that customize the default `object` comparison behavior.
Customizing via `rich comparisons` will be covered in a follow-on exercise.
For (much) more detail on this topic, see [Value comparisons][value comparisons] in the Python documentation.

Numeric types are (mostly) an exception to this type matching rule.
An `integer` **can** be considered equal to a `float` (_or an [`octal`][octal] equal to a [`hexadecimal`][hex]_), as long as the types can be implicitly converted for comparison.

For the other numeric types in the Python standard library ([complex][complex numbers], [decimal][decimal numbers], [fractions][rational numbers]), comparison operators are defined where they "make sense" (_where implicit conversion does not change the outcome_), but throw a `TypeError` if the underlying objects cannot be accurately converted for comparison.
For more information on the rules that python uses for _numeric conversion_, see [arithmetic conversions][arithmetic conversions] in the Python documentation.

```python
>>> import fractions

# A string cannot be converted to an int.
>>> 17 == '17'
False

# An int can be converted to float for comparison.
>>> 17 == 17.0
True

# The fraction 6/3 can be converted to the int 2
# The int 2 can be converted to 0b10 in binary.
>>> 6/3 == 0b10
True

# An int can be converted to a complex number with a 0 imaginary part.
>>> 17 == complex(17)
True

# The fraction 2/5 can be converted to the float 0.4
>>> 0.4 == 2/5
True

>>> complex(2/5, 1/2) == complex(0.4, 0.5)
True
```

Any ordered comparison of a number to a `NaN` (_not a number_) type is `False`.
A confusing side effect of Python's `NaN` definition is that `NaN` never compares equal to `NaN`.

```python
>>> x = float('NaN')

>>> 3 < x
False

>>> x < 3
False

# NaN never compares equal to NaN
>>> x == x
False
```

### Comparing Strings

Unlike numbers, strings (`str`) are compared [_lexicographically_][lexographic order], using their individual Unicode code points (_the result of passing each code point in the `str` to the built-in function [`ord()`][ord], which returns an `int`_).
If all code points in both strings match and are _**in the same order**_, the two strings are considered equal.
This comparison is done in a 'pair-wise' fashion - first-to-first, second-to-second, etc.
In Python 3.x, `str` and `bytes` cannot be directly coerced/compared.

```python
>>> 'Python' > 'Rust'
False

>>> 'Python' > 'JavaScript'
True

# Examples with Mandarin.
# hello < goodbye
>>> '你好' < '再见'
True

# ord() of first characters
>>> ord('你'), ord('再')
(20320, 20877)

# ord() of second characters
>>> ord('好'), ord('见')
(22909, 35265)

# And with Korean words.
# Pretty < beautiful.
>>> '예쁜' < '아름다운'
False

>>> ord('예'), ord('아')
(50696, 50500)
```

### Comparison Chaining

Comparison operators can be chained _arbitrarily_ -- meaning that they can be used in any combination of any length.
Note that the evaluation of an expression takes place from `left` to `right`.

As an example, `x < y <= z` is equivalent to `x < y` `and` `y <= z`, except that `y` is evaluated **only once**.
In both cases, `z` is _not_ evaluated **at all** when `x < y` is found to be `False`.
This is often called `short-circuit evaluation` - the evaluation stops if the truth value of the expression has already been determined.

`Short circuiting` is supported by various boolean operators, functions, and also by comparison chaining in Python.
Unlike many other programming languages, including `C`, `C++`, `C#`, and `Java`, chained expressions like `a < b < c` in Python have a conventional [mathematical interpretation][three way boolean comparison] and precedence.

```python
>>> x = 2
>>> y = 5
>>> z = 10

>>> x < y < z
True

>>> x < y > z
False

>>> x > y < z
False
```

### Comparing object identity

The operators `is` and `is not` test for object [_identity_][object identity], as opposed to object _value_.
An object's identity never changes after creation and can be found by using the [`id()`][id function] function.

`<apple> is <orange>` evaluates to `True` if _**and only if**_ `id(<apple>)` == `id(<orange>)`.
`<apple> is not <orange>` yields the inverse.

Due to their singleton status, `None` and `NotImplemented` should always be compared to items using `is` and `is not`.
See the Python reference docs on [value comparisons][value comparisons none] and [PEP8][pep8 programming recommendations] for more details on this convention.

```python
>>> my_fav_numbers = [1, 2, 3]

>>> your_fav_numbers = my_fav_numbers

>>> my_fav_numbers is your_fav_numbers
True

# The returned id will differ by system and python version.
>>> id(my_fav_numbers)
4517478208

# your_fav_numbers is only an alias pointing to the original my_fav_numbers object.
# Assigning a new name does not create a new object.
>>> id(your_fav_numbers)
4517478208

>>> my_fav_numbers is not your_fav_numbers
False

>>> my_fav_numbers is not None
True

>>> my_fav_numbers is NotImplemented
False
```

### Membership comparisons

The operators `in` and `not in` test for _membership_.
`<fish> in <soup>` evaluates to `True` if `<fish>` is a member of `<soup>` (_if `<fish>` is a subset of or is contained within `<soup>`_), and evaluates `False` otherwise.
`<fish> not in <soup>` returns the negation, or _opposite of_ `<fish> in <soup>`.

For string and bytes types, `<name> in <fullname>` is `True` _**if and only if**_ `<name>` is a substring of `<fullname>`.

```python
# A set of lucky numbers.
>>> lucky_numbers = {11, 22, 33}
>>> 22 in lucky_numbers
True

>>> 44 in lucky_numbers
False

# A dictionary of employee information.
>>> employee = {'name': 'John Doe',
                'id': 67826, 'age': 33,
                'title': 'ceo'}

# Checking for the membership of certain keys.
>>> 'age' in employee
True

>>> 33 in employee
False

>>> 'lastname' not in employee
True

# Checking for substring membership
>>> name = 'Super Batman'
>>> 'Bat' in name
True

>>> 'Batwoman' in name
False
```

[arithmetic conversions]: https://devdocs.io/python~3.14/reference/expressions#arithmetic-conversions
[boolean operations]: https://devdocs.io/python~3.14/library/stdtypes#boolean-operations-and-or-not
[complex numbers]: https://devdocs.io/python~3.14/library/functions#complex
[decimal numbers]: https://devdocs.io/python~3.14/library/decimal
[hex]: https://devdocs.io/python~3.14/library/functions#hex
[id function]: https://devdocs.io/python~3.14/library/functions#id
[lexographic order]: https://en.wikipedia.org/wiki/Lexicographic_order
[object identity]: https://devdocs.io/python~3.14/reference/datamodel
[octal]: https://devdocs.io/python~3.14/library/functions#oct
[ord]: https://devdocs.io/python~3.14/library/functions#ord
[pep8 programming recommendations]: https://pep8.org/#programming-recommendations
[rational numbers]: https://devdocs.io/python~3.14/library/fractions
[rich comparisons]: https://devdocs.io/python~3.14/reference/datamodel#object.__lt__
[three way boolean comparison]: https://en.wikipedia.org/wiki/Three-way_comparison
[value comparisons none]: https://devdocs.io/python~3.14/reference/expressions#value-comparisons
[value comparisons]: https://devdocs.io/python~3.14/reference/expressions#value-comparisons

## Instructions
In this exercise you are going to implement some rules of [Blackjack][blackjack],
such as the way the game is played and scored.

**Note** : In this exercise, _`A`_ means ace, _`J`_ means jack, _`Q`_ means queen, and _`K`_ means king.
Jokers are discarded.
A [standard French-suited 52-card deck][standard_deck] is assumed, but in most versions, several decks are shuffled together for play.

### 1. Calculate the value of a card

In Blackjack, it is up to each individual player if an ace is worth 1 or 11 points (_more on that later_).
Face cards (`J`, `Q`, `K`) are scored at 10 points and any other card is worth its "pip" (_numerical_) value.

Define the `value_of_card(<card>)` function with parameter `card`.
The function should return the _numerical value_ of the passed-in card string.
Since an ace can take on multiple values (1 **or** 11), this function should fix the value of an ace card at 1 for the time being.
Later on, you will implement a function to determine the value of an ace card, given an existing hand.

```python
>>> value_of_card('K')
10

>>> value_of_card('4')
4

>>> value_of_card('A')
1
```

### 2. Determine which card has a higher value

Define the `higher_card(<card_one>, <card_two>)` function having parameters `card_one` and `card_two`.
For scoring purposes, the value of `J`, `Q` or `K` is 10.
The function should return which card has the higher value for scoring.
If both cards have an equal value, return both.
Returning both cards can be done by using a comma in the `return` statement:

```python
# Using a comma in a return creates a Tuple.  Tuples will be covered in a later exercise.
>>> def returning_two_values(value_one, value_two):
        return value_one, value_two

>>> returning_two_values('K', '3')
('K', '3')
```

An ace can take on multiple values, so we will fix `A` cards to a value of 1 for this task.

```python
>>> higher_card('K', '10')
('K', '10')

>>> higher_card('4', '6')
'6'

>>> higher_card('K', 'A')
'K'
```

### 3. Calculate the value of an ace

As mentioned before, an ace can be worth _either_ 1 **or** 11 points.
Players try to get as close as possible to a score of 21, without going _over_ 21 (_going "bust"_).

Define the `value_of_ace(<card_one>, <card_two>)` function with parameters `card_one` and `card_two`, which are a pair of cards already in the hand _before_ getting an ace card.
Your function will have to decide if the upcoming ace will get a value of 1 or a value of 11, and return that value.
Remember: the value of the hand with the ace needs to be as high as possible _without_ going over 21.

**Hint**: if we already have an ace in hand, then the value for the upcoming ace would be 1.

```python
>>> value_of_ace('6', 'K')
1

>>> value_of_ace('7', '3')
11
```

### 4. Determine a "Natural" or "Blackjack" Hand

If a player is dealt an ace (`A`) and a ten-card (10, `K`, `Q`, or `J`) as their first two cards, then the player has a score of 21.
This is known as a **blackjack** hand.

Define the `is_blackjack(<card_one>, <card_two>)` function with parameters `card_one` and `card_two`, which are a pair of cards.
Determine if the two-card hand is a **blackjack**, and return the boolean `True` if it is, `False` otherwise.

**Note** : The score _calculation_ can be done in many ways.
But if possible, we'd like you to check if there is an ace and a ten-card **_in_** the hand (_or at a certain position_), as opposed to _summing_ the hand values.

```python
>>> is_blackjack('A', 'K')
True

>>> is_blackjack('10', '9')
False
```

### 5. Splitting pairs

If the first two cards in a hand are of the same value (_for example, two sixes or a `Q` and `K`_), a player may choose to treat them as two separate hands.
This is known as "splitting pairs".

Define the `can_split_pairs(<card_one>, <card_two>)` function with parameters `card_one` and `card_two`, which are a pair of cards.
Determine if this two-card hand can be split into two pairs.
If the hand can be split, return the boolean `True` otherwise, return `False`

```python
>>> can_split_pairs('Q', 'K')
True

>>> can_split_pairs('10', 'A')
False
```

### 6. Doubling down

When the original two cards dealt total 9, 10, or 11 points, a player can place an additional bet equal to their original bet.
This is known as "doubling down".

Define the `can_double_down(<card_one>, <card_two>)` function with parameters `card_one` and `card_two`, which are a pair of cards.
Determine if the two-card hand can be "doubled down", and return the boolean `True` if it can, `False` otherwise.

```python
>>> can_double_down('A', '9')
True

>>> can_double_down('10', '2')
False
```

[blackjack]: https://bicyclecards.com/how-to-play/blackjack/
[standard_deck]: https://en.wikipedia.org/wiki/Standard_52-card_deck

## You get
`value_of_card` is already written for you above the stub, marked `# given — do not edit` — use it, do not rewrite it. Cards arrive as strings, always one of: `'2' '3' '4' '5' '6' '7' '8' '9' '10' 'J' 'Q' 'K' 'A'`.

> [!NOTE]
> Exercism asks for all six functions in one `black_jack.py`. Here the task is split in two: tasks 1–3 are task `093_black_jack`, and **this task covers tasks 4–6**. And there is one entry point: `solve()` takes **no arguments** and returns a dict that hands your three functions to the grader, keyed by name.

## You return
A dict with these three functions, all returning `True` or `False`.

| key | parameters | returns `True` when |
| --- | --- | --- |
| `"is_blackjack"` | `card_one`, `card_two` — the two cards dealt first | the hand is a "blackjack" (or "natural"): an ace together with any ten-card (`'10'`, `'J'`, `'Q'` or `'K'`) |
| `"can_split_pairs"` | `card_one`, `card_two` | the two cards have the same scoring value, so the player may split the hand into two separate hands. Two sixes qualify; so do a queen and a king, because both score 10 |
| `"can_double_down"` | `card_one`, `card_two` | the two cards total 9, 10 or 11 points, counting an ace as 1, so the player may double their bet |

```python
hand = solve()
hand["is_blackjack"]('A', 'K')      # -> True   (ace plus a ten-card)
hand["is_blackjack"]('A', 'A')      # -> False  (an ace is not a ten-card)
hand["can_split_pairs"]('Q', 'K')   # -> True   (both score 10)
hand["can_split_pairs"]('10', 'A')  # -> False  (10 against 1)
hand["can_double_down"]('A', '9')   # -> True   (1 + 9 = 10, inside 9..11)
hand["can_double_down"]('10', '2')  # -> False  (12 is one too many)
```

## Rules
- this task implements **Exercism tasks 4, 5 and 6 only** — `value_of_card`, `higher_card` and `value_of_ace` belong to task `093_black_jack`
- the dict keys are exactly the three strings above, and each value is the function itself — no parentheses
- all three return booleans — the tests compare with `==`, so `1`/`0` would pass here, but neighbouring tasks check `is True`; write `True`/`False`
- the casino wants `is_blackjack` checked by looking for an ace AND a ten-card in the hand, not by adding the hand up to 21

## Exercism hints

# General

[The Python comparisons tutorial][python comparisons tutorial] and [Python comparisons examples][python comparisons examples] are a great introduction covering the content of this exercise.

### 1. Calculate the value of a card

- You can use the equality comparison operator `==` to determine if a card is an ace card: `card == 'A'`.
- You can use the containment operator `in` to determine if a substring is contained inside a string: `'Q' in 'KJQ'`.
- You can use the [`int` constructor][int constructor] to convert a `str` of an `int` to an `int`: `int('13')`.

### 2. Determine which card has a higher value

- Once you have defined the `value_of_card` function, you can call it from other functions.
- You can use the value comparison operators `>` and `<` to determine if specific cards are _greater than_ or _less than_ a given value: `3 < 12`.
- You can use the equality comparison operator `==` to determine if two values are equal to one another.

### 3. Calculate the value of an ace

- Once you have defined the `value_of_card` function, you can call it from other functions.
- You can use the order comparison operator `>` to decide the appropriate course of action here.

### 4. Determine Blackjack

- Remember, you can use the [`if`/`elif`/`else` syntax][if syntax] to handle different combinations of cards.
- You can chain BOTH comparison operators and boolean operators _arbitrarily_: `y < z < x` or `(y or z) and (x or z)`
- You can reuse the already implemented `value_of_card` function.

### 5. Splitting pairs

- You can reuse the already implemented `value_of_card` function.
- You can handle the `A` case (when at least one of the cards in an ace) separately.

### 6. Doubling down

- An `A` scored at 11 will never allow doubling down if there are two cards in the hand.
- Given the first point, you _should_ be able to reuse the already implemented `value_of_card` function.
- You can chain comparison operators _arbitrarily_: `y < z < x`.
- You can use the [conditional expression][conditional expression] (_sometimes called a "ternary operator"_)
  to shorten simple `if`/`else` statements: `13 if letter == 'M' else 3`.

[conditional expression]: https://devdocs.io/python~3.14/reference/expressions#conditional-expressions
[if syntax]: https://devdocs.io/python~3.14/tutorial/controlflow#if-statements
[int constructor]: https://devdocs.io/python~3.14/library/functions#int
[python comparisons examples]: https://www.tutorialspoint.com/python/comparison_operators_example.htm
[python comparisons tutorial]: https://devdocs.io/python~3.14/reference/expressions#comparisons

## Hints
### Hint 1
Each of the three is a single expression that is already `True` or `False` — you can return the comparison itself, no `if` and no `return True` / `return False`. All three may reuse the already-implemented `value_of_card`. For the first one, resist adding the two cards up: the rule is about WHICH two cards are present, and one of them is not identified by its score.
### Hint 2
Blackjack: one of the two cards must be the ace and one of them must score 10 — two separate membership questions joined with `and`. You can chain BOTH comparison operators and boolean operators arbitrarily: `y < z < x`, or `(y or z) and (x or z)`. Watch the ace-with-ace case: it has an ace, but no ten-card, so it must come out `False`.

Splitting pairs is one `==` between the two card values; you can handle the `'A'` case separately if that reads more clearly.

Doubling down: 9, 10 or 11 is one range, and Python lets you write a range as a single chained comparison with the total in the middle. An `'A'` scored at 11 would never allow doubling down with two cards in hand, which is exactly why `value_of_card` scoring it as 1 is the version you want here.
### Hint 3
Different data, same shape. A delivery may go by bike when it has a small parcel and a city address, and it is 'oversize' when the two side lengths add up to somewhere between 100 and 150 cm:

```python
def by_bike(a, b):
    return 'small' in (a, b) and 'city' in (a, b)
def oversize(a, b):
    return 99 < side(a) + side(b) < 151
```

First one asks about membership twice; the second one chains a range around a sum. `'small' in (a, b)` is short for `a == 'small' or b == 'small'`.
