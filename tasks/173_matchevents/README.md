---
title: match — route an event by its shape
difficulty: medium
tier: core
minutes: 15
prereqs: [92, 106]
tags: [match, dicts]
---
# match — route an event by its shape

*`match` reads a dict's shape and pulls the values out in one line, where `if`/`elif` needs three.*

## Read first
- [match statements](https://devdocs.io/python~3.14/tutorial/controlflow#match-statements) — start here: the tutorial builds up from literals to mapping patterns
- [The match statement](https://devdocs.io/python~3.14/reference/compound_stmts#the-match-statement) — the reference, including guards (`case ... if ...`) and the wildcard `_`
- [Mapping patterns](https://devdocs.io/python~3.14/reference/compound_stmts#mapping-patterns) — the rule that decides this task: a mapping pattern matches when the named keys are present, and ignores any extras

## Why
Your automation bus carries events from several systems, and each one is a dict whose keys depend on what happened. A deploy carries a version, a scale carries a replica count, an alert carries a level. Turning those into one human-readable line per event with `if event.get("type") == ...` means a chain of lookups that repeats the key names, checks each optional field by hand, and gets longer every time a new event type appears. `match` tests the shape and binds the values in the same line, and unknown shapes fall to one wildcard instead of a forgotten `else`.

## You get
`events` — a list of dicts, in the order they arrived, e.g.

```python
[{"type": "deploy", "service": "api", "version": "1.4.2"},
 {"type": "alert", "level": "critical", "text": "disk full"}]
```

The test creates them and hands them to you; you never build them yourself.

## You return
a list of strings, one per event, in the same order.

## Rules
Turn each event into exactly one line:

| the event | the line |
| --- | --- |
| `{"type": "deploy", "service": s, "version": v}` | `f"deploy {s} to {v}"` |
| `{"type": "deploy", "service": s}` with no version | `f"deploy {s} to latest"` |
| `{"type": "scale", "service": s, "replicas": 0}` | `f"stop {s}"` |
| `{"type": "scale", "service": s, "replicas": n}` | `f"scale {s} to {n} replicas"` |
| `{"type": "alert", "level": "critical", "text": t}` | `f"PAGE: {t}"` |
| `{"type": "alert", "text": t}` at any other level | `f"log: {t}"` |
| anything else | `"ignored"` |

```python
solve([{"type": "scale", "service": "api", "replicas": 0},
       {"type": "note", "text": "hi"}])
# -> ["stop api", "ignored"]
```

> [!WARNING]
> The rows are in priority order, and a mapping pattern ignores keys you did not name. `{"type": "deploy", "service": s}` also matches an event that HAS a version, so the specific row has to come first. Every event carries a `"ts"` key none of the rows mention, and that must not stop anything from matching.

## Hints
### Hint 1
One `match event:` per event, with a `case` per row of the table, in the table's order, and `case _:` at the end for `"ignored"`. A name inside a pattern is not a comparison, it is a capture: `"service": s` means "there is a `service` key, call its value `s`".
### Hint 2
Two rows need care. `"replicas": 0` is a literal pattern and matches only zero, so it goes above the row that captures `n`. And a quoted string in the value position is a literal too: `{"type": "alert", "level": "critical", "text": t}` matches only critical alerts, so the general alert row goes underneath it.
### Hint 3
Different data, same shape:

```python
def describe(msg):
    match msg:
        case {"kind": "ping", "id": i}:
            return f"ping {i}"
        case {"kind": "ping"}:
            return "ping, no id"
        case _:
            return "unknown"

print(describe({"kind": "ping", "id": 7, "extra": True}))   # ping 7
```

The `extra` key is ignored, which is what lets your `"ts"` key ride along on every event.
