---
title: classes — spawn a wave of aliens from a list of positions
minutes: 12
prereqs: [200, 203, 206, 212, 215, 221, 227, 233, 236, 245, 248]
tags: [exercism, classes, core]
source: exercism/python concept/ellens-alien-game (MIT, adapted)
---
# classes — spawn a wave of aliens from a list of positions

*Classes — turning rows of data into objects, one call per row.*

## Why
The level designer hands the game a list of starting positions — plain coordinate pairs out of a level file. The game needs live alien objects, one per pair, in the same order. This little function is the seam every program has between "data that came from outside" and "objects the rest of the code talks to": the loader that turns rows from a database into records, the parser that turns YAML into config objects. It is three lines, and the only two things that can go wrong are forgetting that the constructor wants two arguments while the data arrives as one tuple, and returning a generator when the caller asked for a list.

## Introduction

### Object Oriented Programming in Python

If you have been programming in a [functional][functional], [declarative][declarative], or [imperative][imperative] style, shifting focus to [object oriented programming][oop] (OOP) may feel a bit foreign.
An OOP approach asks the programmer to think about modeling a problem as one or more `objects` that interact with one another, keep state, and act upon data.
Objects can represent real world entities (_such as cars or cats_) - or more abstract concepts (_such as integers, vehicles, or mammals_).
Each object becomes a unique instance in computer memory and represents some part of the overall model.

### Classes

`Classes` are the definitions of new object types, and from which new `instances` of objects are created.
They often bundle data with code or functions that operate on that data.
In this sense, classes are _blueprints_ or sets of instructions from which many objects of a similar type can be built and used.
A complex program can have many classes, each building many different flavors of objects.
The process of building an object from a class is known as `instantiation` (_or creating an instance of the class_).

A class definition in Python is straightforward:

```python
class MyClass:
    # Class body goes here
```

#### Class Attributes

Class fields (_otherwise known as `properties`, `attributes`, `data members`, or `variables`_) can be added to the body of the class:

```python
class MyClass:
    number = 5
    string = "Hello!"
```

An instance (_object_) of `MyClass` can be created and bound to a name by [_calling_][calling] the class (_in the same way a function is called_):

```python
>>> new_object = MyClass()

# Class is instantiated and resulting object is bound to the "new_object" name.
# Note: the object address 'at 0x15adc55b0' will vary by computer.
>>> new_object
<__main__.MyClass at 0x15adc55b0>
```

`Class attributes` are shared across all objects (_or instances_) created from a class, and can be accessed via [`dot notation`][dot notation]  -  a `.` placed after the object name and before the attribute name:

```python
>>> new_object = MyClass()

# Accessing the class attribute "number" via dot-notation.
>>> new_object.number
5

# Accessing the class attribute "string" via dot-notation.
>>> new_object.string
'Hello!'

# Instantiating an additional object and binding it to the "second_new_object" name.
>>> second_new_object = MyClass()

>>> second_new_object
# Note: the object address "at 0x15ad99970" will vary by computer.
<__main__.MyClass at 0x15ad99970>

# Second_new_object shares the same class attributes as new_object.
>>> new_object.number == second_new_object.number
True
```

Class attributes are defined in the body of the class itself, before any other methods.
They are owned by the class - allowing them to be shared across instances of the class.
Because these attributes are shared, their value can be accessed and manipulated from the class _directly_.
Altering the value of class attributes alters the value _**for all objects instantiated from the class**_:

```python
>>> obj_one = MyClass()
>>> obj_two = MyClass()

# Accessing a class attribute from an object.
>>> obj_two.number
5

# Accessing the class attribute from the class itself.
>>> MyClass.number
5

# Modifying the value of the "number" class attribute.
>>> MyClass.number = 27

# Modifying the "number" class attribute changes the "number" attribute for all objects.
>>> obj_one.number
27

>>> obj_two.number
27
```

Having a bunch of objects with synchronized data at all times is not particularly useful.
Fortunately, objects created from a class can be customized with their own `instance attributes` (_or instance properties, variables, or fields_).
As their name suggests, instance attributes are unique to each object, and can be modified independently.

### Customizing Object Instantiation with `__init__()`

The special ["dunder method"][dunder] (_short for "double underscore method"_) `__init__()` is used to customize class instances, and can be used to initialize instance attributes or properties for objects.
For its role in initializing instance attributes, `__init__()` is also referred to as a `class constructor` or `initializer`.
`__init__()` takes one required parameter called `self`, which refers to the newly initialized or created object.
Data for instance attributes or properties can then be passed as arguments of `__init__()`, following the `self` parameter.

Below, `MyClass` now has instance attributes called `location_x` and `location_y`.
As you can see, the two attributes have been assigned to the first and second indexes of the `location` (_a tuple_) argument that has been passed to `__init__()`.
The `location_x` and `location_y` attributes for a class instance will now be initialized when you instantiate the class, and an object is created:

```python
class MyClass:
    # These are class attributes, variables, or fields.
    number = 5
    string = "Hello!"

    # This is the class "constructor", with a "location" parameter that is a tuple.
    def __init__(self, location):

        # This is an instance or object property, attribute, or variable.
        # Note that we are unpacking the tuple argument into two separate instance variables.
        self.location_x = location[0]
        self.location_y = location[1]

# Create a new object "new_object_one", with object property (1, 2).
>>> new_object_one = MyClass((1, 2))

# Create a second new object "new_object_two" with object property (-8, -9).
>>> new_object_two = MyClass((-8, -9))

# Note that new_object_one.location_x and new_object_two.location_x two different values.
>>> new_object_one.location_x
1

>>> new_object_two.location_x
-8
```

Note that you only need to pass one argument when initializing `MyClass` above -- Python takes care of passing `self` when the class is called.

### Methods

A `method` is a `function` that is bound to either the class itself (_known as a [class method][class method], which will be discussed in a later exercise_) or an _instance_ of the class (object).
Methods that operate on an object (instance) need to be defined with `self` as the first parameter.
You can then define the rest of the parameters as you would for a "normal" or non-bound function:

```python
class MyClass:
    number = 5
    string = "Hello!"

    # Class constructor.
    def __init__(self, location):
        # Instance properties
        self.location_x = location[0]
        self.location_y = location[1]

    # Instance method. Note "self" as first parameter.
    def change_location(self, amount):
        self.location_x += amount
        self.location_y += amount
        return self.location_x, self.location_y
```

Like attribute access, calling a method simply requires putting a `.` after the object name, and before the method name.
The called method does not need a copy of the object as a first parameter -- Python fills in `self` automatically:

```python
class MyClass:
    number = 5
    string = "Hello!"

    def __init__(self, location):
        self.location_x = location[0]
        self.location_y = location[1]

    def change_location(self, amount):
        self.location_x += amount
        self.location_y += amount
        return self.location_x, self.location_y

# Make a new test_object with location (3,7)
>>> test_object = MyClass((3,7))
>>> (test_object.location_x, test_object.location_y)
(3,7)

# Call change_location to increase location_x and location_y by 7.
>>> test_object.change_location(7)
(10, 14)
```

Class attributes can be accessed from within instance methods in the same way that they are accessed outside of the class:

```python
class MyClass:
    number = 5
    string = "Hello!"

    def __init__(self, location):
        self.location_x = location[0]
        self.location_y = location[1]

    # Alter instance variable location_x and location_y
    def change_location(self, amount):
        self.location_x += amount
        self.location_y += amount
        return self.location_x, self.location_y

    # Alter class variable number for all instances from within an instance.
    def increment_number(self):
        # Increment the 'number' class variable by 1.
        MyClass.number += 1

>>> test_object_one = MyClass((0,0))
>>> test_object_one.number
5

>>> test_object_two = MyClass((13, -3))
>>> test_object_two.increment_number()
>>> test_object_one.number
6
```

### Placeholding or Stubbing Implementation with Pass

In previous concept exercises and practice exercise stubs, you will have seen the `pass` keyword used within the body of  functions in place of actual code.
The `pass` keyword is a syntactically valid placeholder - it prevents Python from throwing a syntax error for an empty function or class definition.
Essentially, it is a way to say to the Python interpreter, 'Don't worry! I _will_ put code here eventually, I just haven't done it yet.'

```python
class MyClass:
    number = 5
    string = "Hello!"

    def __init__(self, location):
        self.location_x = location[0]
        self.location_y = location[1]

    # Alter instance variable location_x and location_y
    def change_location(self, amount):
        self.location_x += amount
        self.location_y += amount
        return  self.location_x, self.location_y

    # Alter class variable number for all instances
    def increment_number(self):
        # Increment the 'number' class variable by 1.
        MyClass.number += 1

    # This will compile and run without error, but has no current functionality.
    def pending_functionality(self):
       # Stubbing or placholding the body of this method.
       pass
```

[calling]: https://www.pythonmorsels.com/topics/calling-a-function
[class method]: https://stackoverflow.com/questions/17134653/difference-between-class-and-instance-methods
[dunder]: https://mathspp.com/blog/pydonts/dunder-methods
[imperative]: https://en.wikipedia.org/wiki/Imperative_programming
[declarative]: https://en.wikipedia.org/wiki/Declarative_programming
[oop]: https://www.digitalocean.com/community/tutorials/how-to-construct-classes-and-define-objects-in-python-3
[functional]: https://en.wikipedia.org/wiki/Functional_programming
[dot notation]: https://stackoverflow.com/questions/45179186/understanding-the-dot-notation-in-python

## Instructions

Ellen is making a game where the player has to fight aliens.
She has just learned about Object Oriented Programming (OOP) and is eager to take advantage of what using `classes` could offer her program.

To Ellen's delight, you have offered to help and she has given you the task of programming the aliens that the player has to fight.

### 1. Create the Alien Class

Define the Alien class with a constructor that accepts two parameters `<x_coordinate>` and `<y_coordinate>`, putting them into `x_coordinate` and `y_coordinate` instance variables.
Every alien will also start off with a health level of 3, so the `health` variable should be initialized as well.

```python
>>> alien = Alien(2, 0)
>>> alien.x_coordinate
2
>>> alien.y_coordinate
0
>>> alien.health
3
```

Now, each alien should be able to internally track its own position and health.

### 2. The `hit` Method

Ellen would like the Alien `class` to have a `hit` method that decrements the health of an alien object by 1 when called.
This way, she can simply call `<alien>.hit()` instead of having to manually change an alien's health.
It is up to you if `hit()` takes healths points _to_ or _below_ zero.

```python
>>> alien = Alien(0, 0)

# Initialized health value.
>>> alien.health
3

# Decrements health by 1 point.
>>> alien.hit()
>>> alien.health
2
```

### 3. The `is_alive` Method

You realize that if the health keeps decreasing, at some point it will probably hit 0 (_or even less!_).
It would be a good idea to add an `is_alive` method that Ellen can quickly call to check if the alien is... well... alive. 😉
`<alien>.is_alive()` should return a boolean.

```python
>>> alien.health
1
>>> alien.is_alive()
True
>>> alien.hit()
>>> alien.health
0
>>> alien.is_alive()
False
```

### 4. The `teleport` Method

In Ellen's game, the aliens have the ability to teleport!
You will need to write a `teleport` method that takes new `x_coordinate` and `y_coordinate` values, and changes the alien's coordinates accordingly.

```python
>>> alien.teleport(5, -4)
>>> alien.x_coordinate
5
>>> alien.y_coordinate
-4
```

### 5. The `collision_detection` Method

Obviously, if the aliens can be hit by something, then they need to be able to detect when such a collision has occurred.
However, collision detection algorithms can be tricky, and you do not yet know how to implement one.
Ellen has said that she will do it later, but she would still like the `collision_detection` method to appear in the class as a reminder to build out the functionality.
It will need to take a variable of some kind (probably another object), but that's really all you know.
You will need to make sure that putting the method definition into the class doesn't cause any errors when called:

```python
>>> alien.collision_detection(other_object)
>>>
```

### 6. Alien Counter

Ellen has come back with a new request for you.
She wants to keep track of how many aliens have been created over the game's lifetime.
She says that it's got something to do with the scoring system.

For example:

```python
>>> alien_one = Alien(5, 1)
>>> alien_one.total_aliens_created
1
>>> alien_two = Alien(3, 0)
>>> alien_two.total_aliens_created
2
>>> alien_one.total_aliens_created
2
# Accessing the variable from the class directly
>>> Alien.total_aliens_created
2
```

### 7. Creating a List of Aliens

Ellen loves what you've done so far, but she has one more favor to ask.
She would like a standalone (_outside the `Alien()` class_) function that creates a `list` of `Alien()` objects, given a list of positions (as `tuples`).

For example:

```python
>>> alien_start_positions = [(4, 7), (-1, 0)]
>>> aliens = new_aliens_collection(alien_start_positions)
...
>>> for alien in aliens:
...     print(alien.x_coordinate, alien.y_coordinate)
(4, 7)
(-1, 0)
```

## You get
The finished `Alien` class is already in the file above `solve`, marked `# given — do not edit`. It is exactly what task `248_ellens_alien_game` asks you to write: `Alien(x_coordinate, y_coordinate)`, a `health` that starts at 3, and a class-level `total_aliens_created` that counts up on every construction.

`positions` — a list of `(x, y)` tuples, in the order the aliens should appear:

```python
[(4, 7), (-1, 0), (3, 3)]
```

The list may be empty. Coordinates may be negative, and the same position may appear twice.

> [!NOTE]
> Exercism calls this function `new_aliens_collection(positions)` and asks for it alongside the class in one `classes.py`. Here **this task covers task 7 only** — the class itself is task `248_ellens_alien_game` — and the entry point is `solve(positions)`.

## You return
A `list` of `Alien` objects, one per position, in the same order as `positions`.

```python
aliens = solve([(4, 7), (-1, 0)])

len(aliens)                                       # -> 2
aliens[0].x_coordinate, aliens[0].y_coordinate    # -> (4, 7)
aliens[1].x_coordinate, aliens[1].y_coordinate    # -> (-1, 0)
aliens[0].health                                  # -> 3
solve([])                                         # -> []
```

## Rules
- one `Alien` per tuple, in order — the alien at index 0 must be built from `positions[0]`
- each alien is a **new** object: two positions that happen to be equal still give two separate aliens
- the return value is a `list`, so a generator expression or a `map(...)` object has to be wrapped in `list()`

> [!WARNING]
> A tuple is a *single* value, and the constructor takes *two* arguments — `Alien(position)` raises `TypeError: __init__() missing 1 required positional argument`. Unpack the pair before you pass it on.

## Exercism hints

### 1. Create the Alien Class

- Remember that `object methods` are always passed `self` as the first parameter.
- Remember the double underscores on _both_ sides of `__init__()`.
- Instance variables are unique to the `class` instance (_object_) that possesses them.
- Class variables are the same across all instances of a `class`.

### 2. The `hit` Method

- Remember that `object methods` are always passed `self` as the first parameter.
- You can choose to allow the Alien's health to fall below zero, or require that it does not.

### 3. The `is_alive` Method

- Remember that `object methods` are always passed `self` as the first parameter.
- 0 may not be the only 'dead' condition, depending on how `hit()` is implemented.

### 4. The `teleport` Method

- Remember that `object methods` are always passed `self` as the first parameter.
- Instance attributes can be updated from a method by using `self.<attribute> = <new attribute value>`.

### 5. The `collision_detection` Method

- Remember that `object methods` are always passed `self` as the first parameter.
- This method seems like an excellent place to use some kind of placeholder…

### 6. Alien Counter

- Class attributes are the same across all instances of a `class`.
- Ideally, this counter would increment whenever someone _made an new Alien_.
- Class attributes can be changed from an instance method by using the _class name_:  `Alien.<class attribute name>`.
- `__init__()` is considered an instance method since it _initializes a new object_.

### 7. Object Creation

- A `tuple` would be a _single_ parameter.
- The Alien constructor takes _2 parameters_.
- Unpacking what is _inside_ the tuple would yield two parameters.
- The standalone function is outside of the `class`.

## Read first
- [Classes (the Python tutorial)](https://docs.python.org/3/tutorial/classes.html) — the constructor call `Alien(2, -1)` is just the class name used like a function
- [Tuple unpacking](https://docs.python.org/3/tutorial/datastructures.html#tuples-and-sequences) — `x, y = position` splits a pair into two names in one line
- [Unpacking argument lists](https://docs.python.org/3/tutorial/controlflow.html#unpacking-argument-lists) — `Alien(*position)` spreads a tuple across the parameters, the shortest form of the same idea
- [List comprehensions](https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions) — one expression per input item, and the result really is a `list`
- [Python Morsels: Classes](https://www.pythonmorsels.com/topics/classes/) — a refresher on what an instance is

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Hints
### Hint 1
One alien per position, in order, collected into a list — that is a `for` loop appending to a list, or the one-line form of the same thing. The only wrinkle: each item of `positions` is a tuple holding two numbers, but the constructor wants those two numbers as two separate arguments.
### Hint 2
Each item in `positions` is a **single** tuple, but `Alien` takes **two** parameters. So the only real question is how to get two arguments out of one tuple. Three routes work: index into it twice, unpack it into two names first, or let Python spread it for you at the call site — there is a prefix operator that does exactly that spreading, and it is the one most Python programmers reach for here.

Collect the results as you go. If you use the one-liner form, keep the square brackets: round brackets would build a generator, and the grader wants a `list`.
### Hint 3
Different data, same move. Rows out of a CSV becoming objects the rest of the program can use:

```python
class Host:
    def __init__(self, name, region):
        self.name = name
        self.region = region

rows = [("web-1", "eu-west-1"), ("db-1", "us-east-1")]
hosts = [Host(*row) for row in rows]

hosts[0].name, hosts[0].region     # -> ('web-1', 'eu-west-1')
len(hosts)                         # -> 2
```

`Host(*row)` is the whole trick: `row` is one tuple going in, two arguments coming out.
