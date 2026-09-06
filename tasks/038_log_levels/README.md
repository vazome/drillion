---
title: enums — name the six log levels once
difficulty: hard
tier: core
minutes: 15
prereqs: [11, 35]
tags: [enums]
source: exercism/python concept/log-levels (MIT, adapted)
---
# enums — name the six log levels once

*Enums — members, values, aliases, and iterating the set of names.*

## Read first
- [enum — support for enumerations](https://devdocs.io/python~3.14/library/enum) — declaring members, `EnumClass(value)` lookup by value, `EnumClass[name]` lookup by name
- [Aliases in an Enum](https://devdocs.io/python~3.14/howto/enum#duplicating-enum-members-and-values) — two names, one value, and why iteration shows only the first
- [The `is` operator](https://www.w3schools.com/python/ref_keyword_is.asp) — enum members are singletons, so identity is the right comparison
- [enum.auto()](https://devdocs.io/python~3.14/howto/enum#using-auto) — for when you do not care what the values are (not this task: here the values are the wire format)
- [The functional API](https://devdocs.io/python~3.14/howto/enum#functional-api) — `Enum("LogLevel", ...)` builds the same class without a `class` block
- [str.split()](https://devdocs.io/python~3.14/library/stdtypes#str.split) — one way to get `INF` out of `"[INF]: File deleted"`

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
Every log pipeline has the same handful of severities, and every log pipeline that spells them as bare strings eventually ships `"WARN"` in one service and `"WRN"` in another, and a dashboard that quietly counts neither. An enum makes the set of allowed values a real thing in the code: there are exactly seven, they are compared by identity so a typo is an error instead of a silent mismatch, and the two spellings you inherited from the old system can be declared as an alias of the same member instead of a second truth. This task builds that enum and the four functions around it — parse an incoming line, shorten it for storage, expose the legacy alias, and list what exists.

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
