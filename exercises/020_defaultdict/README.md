---
title: defaultdict(list) — group log lines by host
minutes: 10
prereqs: [18]
tags: [data-structures]
---
# defaultdict(list) — group log lines by host

*Grouping records by a key is the most-typed loop in ops scripting.*

## Why
A central log collector mixes messages from every host into one stream. An engineer investigating an incident asks "show me everything each host said, host by host, in order". You need to sort the lines into buckets by host name, keeping the message text but dropping the severity word. Grouping records by a key is the most-typed loop in ops scripting.

## You get
`lines` — a list of log lines like `"web-1 ERROR disk full"`: a host name, a level word, then the message (which may contain spaces). The test creates it and hands it to you; you never build it yourself.

## You return
a dict mapping each host to the list of its messages, in the order they appeared.

## Rules
Group log messages by host. Return `{host: [messages, in original order]}`.

Each line is `"host level message"`:

```python
solve(["web-1 ERROR disk full",
       "db-1 WARN slow query",
       "web-1 INFO restarted"])
# -> {"web-1": ["disk full", "restarted"], "db-1": ["slow query"]}
```

The message may contain spaces — keep it exactly as-is. Drop the level. A plain dict or a `defaultdict` both pass the test.

## Hints
### Hint 1
The pattern: for each record, work out its key, then append to that key's list. A plain dict raises `KeyError` the first time a key appears, so you'd be writing an if-check on every loop. There is a dict that skips that.
### Hint 2
`collections.defaultdict(list)` creates the empty list the first time you touch a missing key, so the loop body is a single append. To split each line into exactly three parts, give `split` a `maxsplit` so the message keeps its spaces.
### Hint 3
Different data, same shape:

```python
from collections import defaultdict
by_team = defaultdict(list)
for team, player in [('red', 'ann'), ('blue', 'bo'), ('red', 'cy')]:
    by_team[team].append(player)
print(dict(by_team))   # {'red': ['ann', 'cy'], 'blue': ['bo']}
```

The first touch of `by_team['red']` silently created the empty list.
