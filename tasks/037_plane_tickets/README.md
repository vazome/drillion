---
title: generators — seat every passenger on the plane
difficulty: hard
tier: advanced
minutes: 15
prereqs: [35]
tags: [generators]
source: exercism/python concept/plane-tickets (MIT, adapted)
---
# generators — seat every passenger on the plane

*Generators — `yield`, laziness, and one generator feeding another.*

## Read first
- [Generators (the Python tutorial)](https://devdocs.io/python~3.14/tutorial/classes#generators) — a function with `yield` in it is a generator; calling it runs none of the body
- [yield expressions](https://devdocs.io/python~3.14/reference/expressions#yield-expressions) — what `yield` does to the function it appears in
- [Real Python: Introduction to generators](https://realpython.com/introduction-to-python-generators/) — `yield`, `next()`, and why laziness saves memory
- [Python Morsels: Iterators & Generators](https://www.pythonmorsels.com/iterators/) — the protocol underneath, in short form
- [Lazy evaluation (Wikipedia)](https://en.wikipedia.org/wiki/Lazy_evaluation) — the idea, outside Python
- [inspect.isgenerator()](https://devdocs.io/python~3.14/library/inspect#inspect.isgenerator) — the check the grader runs on three of your four functions

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
An airline runs ten thousand flights a day and still assigns seats by hand. The rule is simple — A, B, C, D across a row, rows counting up, no row 13 because passengers refuse it — but the seating plan must be produced on demand, one seat at a time, not built as a giant list for every aircraft in the fleet. That "produce the next one when asked" shape is exactly what a generator is for, and once the first one exists the rest of the system is generators feeding generators: letters feed seats, seats feed the passenger assignment, assigned seats feed the ticket codes. The same technique reads a 40 GB log file a line at a time, or pages an API without holding every page in memory.

## Introduction

A `generator` is a function or expression that returns a special type of [iterator][iterator] called a [`generator iterator`][generator-iterator].
`Generator-iterator`s are [lazy][lazy iterator]: they do not store their `values` in memory, but _generate_ their values when needed.

A generator function looks like any other function, but contains one or more [yield expressions][yield expression].
Each `yield` will suspend code execution, saving the current execution state (_including all local variables and try-statements_).
When the generator resumes, it picks up state from the suspension - unlike regular functions which reset with every call.

### Constructing a generator

Generators are constructed much like other looping or recursive functions, but require a [`yield` expression](#the-yield-expression), which we will explore in depth a bit later.

An example is a function that returns the _squares_ from a given list of numbers.
As currently written, all input must be processed before any values can be returned:

```python
>>> def squares(list_of_numbers):
...     squares = []
...     for number in list_of_numbers:
...         squares.append(number ** 2)
...     return squares
```

You can convert that function into a generator like this:

```python
>>> def squares_generator(list_of_numbers):
...     for number in list_of_numbers:
...         yield number ** 2
```

The rationale behind this is that you use a generator when you do not need to produce all the values _at once_.
This saves memory and processing power, since only the value you are _currently working on_ is calculated.

### Using a generator

Generators may be used in place of most `iterables` in Python.
This includes _functions_ or _objects_ that require an `iterable`/`iterator` as an argument.

To use the `squares_generator()` generator:

```python
>>> squared_numbers = squares_generator([1, 2, 3, 4])

>>> for square in squared_numbers:
...     print(square)
...
1
4
9
16
```

Values within a `generator` can also be produced/accessed via the `next()` function.
`next()` calls the `__next__()` method of a generator-iterator object, "advancing" or evaluating the code up to its `yield` expression, which then "yields" or returns a value:

```python
>>> squared_numbers = squares_generator([1, 2])

>>> next(squared_numbers)
1
>>> next(squared_numbers)
4
```

When a `generator-iterator` is fully consumed and has no more values to return, it throws a `StopIteration` error.

```python
>>> next(squared_numbers)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
```

> [!NOTE]
> Generator-iterators are a special sub-set of [iterators][iterator].
> `Iterators` are the mechanism/protocol that enables looping over _iterables_.
> Generator-iterators and the iterators returned by common Python [`iterables`][iterables] act very similarly, but there are some important differences to note:
>
> - They are _[lazily evaluated][lazy evaluation]_; iteration is _one-way_ and there is no "backing up" to a previous value.
> - They are _consumed_ by iterating over the returned values; there is no resetting or saving in memory.
> - They are not sortable and cannot be reversed.
> - They are not sequence types, and _do not_ have `indexes`.
>   You cannot reference a previous or future value using addition or subtraction and you cannot use bracket (`[]`) notation or slicing.
> - They cannot be used with the `len()` function, as they have no length.
> - They can be _finite_ or _infinite_ - be careful when collecting all values from an _infinite_ `generator-iterator`!
>
> [iterator]: https://devdocs.io/python~3.14/glossary#term-iterator
> [iterables]: https://wiki.python.org/moin/Iterator
> [lazy evaluation]: https://en.wikipedia.org/wiki/Lazy_evaluation

### The yield expression

The [yield expression][yield expression] is very similar to the `return` expression.
_Unlike_ the `return` expression, `yield` gives up values to the caller at a _specific point_, suspending evaluation/return of any additional values until they are requested.
When `yield` is evaluated, it pauses the execution of the enclosing function and returns any values of the function _at that point in time_.
The function then _stays in scope_, and when `__next__()` is called, execution resumes until `yield` is encountered again.

> [!NOTE]
> Using `yield` expressions is prohibited outside of functions.

```python
>>> def infinite_sequence():
...     current_number = 0
...     while True:
...         yield current_number
...         current_number += 1

>>> lets_try = infinite_sequence()
>>> lets_try.__next__()
0
>>> lets_try.__next__()
1
```

### Why Create a Generator?

Generators are useful in a lot of applications.

When working with a potentially large collection of values, you might not want to put all of them into memory.
A generator can be used to work on larger data piece-by-piece, saving memory and improving performance.

Generators are also very helpful when a process or calculation is _complex_, _expensive_, or _infinite_:

```python
>>> def infinite_sequence():
...     current_number = 0
...     while True:
...         yield current_number
...         current_number += 1
```

Now whenever `__next__()` is called on the `infinite_sequence` object, it will return the _previous number_ + 1.

[generator-iterator]: https://devdocs.io/python~3.14/glossary#term-generator-iterator
[iterator]: https://devdocs.io/python~3.14/glossary#term-iterator
[lazy iterator]: https://en.wikipedia.org/wiki/Lazy_evaluation
[yield expression]: https://devdocs.io/python~3.14/reference/expressions#yield-expressions

## Instructions

Conda Airlines is the programming-world's biggest airline, with over 10,000 flights a day!

They are currently assigning all seats to passengers by hand; this will need to be automated.

They have asked _you_ to create software to automate passenger seat assignments.
They require your software to be memory efficient and performant.

### 1. Generate seat letters

Conda wants to generate seat letters for their airplanes.
An airplane is made of rows of seats.
Each row has _4 seats_.
The seats in each row are always named `A`, `B`, `C`, and `D`.
The first seat in the row is `A`, the second seat in the row is `B`, and so on.
After reaching `D`, it should start again with `A`.

Implement a function `generate_seat_letters(<number>)` that accepts an `int` that holds how many seat letters to be generated.
The function should then return an _iterable_ of seat letters.

```python
>>> letters = generate_seat_letters(4)
>>> next(letters)
"A"
>>> next(letters)
"B"
```

### 2. Generate seats

Conda wants a system that can generate a given number of seats for their airplanes.
Each airplane has _4 seats_ in each row.
The rows are defined using numbers, starting from `1` and going up.
The seats should be ordered, like: `1A`, `1B`, `1C`, `1D`, `2A`, `2B`, `2C`, `2D`, `3A`, `3B`, `3C`, `3D`, ...

Here is an example:

|      x      |  1  |  2  |
| :---------: | :-: | :-: |
|     Row     |  5  | 21  |
| Seat letter |  A  |  D  |
|   Result    | 5A  | 21D |

Many airlines do not have _row_ number 13 on their flights, due to superstition amongst passengers.
Conda Airlines also follows this convention, so make sure you _don't_ generate seats for _row_ number 13.

Implement a function `generate_seats(<number>)` that accepts an `int` that holds how many seats to be generated.
The function should then return an _iterable_ of seats given.

```python
>>> seats = generate_seats(10)
>>> next(seats)
"1A"
>>> next(seats)
"1B"
```

### 3. Assign seats to passengers

Now that you have a function that generates seats, you can use it to assign seats to passengers.

Implement a function `assign_seats(<passengers>)` that accepts a `list` of passenger names.
The function should then return a _dictionary_ of `passenger` as _key_, and `seat_number` as _value_.

```python
>>> passengers = ['Jerimiah', 'Eric', 'Bethany', 'Byte', 'SqueekyBoots', 'Bob']

>>> assign_seats(passengers)
{'Jerimiah': '1A', 'Eric': '1B', 'Bethany': '1C', 'Byte': '1D', 'SqueekyBoots': '2A', 'Bob': '2B'}
```

### 4. Ticket codes

Conda Airlines would like to have a unique code for each ticket.
Since they are a big airline, they have a lot of flights.
This means that there are multiple flights with the same seat number.
They want you to create a system that formulates a unique ticket that is a _12_ character long string.

This code begins with the `assigned_seat` followed by the `flight_id`.
The rest of the code is filled with `0s`.

Implement a function `generate_codes(<seat_numbers>, <flight_id>)` that accepts a `list` of `seat_numbers` and a `string` with the flight number.
The function should then return a `generator` that yields a `ticket_number`.

```python
>>> seat_numbers = ['1A', '17D']
>>> flight_id = 'CO1234'
>>> ticket_ids = generate_codes(seat_numbers, flight_id)

>>> next(ticket_ids)
'1ACO12340000'
>>> next(ticket_ids)
'17DCO1234000'
```

## You get
Nothing. `solve()` takes **no arguments**; the seat counts and passenger lists arrive as arguments to the functions you hand back.

> [!NOTE]
> Exercism asks for these four functions in one `generators.py`. Here there is one entry point: `solve()` returns a dict that hands all four to the grader, keyed by name. The functions themselves keep Exercism's names and signatures.

## You return
A dict with these four functions.

| key | parameters | returns |
| --- | --- | --- |
| `"generate_seat_letters"` | `number` — how many letters to produce | a **generator** yielding `"A"`, `"B"`, `"C"`, `"D"`, `"A"`, … `number` letters in total |
| `"generate_seats"` | `number` — how many seats to produce | a **generator** yielding `"1A"`, `"1B"`, `"1C"`, `"1D"`, `"2A"`, … `number` seats in total, with row 13 skipped entirely |
| `"assign_seats"` | `passengers` — a list of names | a plain `dict` mapping each name to its seat, in the order the names were given |
| `"generate_codes"` | `seat_numbers` — a list of seats; `flight_id` — a string like `"KL1022"` | a **generator** yielding one 12-character ticket code per seat |

```python
airline = solve()

letters = airline["generate_seat_letters"](4)
next(letters)                                  # -> "A"
next(letters)                                  # -> "B"
list(airline["generate_seats"](5))             # -> ["1A", "1B", "1C", "1D", "2A"]

airline["assign_seats"](["Jerimiah", "Eric", "Bethany", "Byte", "SqueekyBoots"])
# -> {"Jerimiah": "1A", "Eric": "1B", "Bethany": "1C", "Byte": "1D", "SqueekyBoots": "2A"}

list(airline["generate_codes"](["1A", "17D"], "CO1234"))
# -> ["1ACO12340000", "17DCO1234000"]
```

## Rules
- the dict keys are exactly the four strings above, and each value is the function **itself** — `{"generate_seats": generate_seats}`, no parentheses
- three of the four must return a **generator**, not a list: the grader calls `inspect.isgenerator()` on the result, and a function that builds a list and returns it fails even when the contents are right. A function containing `yield` returns a generator automatically
- `assign_seats` is the exception — it returns a real `dict`
- rows have four seats, lettered `A` `B` `C` `D`, and rows are numbered from 1
- **there is no row 13.** Row 12 is followed by row 14, and asking for 56 seats gives you rows 1–12, 14 and 15
- asking for `number` seats gives exactly `number` seats — the skipped row does not shorten the answer
- a ticket code is the seat, then the flight id, then as many `0`s as it takes to reach 12 characters: `"1A"` + `"CO1234"` is 8 characters, so four zeros follow

> [!WARNING]
> `generate_seats` and `generate_seat_letters` are graded on the *number* of items too, not just their values. `generate_seat_letters(5)` yields five letters — `A B C D A` — and `generate_seats(5)` yields `1A 1B 1C 1D 2A`.

## Exercism hints

### 1. Generate seat letters

- The returned value should be of _type_ `generator`.
- You can have a sequence of letters from `A` to `D` and cycle through them.
- Use `yield` to return the next letter.

### 2. Generate seats

- The returned value should be of _type_ `generator`.
- Row `13` should be skipped, so go from `12` to `14`.
- Keep in mind that the returned values should be ordered from low to high. `1A, 1B, 2A, ...`
- Here it might be good to reuse or call functions you have already defined.

### 3. Assign seats to passengers

- Make sure your seat numbers do not have any spaces in them.
- Here it might be good to reuse or call functions you have already defined.

### 4. Ticket codes

- You can use `len()` to get the length of a string.
- You can use `"<string>" * <int>` to repeat a string.

## Hints
### Hint 1
You do not build any lists here. Put `yield` inside a loop and the function stops being a normal function — calling it hands back a generator that runs the loop one step at a time, resuming where it left off. Start with the letters: four of them, cycling forever, and the remainder operator `%` is what makes a counter cycle. Then let the other functions call the ones you already wrote instead of repeating the rule.
### Hint 2
Shape of the work.

- `generate_seat_letters(number)` — keep the four letters in a list. Loop `for seat in range(number)` and `yield` the letter at index `seat % 4`.
- `generate_seats(number)` — you need a row number alongside the letter. Every fourth seat moves to the next row; when that lands on 13, move on again. Then `yield` the row and the letter joined into one string with an f-string, and let `generate_seat_letters` supply the letter so the cycling rule lives in exactly one place.
- `assign_seats(passengers)` — ask `generate_seats` for as many seats as there are passengers, then walk the two sequences side by side. One builtin pairs two iterables up for exactly this; build the dict from those pairs.
- `generate_codes(seat_numbers, flight_id)` — for each seat, glue the seat and the flight id together, measure the result with `len()`, and pad it out to 12 characters. Multiplying a one-character string by the shortfall gives you the padding in one step.
### Hint 3
Different data, same shape. Numbering pages of a report, skipping the cover:

```python
def page_labels(count):
    for page in range(count):
        yield f"p{page + 2}"          # page 1 is the cover, so start at 2

def stamped(labels, report_id):
    for label in labels:
        base = f"{label}-{report_id}"
        yield base + "." * (10 - len(base))

pages = page_labels(3)
next(pages)                            # -> 'p2'
list(page_labels(3))                   # -> ['p2', 'p3', 'p4']
list(stamped(["p2"], "Q3"))            # -> ['p2-Q3....']
```

Note that `page_labels(3)` on its own prints nothing and does no work — the loop body only runs once something asks for a value, which is the whole point of a generator.
