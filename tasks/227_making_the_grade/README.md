---
title: loops — rounding and counting exam scores
minutes: 12
prereqs: [200, 212, 215, 221, 224]
tags: [exercism, loops, core]
source: exercism/python concept/making-the-grade (MIT, adapted)
---
# loops — rounding and counting exam scores

*A `while` that drains a list, and two `for` loops — one that counts, one that collects.*

## Why
You are the teaching assistant with a pile of exam scores, and the three things you do with them are the three things every loop you write at work does: transform every item, count the items that match a rule, and collect the items that match a rule. Write them once as explicit loops with an explicit counter and an explicit results list, and you will recognise them instantly later — when they show up as a comprehension over a list of pods, a `sum()` over invoices, or a filter over a week of latency samples. This is the vocabulary task that makes those shorthands readable.

## Introduction
Python has two looping constructs.
`while` loops for _indefinite_ (uncounted) iteration and `for` loops for _definite_, (counted) iteration.
The keywords `break`, `continue`, and `else` help customize loop behavior.
`range()` and `enumerate()` help with loop counting and indexing.


### While

[`while`][while statement] loops will continue to execute as long as the `loop expression` or "test" evaluates to `True` in a [`boolean context`][truth value testing], terminating when it evaluates to `False`:

```python

# Lists are considered "truthy" in a boolean context if they
# contain one or more values, and "falsy" if they are empty.

>>> placeholders = ["spam", "ham", "eggs", "green_spam", "green_ham", "green_eggs"]

>>> while placeholders:
...     print(placeholders.pop(0))
...
'spam'
'ham'
'eggs'
'green_spam'
'green_ham'
'green_eggs'
```


### For

The basic [`for`][for statement] `loop` in Python is better described as a _`for each`_ which cycles through the values of any [iterable object][iterable], terminating when there are no values returned from calling [`next()`][next built-in]:

```python

>>> word_list = ["bird", "chicken", "barrel", "bongo"]

>>> for word in word_list:
...    if word.startswith("b"):
...        print(f"{word.title()} starts with a B.")
...    else:
...        print(f"{word.title()} doesn't start with a B.")
...
'Bird starts with a B.'
'Chicken doesn\'t start with a B.'
'Barrel starts with a B.'
'Bongo starts with a B.'
```


### Sequence Object range()

When there isn't a specific `iterable` given, the special [`range()`][range] sequence is used as a loop counter.
`range()` requires an `int` before which to `stop` the sequence, and can optionally take `start` and `step` parameters.
If no `start` number is provided, the sequence will begin with 0.
`range()` objects are **lazy** (_values are generated on request_), support all [common sequence operations][common sequence operations], and take up a fixed amount of memory, no matter how long the sequence specified.

```python
# Here we use range to produce some numbers, rather than creating a list of them in memory.
# The values will start with 1 and stop *before* 7

>>> for number in range(1, 7):
...    if number % 2 == 0:
...       print(f"{number} is even.")
...    else:
...       print(f"{number} is odd.")
'1 is odd.'
'2 is even.'
'3 is odd.'
'4 is even.'
'5 is odd.'
'6 is even.'

# range() can also take a *step* parameter.
# Here we use range to produce only the "odd" numbers, starting with 3 and stopping *before* 15.

>>> for number in range(3, 15, 2):
...    if number % 2 == 0:
...       print(f"{number} is even.")
...    else:
...       print(f"{number} is odd.")
...
'3 is odd.'
'5 is odd.'
'7 is odd.'
'9 is odd.'
'11 is odd.'
'13 is odd.'
```


### Values and Indexes with enumerate()

If both values and their indexes are needed, the built-in [`enumerate(<iterable>)`][enumerate] will return (`index`, `value`) pairs:

```python

>>> word_list = ["bird", "chicken", "barrel", "apple"]

# *index* and *word* are the loop variables.
# Loop variables can be any valid python name.

>>> for index, word in enumerate(word_list):
...    if word.startswith("b"):
...        print(f"{word.title()} (at index {index}) starts with a B.")
...    else:
...        print(f"{word.title()} (at index {index}) doesn't start with a B.")
...
'Bird (at index 0) starts with a B.'
'Chicken (at index 1) doesn\'t start with a B.'
'Barrel (at index 2) starts with a B.'
'Apple (at index 3) doesn\'t start with a B.'


# The same method can be used as a "lookup" for pairing items between two lists.
# Of course, if the lengths or indexes don't line up, this doesn't work.

>>> word_list = ["cat", "chicken", "barrel", "apple", "spinach"]
>>> category_list = ["mammal", "bird", "thing", "fruit", "vegetable"]

>>> for index, word in enumerate(word_list):
...    print(f"{word.title()} is in category: {category_list[index]}.")
...
'Cat is in category: mammal.'
'Chicken is in category: bird.'
'Barrel is in category: thing.'
'Apple is in category: fruit.'
'Spinach is in category: vegetable.'
```


### Altering Loop Behavior

The [`continue`][continue statement] keyword can be used to skip forward to the next iteration cycle:

```python
word_list = ["bird", "chicken", "barrel", "bongo", "sliver", "apple", "bear"]

# This will skip *bird*, at index 0
for index, word in enumerate(word_list):
    if index == 0:
        continue
    if word.startswith("b"):
        print(f"{word.title()} (at index {index}) starts with a b.")

'Barrel (at index 2) starts with a b.'
'Bongo (at index 3) starts with a b.'
'Bear (at index 6) starts with a b.'
```


The [`break`][break statement] (_like in many C-related languages_) keyword can be used to stop the iteration and "break out" of the innermost enclosing `loop`:

```python
>>>  word_list = ["bird", "chicken", "barrel", "bongo", "sliver", "apple"]

>>> for index, word in enumerate(word_list):
...    if word.startswith("b"):
...        print(f"{word.title()} (at index {index}) starts with a B.")
...    elif word == "sliver":
...       break
...    else:
...       print(f"{word.title()} doesn't start with a B.")
... print("loop broken.")
...
'Bird (at index 0) starts with a B.'
'Chicken doesn\'t start with a B.'
'Barrel (at index 2) starts with a B.'
'Bongo (at index 3) starts with a B.'
'loop broken.'
```

[break statement]: https://docs.python.org/3/reference/simple_stmts.html#the-break-statement
[common sequence operations]: https://docs.python.org/3/library/stdtypes.html#common-sequence-operations
[continue statement]: https://docs.python.org/3/reference/simple_stmts.html#the-continue-statement
[enumerate]: https://docs.python.org/3/library/functions.html#enumerate
[for statement]: https://docs.python.org/3/reference/compound_stmts.html#for
[iterable]: https://docs.python.org/3/glossary.html#term-iterable
[next built-in]: https://docs.python.org/3/library/functions.html#next
[range]: https://docs.python.org/3/library/stdtypes.html#range
[truth value testing]: https://docs.python.org/3/library/stdtypes.html#truth-value-testing
[while statement]: https://docs.python.org/3/reference/compound_stmts.html#the-while-statement

## Instructions
You're a teaching assistant correcting student exams.
Keeping track of results manually is getting both tedious and mistake-prone.
You decide to make things a little more interesting by putting together some functions to count and calculate results for the class.

### 1. Rounding Scores

While you can give "partial credit" on exam questions, overall exam scores have to be `int`s.
So before you can do anything else with the class scores, you need to go through the grades and turn any `float` scores into `int`s. Lucky for you, Python has the built-in [`round()`][round] function you can use.

Create the function `round_scores(student_scores)` that takes a `list` of `student_scores`.
This function should _consume_ the input `list` and `return` a new list with all the scores converted to `int`s.
The order of the scores in the resulting `list` is not important.

```python
>>> student_scores = [90.33, 40.5, 55.44, 70.05, 30.55, 25.45, 80.45, 95.3, 38.7, 40.3]
>>> round_scores(student_scores)
...
[40, 39, 95, 80, 25, 31, 70, 55, 40, 90]
```

### 2. Non-Passing Students

As you were grading the exam, you noticed some students weren't performing as well as you had hoped.
But you were distracted, and forgot to note exactly _how many_ students.

Create the function `count_failed_students(student_scores)` that takes a `list` of `student_scores`.
This function should count up the number of students who don't have passing scores and return that count as an integer.
A student needs a score greater than **40** to achieve a passing grade on the exam.

```python
>>> count_failed_students(student_scores=[90,40,55,70,30,25,80,95,38,40])
5
```

### 3. The "Best"

The teacher you're assisting wants to find the group of students who've performed "the best" on this exam.
What qualifies as "the best" fluctuates, so you need to find the student scores that are **greater than or equal to** the current threshold.

Create the function `above_threshold(student_scores, threshold)` taking `student_scores` (a `list` of grades), and `threshold` (the "top score" threshold) as parameters.
This function should return a `list` of all scores that are `>=` to `threshold`.

```python
>>> above_threshold(student_scores=[90,40,55,70,30,68,70,75,83,96], threshold=75)
[90,75,83,96]
```

### 4. Calculating Letter Grades

The teacher you are assisting likes to assign letter grades as well as numeric scores.
Since students rarely score 100 on an exam, the "letter grade" lower thresholds are calculated based on the highest score achieved, and increment evenly between the high score and the failing threshold of **<= 40**.

Create the function `letter_grades(highest)` that takes the "highest" score on the exam as an argument, and returns a `list` of lower score thresholds for each "American style" grade interval: `["D", "C", "B", "A"]`.


```python
"""Where the highest score is 100, and failing is <= 40.
       "F" <= 40
 41 <= "D" <= 55
 56 <= "C" <= 70
 71 <= "B" <= 85
 86 <= "A" <= 100
"""

>>> letter_grades(highest=100)
[41, 56, 71, 86]


"""Where the highest score is 88, and failing is <= 40.
       "F" <= 40
 41 <= "D" <= 52
 53 <= "C" <= 64
 65 <= "B" <= 76
 77 <= "A" <= 88
"""

>>> letter_grades(highest=88)
[41, 53, 65, 77]
```

### 5. Matching Names to Scores

You have a list of exam scores in descending order, and another list of student names also sorted in descending order by their exam scores.
You would like to match each student name with their exam score and print out an overall class ranking.

Create the function `student_ranking(student_scores, student_names)` with parameters `student_scores` and `student_names`.
Match each student name on the student_names `list` with their score from the student_scores `list`.
You can assume each argument `list` will be sorted from highest score(er) to lowest score(er).
The function should return a `list` of strings with the format `<rank>. <student name>: <student score>`.

```python
>>> student_scores = [100, 99, 90, 84, 66, 53, 47]
>>> student_names =  ['Joci', 'Sara','Kora','Jan','John','Bern', 'Fred']
>>> student_ranking(student_scores, student_names)
...
['1. Joci: 100', '2. Sara: 99', '3. Kora: 90', '4. Jan: 84', '5. John: 66', '6. Bern: 53', '7. Fred: 47']
```

### 6. A "Perfect" Score

Although a "perfect" score of 100 is rare on an exam, it is interesting to know if at least one student has achieved it.

Create the function `perfect_score(student_info)` with parameter `student_info`.
`student_info` is a `list` of lists containing the name and score of each student: `[["Charles", 90], ["Tony", 80]]`.
The function should `return` _the first_ `[<name>, <score>]` pair of the student who scored 100 on the exam.

If no 100 scores are found in `student_info`, an empty list `[]` should be returned.

```python
>>> perfect_score(student_info=[["Charles", 90], ["Tony", 80], ["Alex", 100]])
["Alex", 100]

>>> perfect_score(student_info=[["Charles", 90], ["Tony", 80]])
[]
```

[round]: https://docs.python.org/3/library/functions.html#round

## You get
Nothing. `solve()` takes **no arguments**; the grader calls your functions with the score lists.

> [!NOTE]
> Exercism asks for all six functions in one `loops.py`. Here the task is split in two: **this task covers tasks 1–3**, and tasks 4–6 are task `228_making_the_grade`. There is one entry point — `solve()` returns a dict that hands your three functions to the grader, keyed by name.

## You return
A dict with these three functions.

| key | parameters | returns |
| --- | --- | --- |
| `"round_scores"` | `student_scores` — a list of scores, some of them `float` (partial credit), possibly empty | a new list of `int`s, one per score; the order is **not** graded |
| `"count_failed_students"` | `student_scores` — a list of `int` scores | how many students did not pass, as an `int` |
| `"above_threshold"` | `student_scores`, `threshold` | a list of the scores that reach the threshold, in the order they appeared |

```python
grades = solve()
grades["round_scores"]([90.33, 40.5, 30.55, 38.7])
# -> [39, 31, 40, 90]    any order; note 40.5 rounds DOWN to 40
grades["count_failed_students"]([90, 40, 55, 70, 30, 25, 80, 95, 38, 40])
# -> 5
grades["above_threshold"]([90, 40, 55, 70, 30, 68, 70, 75, 83, 96], 75)
# -> [90, 75, 83, 96]
```

## Rules
- this task implements **Exercism tasks 1, 2 and 3 only** — `letter_grades`, `student_ranking` and `perfect_score` belong to task `228_making_the_grade`
- the dict keys are exactly the three strings above, and each value is the function itself — no parentheses
- a score **greater than 40** passes, so `40` itself is a failure and `41` is not
- `above_threshold` uses `>=`, keeps the original order and returns `[]` when nothing qualifies — including when the score list is empty
- `round_scores` order is not graded (both sides are sorted before comparing), but every score must appear exactly once, and an empty list in gives an empty list out
- rounding is the built-in `round()`, which is not the rounding you were taught at school: it sends halves to the nearest **even** integer, so `round(0.5)` is `0`, `round(1.5)` is `2` and `round(40.5)` is `40`

> [!WARNING]
> `round()` returns an `int` only when you call it with one argument. `round(40.5, 0)` gives the float `40.0`, and a list of floats fails a test that expects a list of ints.

## Exercism hints
### General

- [`while`][while-loops] loops are used for _indefinite_ (uncounted) iteration.
- [`for`][for-loops] loops are used for _definite_ (counted) iteration.
- The keywords [`break` and `continue`][control flow] help customize loop behavior.
- [`range(<start>, <stop>, <step>)`][range] can be used to generate a sequence for a loop counter.
- The built-in [`enumerate()`][enumerate] will return (`<value>`, `<index>`) pairs to iterate over.

Also being familiar with the following can help with completing the tasks:

- [`lists`][list]: indexing, nested lists, [`<list>.append()`][append and pop], [`<list>.pop()`][append and pop].
- [`str`][str]: `str()` constructor, using the `+` to concatenate strings, optionally, [`f-strings`][f-strings].

### 1. Rounding Scores

- `While` loops will continue to execute until their test condition evaluates to `False`.
- `<list>.pop()` will remove and return the last item in a `list`.
- Empty lists evaluate to `False` (most empty objects in Python are "Falsy")

### 2. Non-Passing Students

- There's no need to declare `loop` counters or `index` counters when iterating through an object using a `for` loop.
- A results counter does need to be set up and _incremented_ — you'll want to `return` the count of non-passing students when the loop terminates.

### 3. The "Best"

- There's no need to declare `loop` counters or `index` counters when iterating through an object using a `for` loop.
- Having an empty `list` to add the "best" marks to is helpful here.
- `<list>.append()` can help add things to the results `list`.

### 4. Calculating Letter Grades

- These are _lower thresholds_.  The _lower threshold_ for a "D" is a score of **41**, since an "F" is **<= 40**.
- [`range()`][range] can be helpful here to generate a sequence with the proper "F" -> "A" increments.
- [`round()`][round] without parameters should round off increments nicely.
- As with "the best" task, `<list>.append()` could be useful here to append items from `range()` into a results `list`.

### 5. Matching Names to Scores

- [`enumerate()`][enumerate] could be helpful here.
- If both lists are the same length and sorted the same way, could you use the `index` from one to retrieve a `value` from the other?

### 6. A "Perfect" Score

- There may be or may not be a student with a score of 100, and you can't return `[]` without checking **all** scores.
- The [`control flow`][control flow] statements `continue` and `break` may be useful here to move past unwanted values.

[append and pop]: https://docs.python.org/3/tutorial/datastructures.html#more-on-lists
[control flow]: https://docs.python.org/3/tutorial/controlflow.html#break-and-continue-statements-and-else-clauses-on-loops
[enumerate]: https://docs.python.org/3/library/functions.html#enumerate
[f-strings]: https://docs.python.org/3/reference/lexical_analysis.html#formatted-string-literals
[for-loops]: https://docs.python.org/3/tutorial/controlflow.html#for-statements
[list]: https://docs.python.org/3/library/stdtypes.html#list
[range]: https://docs.python.org/3/tutorial/controlflow.html#the-range-function
[round]: https://docs.python.org/3/library/functions.html#round
[str]: https://docs.python.org/3/library/stdtypes.html#str
[while-loops]: https://docs.python.org/3/reference/compound_stmts.html#the-while-statement

## Read first
- [`for` statements (Python tutorial)](https://docs.python.org/3/tutorial/controlflow.html#for-statements) — the `for each` loop, which is what Python's `for` really is
- [the `while` statement](https://docs.python.org/3/reference/compound_stmts.html#the-while-statement) — keeps going while its test is truthy; an empty list is falsy
- [truth value testing](https://docs.python.org/3/library/stdtypes.html#truth-value-testing) — why `while student_scores:` is a complete stopping condition
- [`round()`](https://docs.python.org/3/library/functions.html#round) — one argument gives you an `int`; two give you a `float`
- [more on lists](https://docs.python.org/3/tutorial/datastructures.html#more-on-lists) — `append()` and `pop()`, the two methods these three loops are built from
- [Loop Like a Native (Ned Batchelder)](https://nedbatchelder.com/text/iter.html) — the talk that explains why you almost never need an index
- [`for` loops in Python (Real Python)](https://realpython.com/python-for-loop/) — the long version, with `range()`
- [`while` loops in Python (Real Python)](https://realpython.com/python-while-loop/) — including the ways they fail to terminate
- [control flow for loops](https://docs.python.org/3/tutorial/controlflow.html#break-and-continue-statements-and-else-clauses-on-loops) — `break`, `continue` and the loop `else`, used properly in the next task

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Hints
### Hint 1
Three loops, three shapes, and it is worth naming the shape before you write it.

The first is a `while`: it keeps executing until its test condition evaluates to `False`, so something inside the loop has to make progress towards that or it never stops. The second sets up a results counter before the loop and increments it inside — you return the count once the loop has terminated. The third does the same thing with an empty list instead of a counter, and adds to it.
### Hint 2
Most empty objects in Python are falsy, lists included, so `while student_scores:` is already the whole condition — no length check, no index. `<list>.pop()` removes **and returns** the last item, which is both "make progress" and "here is the value to work on". Round it and append it to your results list.

The other two are plain `for score in student_scores:` — there is no need to declare a loop counter or an index counter when you iterate over an object with a `for` loop. In the counting one, `+= 1` inside an `if`; in the collecting one, `<list>.append(score)` inside an `if`. Both return the thing you set up *before* the loop, *after* the loop has finished — a `return` inside the loop stops it on the first item.

Mind the two boundaries: failing is *at or below* 40, and "the best" is *at or above* the threshold.
### Hint 3
Different data, same three shapes — file sizes and request latencies:

```python
sizes = [4.2, 8.9, 1.5]
whole = []
while sizes:
    whole.append(round(sizes.pop()))
whole                       # -> [2, 9, 4]     reversed, because pop() takes from the end

latencies = [120, 340, 95, 780]
slow = 0
for ms in latencies:
    if ms > 300:
        slow += 1
slow                        # -> 2

worst = []
for ms in latencies:
    if ms >= 300:
        worst.append(ms)
worst                       # -> [340, 780]    original order preserved
```

Note `round(1.5)` came out as `2` and `round(4.2)` as `4` — halves go to the nearest even number, everything else goes the way you expect.
