---
title: defensive parsing — skip the junk, count it
minutes: 15
prereqs: [43]
tags: [errors]
---
# defensive parsing — skip the junk, count it

*Interviewers feed you a log with junk in it on purpose; one bad line must not kill the run.*

## Why
A log export from a customer has junk mixed in: blank lines,
lines cut short, a field that should be a number but says "N/A". Someone
in support wants the good records loaded so they can look at response
times. A script that crashes on the first bad line is useless; a script
that quietly throws lines away is worse, because nobody learns that 40%
of the data went missing. So: keep what you can, and count what you
dropped.

## You get
`lines` — a list of strings, one per log line, like
["2026-08-12T10:12:44Z INFO checkout 137", "", "2026-08-12T10:12:46Z
WARN cart"]. The test builds it, junk included, and hands it to you.

## You return
a pair (records, skipped). records is a list of
dictionaries, one per good line, with "ts", "level", "service" and "ms"
(a number). skipped is how many lines you threw away.

## Rules
Parse the good lines out of a dirty log. Report how many you dropped.

A good line is exactly four whitespace-separated fields:

```
2026-08-12T10:12:44Z INFO checkout 137
<timestamp>          <level> <service> <latency in ms>
```

Return the tuple (records, skipped):

  - records: a list, in input order, of
    {"ts": <str>, "level": <str>, "service": <str>, "ms": <int>}
    Note ms is an int, not the string you split out.
  - skipped: how many lines you did not turn into a record.

Skip a line, without raising, when any of these is true:
  - it is empty or only whitespace
  - it does not split into exactly 4 fields (too few or too many)
  - the level is not one of DEBUG, INFO, WARN, ERROR (case matters)
  - the last field is not a whole number

```
["2026-08-12T10:12:44Z INFO checkout 137",
 "2026-08-12T10:12:45Z info checkout 12",     # lowercase level
 "2026-08-12T10:12:46Z WARN cart",            # only 3 fields
 "2026-08-12T10:12:47Z ERROR cart N/A"]       # ms is not a number
->  ([{"ts": "2026-08-12T10:12:44Z", "level": "INFO",
       "service": "checkout", "ms": 137}], 3)
```

The count matters as much as the parsing. A parser that silently
drops 40% of your log is worse than one that crashes, because
nobody finds out.

## Hints
### Hint 1
The instinct is one try/except wrapped around the whole loop. That stops at the first bad line and throws away everything after it. The unit of failure here is a single line, so the handling belongs inside the loop. Second thing to notice: only one of the four failure modes actually raises — a wrong level is just a value you have to check for yourself.
### Hint 2
Per line: strip it, skip if falsy, parts = line.split(), skip if len(parts) != 4, skip if parts[1] not in the allowed set, then wrap int(parts[3]) in try/except ValueError. Use `continue` on every skip path so the append at the bottom only runs for lines that survived all four checks. Keep one counter alongside the results list.
### Hint 3
Different data — reading key=value tokens where some are malformed:

```python
good, bad = {}, 0
for token in ['cpu=2', 'mem', 'disk=x', '  ']:
    token = token.strip()
    key, sep, raw = token.partition('=')
    if not sep:
        bad += 1
        continue
    try:
        good[key] = int(raw)
    except ValueError:
        bad += 1
        continue
print(good, bad)     # {'cpu': 2} 3
```

Same shape: check what you can check with `in` and len, and catch only the conversion that genuinely raises.
