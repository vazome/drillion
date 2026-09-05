---
title: logging — levels, a formatter, a custom handler
difficulty: hard
tier: core
minutes: 18
prereqs: [21]
tags: [stdlib-ops]
---
# logging — levels, a formatter, a custom handler

*print in a daemon has no level, no timestamp and nowhere to go but stdout.*

## Read first
- [Logging HOWTO](https://devdocs.io/python~3.14/howto/logging) — levels, and why `print` is not logging
- [logging](https://devdocs.io/python~3.14/library/logging) — the reference

## Why
A background service writes hundreds of messages a minute. In production the operators want only warnings and errors; while debugging they want everything — and they want to switch between the two with one setting, not a code change. The messages must also go somewhere you control (a file, a log system, or here a plain list the test can inspect) in one consistent format. You wire up one such logger.

## You get
`name` — a string naming the logger, like `"drill38.0.solve"`. The test creates it and hands it to you; you never build it yourself.

`level` — a whole number meaning "keep messages at this severity or higher", like `logging.WARNING`.

`messages` — a list of (severity name, text) pairs, like `[("INFO", "starting"), ("ERROR", "disk full")]`.

## You return
a list of strings — the formatted messages that got past the level filter, in order, like `["ERROR:disk full"]`.

## Rules
Set up one logger and capture what it emits, printing nothing.

| Argument | What it is |
| --- | --- |
| `name` | a unique logger name, e.g. `"drill38.0.solve"` |
| `level` | a level as an int, e.g. `logging.WARNING` |
| `messages` | list of `(levelname, text)` pairs, e.g. `[("INFO", "starting"), ("ERROR", "disk full")]` |

Build it in this order:

1. A handler class of your own: subclass `logging.Handler`, and in its `emit(self, record)` append `self.format(record)` to a list.
2. Give the handler `logging.Formatter("%(levelname)s:%(message)s")`.
3. Get the logger by name, set its level, attach the handler, and set `.propagate = False` so records stop here instead of climbing to the root logger and being printed twice by whatever else is running.
4. Log every message at its own level, in order.
5. Return the list of formatted strings.

```python
solve("drill38.0.solve", logging.WARNING, [("INFO", "hi"), ("ERROR", "boom")])
# -> ["ERROR:boom"]
```

Only records at or above the logger's level survive; the rest never reach the handler. That is the point of levels — the same daemon runs quiet in production and chatty at DEBUG without touching a line of code.

## Hints
### Hint 1
Three separate objects, and mixing them up is the usual beginner failure. The logger is a named thing you fetch, and it decides which records pass its level. The handler decides where a surviving record goes — a file, syslog, or in this case a list. The formatter decides what it looks like as text. Loggers are also a tree: by default a record travels up to the root and gets emitted again there, which is why one flag exists to stop it.
### Hint 2
Subclass logging.Handler and override emit(self, record); inside, self.format(record) gives you the formatted string. Then: logging.getLogger(name), .setLevel(level), handler.setFormatter(...), .addHandler(handler), .propagate = False. To log at a level you only know as a string, getattr(logging, 'INFO') gives you the int and logger.log(int, text) takes it.
### Hint 3
Different data, same wiring:

```python
import logging
seen = []

class ListHandler(logging.Handler):
    def emit(self, record):
        seen.append(self.format(record))

h = ListHandler()
h.setFormatter(logging.Formatter('%(levelname)s|%(message)s'))
log = logging.getLogger('demo.backup')
log.setLevel(logging.INFO)
log.propagate = False
log.addHandler(h)
log.debug('opening socket')
log.log(getattr(logging, 'WARNING'), 'slow disk')
print(seen)          # ['WARNING|slow disk']
```

The debug line was dropped by the logger's level, not by the handler.
