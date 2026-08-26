---
title: enums — name the six log levels once
minutes: 15
prereqs: [209, 218, 227, 233, 248]
tags: [exercism, enums, data-structures]
source: exercism/python concept/log-levels (MIT, adapted)
---
# enums — name the six log levels once

*Enums — members, values, aliases, and iterating the set of names.*

## Why
Every log pipeline has the same handful of severities, and every log pipeline that spells them as bare strings eventually ships `"WARN"` in one service and `"WRN"` in another, and a dashboard that quietly counts neither. An enum makes the set of allowed values a real thing in the code: there are exactly seven, they are compared by identity so a typo is an error instead of a silent mismatch, and the two spellings you inherited from the old system can be declared as an alias of the same member instead of a second truth. This drill builds that enum and the four functions around it — parse an incoming line, shorten it for storage, expose the legacy alias, and list what exists.

## Introduction

In Python, [an enum](https://docs.python.org/3/library/enum.html) is a set of names that are bound to unique `literal`, or `constant` values. Enums are defined by inheriting an `Enum` class. Built-in enum types are available in the module `enum` and the class `Enum` can be imported using `from enum import Enum`.

```python
class Color(Enum):
    RED = 1
    GREEN = 2
```

Note that the values of the enum members can be any data types such as str, tuple, float, etc.

```python
class Color(Enum):
    RED = 'red'
    GREEN = 'green'
```

When assigning the same value to two members in an enum, the latter assigned member will be an alias to the formed one. It is not allowed to use the same name for two members of an enum.

```python
class Color(Enum):
    RED = 1
    GREEN = 2
    ALIAS_OF_RED = 1

Color.ALIAS_OF_RED
#=> <Color.RED: 1>

Color.ALIAS_OF_RED.value
#=> 1
```

Iterating through the members of the enum can be done with the standard `for member in` syntax:

```python
for member in Color:
    print((member.name, member.value))
#=> (RED, 1)
#=> (GREEN, 2)
```

Enum members can be compared using [`is` (_identity operator_)](https://www.w3schools.com/python/ref_keyword_is.asp) or `is not`. The `==` or `!=` (_equality_operators_) work likewise.

```python
a = Color.RED

a is Color.RED
#=> True

a == Color.RED
#=> True
```

To access an enum member for a given value, `EnumName(value)` can be used:

```python
g = Color(2)

g is Color.GREEN
#=> True

g
#=> <Color.GREEN: 2>
```

## Instructions

In this exercise, you'll be processing log messages with six severity levels.

Each log line is a string formatted as follows: `"[<LVL>]: <MESSAGE>"`.

These are the different log levels:

| LEVEL     | LVL   |
| --------- | ----- |
| `Trace`   | `TRC` |
| `Debug`   | `DBG` |
| `Info`    | `INF` |
| `Warning` | `WRN` |
| `Error`   | `ERR` |
| `Fatal`   | `FTL` |

### 1. Parse log level

Define a `LogLevel` enum that has six elements corresponding to the log levels defined above.
Next, define the `parse_log_level` function which takes the log message as parameter and returns the enum member of its level.

```python
parse_log_level("[INF]: File deleted")
#=> LogLevel.Info
```

### 2. Support unknown log level

Unfortunately, some log messages occasionally appear with an _unknown_ severity. To gracefully handle these 'mysterious' log messages in the function `parse_log_level`, add an `Unknown` member to the `LogLevel` enum which is returned when parsing an unknown log level:

```python
parse_log_level("[XYZ]: Overly specific, out of context message")
#=> LogLevel.Unknown
```

### 3. Convert a log message to the short format

The log level of a log line is quite verbose. To reduce the disk space needed to store the log messages, a short format is defined: `"[<CODE_LEVEL>]:<MESSAGE>"`.

The log level codes follow a straightforward mapping:

| LEVEL     | CODE |
| --------- | ---- |
| `Trace`   | `0`  |
| `Debug`   | `1`  |
| `Info`    | `4`  |
| `Warning` | `5`  |
| `Error`   | `6`  |
| `Fatal`   | `7`  |
| `Unknown` | `42` |

Define the `convert_to_short_log()` function, which takes two parameters:

1. Log level - The Log level of the log sent. ex: `LogLevel.Error`.
2. Log Message - The message of type `str`.

```python
convert_to_short_log(LogLevel.Error, "Stack overflow")
# => "6:Stack overflow"
```

### 4. Create an Alias

It looks like the user has created logs for `LogLevel.Warn` instead of `LogLevel.Warning`. Create an `alias` for `LogLevel.Warning` and return the new alias member in the function `get_warn_alias`.

This can be done on the same enum class `LogLevel` already defined at the top of the file. Both the LogLevels should point to same value: `"WRN"`.

```python
get_warn_alias()
#=> LogLevel.Warn

get_warn_alias() == LogLevel.Warning
#=> True
```

### 5. All Member Names and Values

Define the function `get_members()`.

This function should return a list of tuples `(name, value)` containing all the members of the enum `LogLevel`.

```python
get_members()
#=> [('Trace', 'TRC'), ('Debug', 'DBG'), ('Info', 'INF'), ('Warning', 'WRN'),
# ('Error', 'ERR'), ('Fatal', 'FTL'), ('Unknown', 'UKN')]
```

## You get
Nothing. `solve()` takes **no arguments**; the log lines arrive as arguments to the functions you hand back.

> [!NOTE]
> Exercism asks for the enum and the four functions in one `enums.py`. Here there is one entry point: `solve()` returns a dict holding your `LogLevel` class **and** the four functions, keyed by name.
>
> Two things Exercism's prose leaves loose and its tests pin down: the member **names are upper case** (`LogLevel.INFO`, not `LogLevel.Info`), and the `Unknown` member's value is the string `"UKN"`.

## You return
A dict with these five entries.

| key | what it is |
| --- | --- |
| `"LogLevel"` | the enum **class** itself — the class object, not a member and not an instance |
| `"parse_log_level"` | a function taking one log line, e.g. `"[INF]: File deleted"`, returning the matching `LogLevel` member, or `LogLevel.UNKNOWN` when the code is not one you know |
| `"convert_to_short_log"` | a function taking a `LogLevel` member and a message string, returning the short form: the level's numeric code, a colon, then the message |
| `"get_warn_alias"` | a function taking nothing, returning `LogLevel.WARN` — the alias of `LogLevel.WARNING` |
| `"get_members"` | a function taking nothing, returning a list of `(name, value)` tuples, one per member, in the order they are declared |

```python
logs = solve()
LogLevel = logs["LogLevel"]

logs["parse_log_level"]("[INF]: File deleted")           # -> LogLevel.INFO
logs["parse_log_level"]("[XYZ]: out of context")         # -> LogLevel.UNKNOWN
logs["convert_to_short_log"](LogLevel.ERROR, "Stack overflow")  # -> "6:Stack overflow"
logs["get_warn_alias"]() is LogLevel.WARNING             # -> True
logs["get_members"]()
# -> [("TRACE", "TRC"), ("DEBUG", "DBG"), ("INFO", "INF"), ("WARNING", "WRN"),
#     ("ERROR", "ERR"), ("FATAL", "FTL"), ("UNKNOWN", "UKN")]
```

## Rules
- the dict keys are exactly the five strings above; the four function values are the functions **themselves**, no parentheses, and `"LogLevel"` is the class, not `LogLevel()`
- `LogLevel` subclasses `enum.Enum`; its members are named and valued exactly like this, in this order:

| member | value | short code |
| --- | --- | --- |
| `TRACE` | `"TRC"` | 0 |
| `DEBUG` | `"DBG"` | 1 |
| `INFO` | `"INF"` | 4 |
| `WARNING` | `"WRN"` | 5 |
| `ERROR` | `"ERR"` | 6 |
| `FATAL` | `"FTL"` | 7 |
| `UNKNOWN` | `"UKN"` | 42 |

- `WARN` is an **alias**: another name declared with the value `"WRN"`, so `LogLevel.WARN is LogLevel.WARNING` is `True`
- declare `WARNING` **first** and `WARN` second — whichever name comes first is the real member and the other becomes the alias, and `get_members()` is checked for `("WARNING", "WRN")`
- `parse_log_level` gets the whole line, `"[<LVL>]: <MESSAGE>"`, and has to pull the three letters out of the brackets itself
- `convert_to_short_log` returns a string — the code, then `":"`, then the message with no space added: `"6:Stack overflow"`
- how you map a member to its numeric code is up to you: a second enum, a dict, or a chain of `if`s all pass

> [!WARNING]
> `get_members()` returns **seven** tuples, not eight. An alias is not a separate member: iterating an `Enum` skips it, which is exactly the behaviour being tested. Values are compared with `==`, and members with `is`, so the strings have to be spelled exactly as in the table.

## Exercism hints

### General

- [Python Docs: Enum](https://docs.python.org/3/library/enum.html)

### 1. Parse log level

- Use [`str.split`](https://www.w3schools.com/python/ref_string_split.asp) to extract the log level from the message.
- With the extracted part of the string, access and return the enum member using `LogLevel(string)`.

### 2. Support unknown log level

- Create a new Unknown log level member in the existing enum.
- Check if the extracted part of the string is a value of the enum `LogLevel`.
- If the value does not match any of the enum member values, then return the Unknown member of `LogLevel`.

### 3. Convert log line to short format

- Find the code (an integer) of the log level based on the log level, multiple solutions are possible: if statements, another enum or any other solution.
- Use string formatting to return a properly formatted code level and message.

### 4. Create an Alias

- Create the new alias member named Warn in the existing enum.
- Return the newly created member.

### 5. All Member Names and Values

- Iterate on all the members of the enum and return a list of tuple.
- The tuple can be constructed with `(item1, item2)`.
- The name and value of the enum can be accessed with `member.name` and `member.value`.
- Return the list containing all the tuples.

## Read first
- [enum — support for enumerations](https://docs.python.org/3/library/enum.html) — declaring members, `EnumClass(value)` lookup by value, `EnumClass[name]` lookup by name
- [Aliases in an Enum](https://docs.python.org/3/howto/enum.html#duplicating-enum-members-and-values) — two names, one value, and why iteration shows only the first
- [The `is` operator](https://www.w3schools.com/python/ref_keyword_is.asp) — enum members are singletons, so identity is the right comparison
- [enum.auto()](https://docs.python.org/3/howto/enum.html#using-auto) — for when you do not care what the values are (not this drill: here the values are the wire format)
- [The functional API](https://docs.python.org/3/howto/enum.html#functional-api) — `Enum("LogLevel", ...)` builds the same class without a `class` block
- [str.split()](https://docs.python.org/3/library/stdtypes.html#str.split) — one way to get `INF` out of `"[INF]: File deleted"`

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Hints
### Hint 1
Declare the class first — `class LogLevel(Enum):` with one `NAME = "VALUE"` line per severity — and everything else becomes short. Two lookups do most of the work and it is worth knowing which is which: `LogLevel("INF")` finds a member **by value**, and `LogLevel["INFO"]` finds it **by name**. `parse_log_level` wants the first one, because what it has extracted from the line is a value.
### Hint 2
Shape of the work.

- `parse_log_level(message)` — carve `INF` out of `"[INF]: File deleted"`: split on `":"` and take the first piece, then drop the first and last characters (`[1:-1]`). Before you call `LogLevel(code)`, check that the code is one of the values you declared — looking up a value that does not exist raises `ValueError` rather than returning something. Iterating the enum gives you its members, and each member carries its `.value`, so you can gather the declared codes and fall back to the unknown member when the code is not among them.
- `convert_to_short_log(log_level, message)` — you need the number that goes with the member. A second enum sharing the same member names lets you look the number up by `.name`; a plain dict keyed by the member works just as well. Then f-string the number, a colon and the message together.
- `get_warn_alias()` — one line: return the alias member.
- `get_members()` — `for member in LogLevel` walks the members in declaration order, skipping the alias for free. Append `(member.name, member.value)` for each one.
### Hint 3
Different data, same shape. Deployment states, with a legacy spelling kept as an alias:

```python
from enum import Enum

class State(Enum):
    PENDING = "pend"
    RUNNING = "run"
    IN_PROGRESS = "run"      # alias: the old name for RUNNING
    DONE = "done"

State("run")                  # -> <State.RUNNING: 'run'>   lookup by value
State["DONE"]                 # -> <State.DONE: 'done'>     lookup by name
State.IN_PROGRESS is State.RUNNING            # -> True
[(m.name, m.value) for m in State]
# -> [('PENDING', 'pend'), ('RUNNING', 'run'), ('DONE', 'done')]
```

Three tuples out of four declared names — the alias is the same object as `RUNNING`, so iteration only yields it once, under its first name.
