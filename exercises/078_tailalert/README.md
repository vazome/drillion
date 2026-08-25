---
title: 'DRILL: tail a growing log, alert with context'
minutes: 25
prereqs: [21]
tags: [whole-task]
practices: [26, 29, 21]
---
# DRILL: tail a growing log, alert with context

*Whole-task drill: watch a log that never ends and alert with context.*

Combines topics 26 (line iteration), 29 (regex), 21 (deque).

## Why
A service writes a log file that grows all day and never stops. The on-call team wants to be paged every time an ERROR line shows up, and the page must include the few lines just before it so they can see what led up to the error. The log can be huge, so the tool must never try to hold all of it in memory.

## You get
`stream` — a source of log lines you can only read one at a time, first to last, like a file being read while it is still growing. Each line ends with a newline character. You cannot look ahead or ask how many lines there are. The test hands you a short fake one.

`pattern` — a search pattern as a string, like `"ERROR (?P<code>E[0-9]+)"`. It is a regular expression (a small language for matching text), and it always contains a named part called `"code"` that picks out the error code.

`window` — a whole number, like `2`: how many earlier lines to include with each alert.

## You return
a list of dictionaries, one per line that matched. Each has `"line_no"` (the line's position, counting from 1), `"code"` (the error code picked out of the line) and `"before"` (the last few lines seen before it, oldest first).

## Rules
Follow a log as it grows and raise an alert on every match.

`stream` is an ITERATOR of lines, the way `tail -f` hands them over: one line at a time, in order, each with its trailing newline. You cannot look ahead, you cannot count them first, and you must assume it never ends. `pattern` is a regex string with a named group `"code"`.

Return one dict per matching line:

```python
stream  = iter(["10:02 INFO ok\n", "10:03 WARN slow\n", "10:04 ERROR E503 upstream\n"])
pattern = r"ERROR (?P<code>E\d+)"
window  = 2

solve(stream, pattern, window)
# -> [{"line_no": 3,
#      "code": "E503",
#      "before": ["10:02 INFO ok", "10:03 WARN slow"]}]
```

Rules:

- `line_no` is 1-based and counts every line seen, not just matches.
- Strip the trailing newline off every line you store.
- `"before"` holds the last `window` lines seen before the match, oldest first. Near the start of the stream there are fewer, and that is fine. A matching line can itself show up in a later alert's `"before"`.

> [!TIP]
> Hold at most `window` lines in memory. Buffering the whole stream is the wrong answer even though the test would not catch it.

> [!TIP]
> "How would you alert on this log without reading 10 GB" is a real question. Say the memory argument out loud.

## Hints
### Hint 1
Two things happen per line and they are independent: you ask whether this line matches, and you keep a rolling memory of the few lines behind it. The memory is the interesting half — a plain list plus a slice grows forever, and the container you want throws the oldest item away by itself.
### Hint 2
collections.deque(maxlen=window) for the history. re.compile(pattern) once, above the loop, never inside it, then m = rx.search(line) and m.group('code') for the named group. enumerate(stream, start=1) gives you the line number. Order matters at the end of the loop body: snapshot with list(history) while you build the alert, and append the current line after that, so a line is never in its own context.
### Hint 3
Different data, same three moves:

```python
import re
from collections import deque
rx = re.compile(r'user=(?P<who>\w+)')
seen = deque(maxlen=2)
for i, line in enumerate(['boot', 'idle', 'login user=ana'], start=1):
    m = rx.search(line)
    if m:
        print(i, m.group('who'), list(seen))   # 3 ana ['boot', 'idle']
    seen.append(line)
```

Yours strips the newline first and collects dicts instead of printing.
