---
title: testing — what to actually test in an ops script
difficulty: easy
tier: core
track: rsample
minutes: 8
prereqs: []
tags: [testing]
---
# testing — what to actually test in an ops script

*Coverage percentage is easy to game; knowing which lines deserve a test is the real skill.*

## Read first
- [TestPyramid](https://martinfowler.com/bliki/TestPyramid.html) — many small unit tests, few big end-to-end ones
- [Effective Python testing with pytest](https://realpython.com/pytest-python-testing/) — the pytest tutorial; 'Fixtures' and 'Marks' sections

## Why
Your team has a big ops script and a rule that "everything must have tests". Writing a test for every single function wastes days and produces brittle tests that break on every rename. The tech lead wants a consistent triage: functions that make decisions get tests; thin wrappers around a library call, plain config constants, and straight-line glue code are skipped, unless the glue starts branching, which makes it decision-making again. You encode that rule so the team can apply it to a list of functions.

## You get
`units` — a list of dicts, one per function in the script, like `{"name": "parse_uptime", "kind": "logic", "branches": 3}`, where kind is `"logic"`, `"wrapper"`, `"config"` or `"glue"` and branches is how many if/else paths it has. Names are unique. The test creates it and hands it to you.

## You return
a dict mapping each name to the string `"test"` or `"skip"`.

## Rules
Decide which pieces of a script are worth writing a test for.

Each unit describes one function in the script:

```python
{"name": "parse_uptime", "kind": "logic", "branches": 3}
```

kind is one of `"logic"`, `"wrapper"`, `"config"` or `"glue"`, and branches is how many if/else paths it contains. Return a dict mapping each name to `"test"` or `"skip"`. Names are unique.

The rule:

| kind | Verdict |
| --- | --- |
| `"logic"` | `"test"`, always |
| `"wrapper"` | `"skip"` |
| `"config"` | `"skip"` |
| `"glue"` | `"test"` if `branches >= 2`, else `"skip"` |

```python
solve([{"name": "parse_uptime", "kind": "logic", "branches": 3},
       {"name": "get_bucket", "kind": "wrapper", "branches": 0},
       {"name": "route_alert", "kind": "glue", "branches": 2},
       {"name": "run_all", "kind": "glue", "branches": 0}])
# -> {"parse_uptime": "test", "get_bucket": "skip",
#     "route_alert": "test", "run_all": "skip"}
```

Why the rule looks like that:

**logic** is code that decides something you wrote the rules for — parsing a line, comparing against a threshold, choosing whether to retry. It has edge cases, and edge cases are what tests are for.

**wrapper** is a function whose body is one library call plus a return. A test there asserts that boto3 still works, which is not your problem, and it breaks every time you touch the signature. It also needs a mock to run at all, so the test is mostly mock setup.

**config** is constants and defaults. The test would restate the value, so it passes right up until someone changes both together.

**glue** wires calls into an order. With no branches there is nothing to get wrong that an end-to-end run would not catch louder. Once it is picking between paths, that choice is your logic again, and it is worth pinning down.

## Hints
### Hint 1
The question sitting behind the rule: if this broke, would a test have caught it, and would that test break for any other reason. A function that only forwards to a library fails on both counts — it breaks when you rename an argument, not when the behaviour is wrong. Code that decides something passes on both.
### Hint 2
One dict, built in a loop over units. Two of the four kinds are always skip and one is always test, so only glue needs to look at branches. Order the if/elif so the glue case comes last and the rest fall through to a single skip. Key the dict by unit['name'].
### Hint 3
Different data — same shape of decision, routing health checks:

```python
checks = [{'n': 'disk', 'sev': 'page'},
          {'n': 'cache_hit', 'sev': 'info'}]
action = {}
for c in checks:
    if c['sev'] == 'page':
        action[c['n']] = 'wake someone'
    else:
        action[c['n']] = 'dashboard'
print(action)    # {'disk': 'wake someone', 'cache_hit': 'dashboard'}
```

Yours has four kinds feeding two labels, and one of them needs a second look at a number before it picks.
