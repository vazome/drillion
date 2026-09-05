---
title: basics — Guido's lasagna kitchen timer
difficulty: easy
tier: core
minutes: 12
prereqs: []
tags: [functions]
source: exercism/python concept/guidos-gorgeous-lasagna (MIT, adapted)
---
# basics — Guido's lasagna kitchen timer

*Constants and small functions — the shape every Python module has.*

## Read first
- [Defining functions](https://devdocs.io/python~3.14/tutorial/controlflow#defining-functions) — `def`, parameters, `return`, and what a function hands back when you forget to return anything
- [Reuven Lerner: Understanding Python Assignment](https://lerner.co.il/2019/06/18/understanding-python-assignment/) — what `name = value` actually binds, and why `SCREAMING_SNAKE_CASE` is a promise to yourself, not a lock
- [Real Python: Commenting vs Documenting Code](https://realpython.com/documenting-python-code/#commenting-vs-documenting-code) — comments explain why, docstrings explain what
- [Python Morsels: Everything is an Object](https://www.pythonmorsels.com/everything-is-an-object/) — including functions, which is why one fits in a dict
- [Eli Bendersky: Python internals: how callables work](https://eli.thegreenplace.net/2012/03/23/python-internals-how-callables-work/) — what actually happens at `f()`
- [Sentdex (YouTube): Python 3 Programming Tutorial — Functions](https://www.youtube.com/watch?v=owglNL1KQf0) — the same material, spoken
- [dynamic typing and strong typing](https://stackoverflow.com/questions/11328920/is-python-strongly-typed) — why Python lets you rebind a name to another type but will not add an `int` to a `str`
- [type hints](https://devdocs.io/python~3.14/library/typing) — optional annotations, ignored at runtime
- [significant indentation](https://devdocs.io/python~3.14/reference/lexical_analysis#indentation) — the block rule that bites everyone once
- [DigitalOcean: How to Write Doctests in Python](https://www.digitalocean.com/community/tutorials/how-to-write-doctests-in-python) — docstrings that are also tests
- [Ned Batchelder: Is Python Interpreted or Compiled? Yes.](https://nedbatchelder.com/blog/201803/is_python_interpreted_or_compiled_yes.html) — what runs when you run a `.py`

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
You are writing the kitchen timer for a recipe app. The cook opens the lasagna recipe, tells the app how many layers they are building and how long the dish has already been in the oven, and the app has to answer two questions: "how much longer does it bake?" and "how long have I been at this?". The cookbook numbers never change — 40 minutes in the oven, 2 minutes of work per layer — so they belong in named constants at the top of the file, not copy-pasted into every calculation. That is the whole habit this task is about.

## Introduction
Python is a [dynamic and strongly][dynamic typing in python] typed programming language.
It employs both [duck typing][duck typing] and [gradual typing][gradual typing] via [type hints][type hints].

While Python supports many different programming _styles_, internally **everything in Python is an [object][everythings an object]**.
This includes numbers, strings, lists, and even functions.

We'll dig more into what all of that means as we continue through the track.

This first exercise introduces 4 major Python language features:
1.  Name Assignment (_variables and constants_),
2.  Functions (_the `def` keyword and the `return` keyword_),
3.  Comments, and
4.  Docstrings.

> [!NOTE]
> In general, content, tests, and analyzer tooling for the Python track follow the style conventions outlined in [PEP 8](https://www.python.org/dev/peps/pep-0008/) and [PEP 257](https://www.python.org/dev/peps/pep-0257/) for Python code style, with the additional (strong) suggestion that there be no single letter variable names or variables named ["_"][uses of _ in Python].
>
> On the Python track, [variables][variables] are always written in [`snake_case`][snake case], and constants in `SCREAMING_SNAKE_CASE`.

[variables]: https://realpython.com/python-variables/
[snake case]: https://en.wikipedia.org/wiki/Snake_case
[uses of _ in Python]: https://medium.com/better-programming/how-to-use-underscore-properly-in-python-37df5e05ba4c

### Name Assignment (Variables & Constants)

Programmers can bind [_names_][facts-and-myths-about-python-names] (also called _variables_) to any type of object using the assignment `=` operator: `<name> = <value>`.
A name can be reassigned (or re-bound) to different values (different object types) over its lifetime.

```python
>>> my_first_variable = 1  #<-- my_first_variable bound to an integer object of value one.
>>> my_first_variable = 2  #<-- my_first_variable re-assigned to integer value 2.

>>> print(type(my_first_variable))
<class 'int'>

>>> print(my_first_variable)
2

>>> my_first_variable = "Now, I'm a string." #<-- You may re-bind a name to a different object type and value.
>>> print(type(my_first_variable))
<class 'str'>

>>> my_first_variable = 'You can call me "str".' #<-- Strings can be declared using single or double quote marks.
>>> print(my_first_variable)
You can call me "str".
```

#### Constants

Constants are names meant to be assigned only once in a program.
They should be defined at a [module][module] (file) level, and are typically visible to all functions and classes in the program.
Using `SCREAMING_SNAKE_CASE` signals that the name should not be re-assigned, or its value mutated.

### Functions

The `def` keyword begins a [function definition][function definition].
Each function can have zero or more formal [parameters][parameters] in `()` parentheses, followed by a `:` colon.
Statements for the _body_ of the function begin on the line following `def` and must be _indented in a block_.

```python
# The body of a function is indented by 2 spaces, & prints the sum of the numbers.
def add_two_numbers(number_one, number_two):
  total = number_one + number_two
  print(total)

>>> add_two_numbers(3, 4)
7

# Inconsistent indentation in your code blocks will raise an error.
>>> def add_three_numbers_misformatted(number_one, number_two, number_three):
...     result = number_one + number_two + number_three   # This was indented by 4 spaces.
...    print(result)     #this was only indented by 3 spaces
...
...
  File "<stdin>", line 3
    print(result)
    ^
IndentationError: unindent does not match any outer indentation level
```

Functions _explicitly_ return a value or object via the [`return`][return] keyword:

```python
# Function definition on first line, explicit return used on final line.
>>> def add_two_numbers(number_one, number_two):
        return number_one + number_two

# Calling the function in the Python shell returns the sum of the numbers.
>>> add_two_numbers(3, 4)
7

# Assigning the function call to a variable and printing it
# will also return the value.
>>> sum_with_return = add_two_numbers(5, 6)
>>> print(sum_with_return)
11
```

Functions that do not have an _explicit_ expression following a `return` will _implicitly_ return the [`None`][none] object.
The details of `None` will be covered in a later exercise.
For the purposes of this exercise and explanation, `None` is a placeholder that represents nothing, or null:

```python

# This function will return `None`
def square_a_number(number):
    square = number * number
    return # <-- note that this return is not followed by an expression

# Calling the function in the Python shell appears
# to not return anything at all.
>>> square_a_number(2)
>>>

# Using print() with the function call shows that
# the function is actually returning the **None** object.
>>> print(square_a_number(2))
None
```

Functions that omit `return` will also  _implicitly_ return the [`None`][none] object.
This means that if you do not use `return` in a function, Python will return the `None` object for you.

```python
# This function omits a return keyword altogether.
def add_two_numbers(number_one, number_two):
  result = number_one + number_two

>>> add_two_numbers(5, 7)
>>> print(add_two_numbers(5, 7))
None

# Assigning the function call to a variable and printing
# the variable will also show None.
>>> sum_without_return = add_two_numbers(5, 6)
>>> print(sum_without_return)
None
```

#### Calling Functions

Functions are [_called_][calls] or invoked using their name followed by `()`.
Dot (`.`) notation is used for calling functions defined inside a class or module.

```python
>>> def raise_to_power(number, power):
...     return number ** power
...

>>> raise_to_power(3,3) # <--Invoking the function with the arguments 3 and 3.
27

# A mismatch between the number of parameters and the number of arguments will raise an error.
>>> raise_to_power(4,)
...
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: raise_to_power() missing 1 required positional argument: 'power'

# Calling methods or functions in classes and modules.
>>> start_text = "my silly sentence for examples."
>>> str.upper(start_text)  # <--Calling the upper() method from the built-in str class on start_text.
'MY SILLY SENTENCE FOR EXAMPLES.'

# Importing the math module
>>> import math

>>> math.pow(2,4)  # <--Calling the pow() function from the math module.
16.0
```

### Comments

[Comments][comments] in Python start with a `#` that is not part of a string, and end at line termination.
Unlike many other programming languages, Python **does not support** multi-line comment marks.
Each line of a comment block must start with the `#` character.

### Docstrings

The first statement of a function body can optionally be a [_docstring_][docstring], which concisely summarizes the function or object's purpose.
Docstrings are declared using triple double quotes (""") indented at the same level as the code block:

```python

# An example from PEP257 of a multi-line docstring
# reformatted to use Google style non-type hinted docstrings.
# Some additional details can be found in the Sphinx documentation:
# https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html#getting-started

def complex(real=0.0, imag=0.0):
    """Form a complex number.

    Keyword Arguments:
        real (float): The real part of the number (default 0.0)
        imag (float): The imaginary part of the number (default 0.0)

    """

    if imag == 0.0 and real == 0.0:
        return complex_zero

```

Docstrings are read by automated documentation tools such as [Sphinx][sphinx] and are returned by calling the special attribute `.__doc__` on the function, method, or class name.
General docstring conventions are laid out in [PEP257][pep257], but exact formats will vary by project and team.
Exercism concept exercises try to follow the Google style for un-type hinted code.

Docstrings can also function as [lightweight unit tests][doctests], which will be covered in a later exercise.

```python
# An example on a user-defined function using a Google style docstring.
>>> def raise_to_power(number, power):
    """Raise a number to an arbitrary power.

    Parameters:
        number (int): The base number.
        power (int): The power to raise the base number to.

    Returns:
        int: The number raised to the specified power.

    Takes a number and raises it to the specified power, returning the result.

    """

    return number ** power
...

# Calling the .__doc__ attribute of the function and printing the result.
>>> print(raise_to_power.__doc__)
Raise a number to an arbitrary power.

Parameters:
    number (int): The base number.
    power (int): The power to raise the base number to.

Returns:
    int: The number raised to the specified power.

Takes a number and raises it to the specified power, returning the result.
```

[calls]: https://devdocs.io/python~3.14/reference/expressions#calls
[comments]: https://realpython.com/python-comments-guide/#python-commenting-basics
[docstring]: https://devdocs.io/python~3.14/tutorial/controlflow#tut-docstrings
[doctests]: https://devdocs.io/python~3.14/library/doctest
[duck typing]: https://en.wikipedia.org/wiki/Duck_typing
[dynamic typing in python]: https://stackoverflow.com/questions/11328920/is-python-strongly-typed
[everythings an object]: https://devdocs.io/python~3.14/reference/datamodel
[facts-and-myths-about-python-names]: https://nedbatchelder.com/text/names.html
[function definition]: https://devdocs.io/python~3.14/tutorial/controlflow#defining-functions
[gradual typing]: https://en.wikipedia.org/wiki/Gradual_typing
[module]: https://devdocs.io/python~3.14/tutorial/modules
[none]: https://devdocs.io/python~3.14/library/constants
[parameters]: https://devdocs.io/python~3.14/glossary#term-parameter
[pep257]: https://www.python.org/dev/peps/pep-0257/
[return]: https://devdocs.io/python~3.14/reference/simple_stmts#return
[sphinx]: https://www.sphinx-doc.org/en/master/usage/index.html
[type hints]: https://devdocs.io/python~3.14/library/typing

## Instructions
You're going to write some code to help you cook a gorgeous lasagna from your favorite cookbook.

You have five tasks, all related to cooking your recipe.

> [!NOTE]
> We have started the first function definition for you in the stub file, but you will need to write the remaining function definitions yourself.
> You will also need to define any constants yourself.
> Read the #TODO comment lines in the stub file carefully.
> Once you are done with a task, remove the TODO comment.

### 1. Define expected bake time in minutes as a constant

Define the `EXPECTED_BAKE_TIME` [constant][constants] that represents how many minutes the lasagna should bake in the oven.
According to your cookbook, the Lasagna should be in the oven for 40 minutes:

```python
>>> print(EXPECTED_BAKE_TIME)
40
```

### 2. Calculate remaining bake time in minutes

Complete the `bake_time_remaining()` function that takes the actual minutes the lasagna has been in the oven as an argument and returns how many minutes the lasagna still needs to bake based on the `EXPECTED_BAKE_TIME` constant.

```python
>>> bake_time_remaining(30)
10
```

### 3. Calculate preparation time in minutes

Define the `preparation_time_in_minutes()` [function][functions] that takes the `number_of_layers` you want to add to the lasagna as an argument and returns how many minutes you would spend making them.
Assume each layer takes 2 minutes to prepare.

```python
>>> def preparation_time_in_minutes(number_of_layers):
        ...
        ...

>>> preparation_time_in_minutes(2)
4
```

### 4. Calculate total elapsed time (prepping + baking) in minutes

Define the `elapsed_time_in_minutes()` function that takes two parameters as arguments:

- `number_of_layers` (_the number of layers added to the lasagna_)
- `elapsed_bake_time` (_the number of minutes the lasagna has spent baking in the oven already_).

This function should return the total minutes you have been in the kitchen cooking — your preparation time layering +
the time the lasagna has spent baking in the oven.

```python
>>> def elapsed_time_in_minutes(number_of_layers, elapsed_bake_time):
        ...
        ...

>>> elapsed_time_in_minutes(3, 20)
26
```

### 5. Update the recipe with notes

Go back through the recipe, adding "notes" in the form of [function docstrings][function-docstrings].

```python
def elapsed_time_in_minutes(number_of_layers, elapsed_bake_time):
    """Calculate the elapsed cooking time.

    Parameters:
        number_of_layers (int): The number of layers in the lasagna.
        elapsed_bake_time (int): Time the lasagna has been baking in the oven.

    Returns:
        int: The total time elapsed (in minutes) preparing and baking.

    This function takes two integers representing the number of lasagna
    layers and the time already spent baking the lasagna. It calculates
    the total elapsed minutes spent cooking (preparing + baking).

    """
```

[constants]: https://stackoverflow.com/a/2682752
[functions]: https://devdocs.io/python~3.14/tutorial/controlflow#defining-functions
[function-docstrings]: https://devdocs.io/python~3.14/tutorial/controlflow#documentation-strings

## You get
Nothing. You define the numbers and the functions yourself.

> [!NOTE]
> Exercism hands you a `lasagna.py` stub and checks the module-level names directly. Here there is one entry point: `solve()` takes **no arguments** and returns a dict that hands those same four names to the grader. Define the constants and functions wherever you like — module level or inside `solve` — as long as the dict points at them.

## You return
A dict with these four entries, wired to your own code.

| key | what it holds |
| --- | --- |
| `"EXPECTED_BAKE_TIME"` | the plain number 40: how many minutes the cookbook says the lasagna spends in the oven, start to finish |
| `"bake_time_remaining"` | a function taking `elapsed_bake_time` (minutes already spent in the oven, e.g. 30) and returning how many minutes of baking are still to go |
| `"preparation_time_in_minutes"` | a function taking `number_of_layers` (e.g. 2) and returning the minutes of layering work, at 2 minutes a layer |
| `"elapsed_time_in_minutes"` | a function taking `number_of_layers` and `elapsed_bake_time` and returning the total minutes spent in the kitchen: the layering work plus the baking done so far |

```python
answers = solve()
answers["EXPECTED_BAKE_TIME"]                    # -> 40
answers["bake_time_remaining"](30)               # -> 10   (40 - 30)
answers["preparation_time_in_minutes"](2)        # -> 4    (2 layers x 2 minutes)
answers["elapsed_time_in_minutes"](3, 20)        # -> 26   (3 x 2 of prep, plus 20 baked)
```

## Rules
Every input is a whole number of minutes or layers; every function returns a number. The dict keys are exactly the four strings above.

- the three function values are the functions **themselves**, not the result of calling them — `{"bake_time_remaining": bake_time_remaining}`, no parentheses
- `"EXPECTED_BAKE_TIME"` is the number, not a function
- Exercism's task 5 (docstrings) is not graded here, so write them for yourself or skip them

Nobody bakes past the cookbook time, so `bake_time_remaining` never has to deal with a negative answer.

## Exercism hints

### General

- [The Python Tutorial][the python tutorial] can be a great introduction.
- [PEP 8][pep8] is the Python code style guide.
- [PEP 257][PEP257] details Python docstring conventions.
- [Numbers][numbers] in Python can be integers, floats, or complex.


### 1. Define expected bake time in minutes

- You need to [name][naming] a [constant][constants], and [assign][assignment] it an [integer][numbers] value.
  This constant should be the first thing after the docstring that is at the top of the file.
  Remember to remove the #TODO comment after defining the constant.

### 2. Calculate remaining bake time in minutes

- You need to define a [function][defining functions] with a single parameter representing the time elapsed so far.
- Use the [mathematical operator for subtraction][numbers] to subtract values.
- This function should [return a value][return].

### 3. Calculate preparation time in minutes

- You need to define a [function][defining functions] with a single parameter representing the number of layers.
- Use the [mathematical operator for multiplication][numbers] to multiply values.
- You can define a PREPARATION_TIME _constant_ for the time in minutes per layer rather than using a ["magic
  number"][magic-numbers] in your code.
- This function should [return a value][return].

### 4. Calculate total elapsed cooking time (prep + bake) in minutes

- You need to define a [function][defining functions] with two parameters.
- Remember: you can always _call_ a function you've defined previously.
- You can use the [mathematical operator for addition][python as a calculator] to sum values.
- This function should [return a value][return].

### 5. Update the recipe with notes

- Clearly [commenting][comments] and [documenting][docstrings] your code according to [PEP257][pep257] is always recommended.
- Some examples of Google-style docstrings can be found in the Sphinx documentation for the [napoleon module][napoleon].

[assignment]: https://devdocs.io/python~3.14/reference/simple_stmts#assignment-statements
[comments]: https://realpython.com/python-comments-guide/
[constants]: https://stackoverflow.com/a/2682752
[defining functions]: https://devdocs.io/python~3.14/tutorial/controlflow#defining-functions
[docstrings]: https://devdocs.io/python~3.14/tutorial/controlflow#tut-docstrings
[magic-numbers]: https://en.wikipedia.org/wiki/Magic_number_(programming)
[naming]: https://realpython.com/python-variables/
[napoleon]: https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html#module-sphinx.ext.napoleon
[numbers]: https://devdocs.io/python~3.14/tutorial/introduction#numbers
[pep8]: https://www.python.org/dev/peps/pep-0008/
[pep257]: https://www.python.org/dev/peps/pep-0257/
[python as a calculator]: https://devdocs.io/python~3.14/tutorial/introduction#using-python-as-a-calculator
[return]: https://devdocs.io/python~3.14/reference/simple_stmts#return
[the python tutorial]: https://devdocs.io/python~3.14/tutorial/introduction

## Hints
### Hint 1
Two numbers in this recipe never change: 40 and 2. [Name](https://realpython.com/python-variables/) each one and [assign](https://devdocs.io/python~3.14/reference/simple_stmts#assignment-statements) it an integer value once, above the functions, and let the functions read those names — that is how you avoid a ["magic number"](https://en.wikipedia.org/wiki/Magic_number_(programming)) sitting in the middle of your arithmetic. The third function does not need to redo the per-layer arithmetic: remember, you can always *call* a function you have defined previously.
### Hint 2
Shape of the work: define the two constants, then define the three functions, then build the dict that maps each key string to the matching function.

- `bake_time_remaining` — one parameter, the time elapsed so far; use the [mathematical operator for subtraction](https://devdocs.io/python~3.14/tutorial/introduction#numbers) and [return a value](https://devdocs.io/python~3.14/reference/simple_stmts#return).
- `preparation_time_in_minutes` — one parameter, the number of layers; use the operator for multiplication and return a value.
- `elapsed_time_in_minutes` — two parameters; [use the operator for addition](https://devdocs.io/python~3.14/tutorial/introduction#using-python-as-a-calculator) to sum the other two answers.

Put the function name in the dict WITHOUT parentheses — `{'bake_time_remaining': bake_time_remaining}` hands over the function itself so the caller can run it later; adding `()` would run it now, with no arguments, and store the result.
### Hint 3
Different data, same shape. A car wash charges a fixed 15-minute wash plus 3 minutes per extra service:

```python
WASH_TIME = 15
PER_EXTRA = 3
def extras_time(extras):
    return extras * PER_EXTRA
def total_time(extras):
    return WASH_TIME + extras_time(extras)
def handles():
    return {'WASH_TIME': WASH_TIME, 'total_time': total_time}
```

`handles()['total_time'](2)` is 21. Note `total_time` reusing `extras_time` instead of writing `extras * 3` a second time.
