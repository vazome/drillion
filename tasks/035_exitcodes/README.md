---
title: exit codes — main(argv) returns an int
difficulty: medium
tier: core
minutes: 12
prereqs: [18]
tags: [stdlib-ops]
---
# exit codes — main(argv) returns an int

*A pipeline reads one thing from your script: the exit code.*

## Why
A CI pipeline runs your deploy script and then decides whether to carry on. It cannot read your printed messages; it reads exactly one number, the exit code. Zero means success, anything else means failure, and different numbers let the pipeline tell a usage mistake from a refused deploy. You write the decision part of the deploy command so it hands back the right number for each situation.

## You get
`argv` — a list of strings, the command-line arguments without the program name, like `["deploy", "web", "3"]`. The test creates it and hands it to you; you never build it yourself.

## You return
a whole number, 0, 1, 2 or 3, as described in the rules below. Do not exit the program and do not print.

## Rules
This is the body of a CLI's `main()`. `argv` is the argument list with the program name already stripped, e.g. `["deploy", "web", "3"]`.

> [!WARNING]
> Return an int. Do not call `sys.exit`, do not print.

Check in this order and return the first code that applies:

| Code | Meaning | When |
| --- | --- | --- |
| `2` | usage error | `argv` is not exactly 3 items, or `argv[0]` is not `"deploy"` or `"rollback"`, or `argv[2]` is not a non-negative whole number |
| `3` | unknown service | `argv[1]` is not in `KNOWN_SERVICES` |
| `1` | refused | the replica count is above `MAX_REPLICAS` |
| `0` | success | everything above passed |

```python
solve(["deploy", "web", "3"])    # -> 0
solve(["deploy", "web", "99"])   # -> 1
solve(["ship", "web", "3"])      # -> 2
solve(["deploy", "ftp", "3"])    # -> 3
```

The real program ends with one line:

```python
sys.exit(main(sys.argv[1:]))
```

Keep the decisions in a function that returns a code and let that single line do the exiting — then tests can call `main()` directly, which is exactly what is happening here.

Why this matters: a shell `&&` chain, a Makefile and every CI step read the exit code and nothing else. A script that prints ERROR and exits 0 gives you a green pipeline sitting on top of a broken deploy. 0 means success, anything else means failure, and distinct codes let the caller tell which failure it was without parsing your output.

## Hints
### Hint 1
A process hands its parent one small integer, and only zero means success. So the interesting design question is not how to print an error, it is which number each kind of failure gets. Bad usage, bad input and a refused operation are three different things to whoever is calling you. Also note what the spec asks for: a function that RETURNS the number, not one that exits — those are different jobs and only one of them is testable.
### Hint 2
A chain of guard clauses, each returning early, in the order the spec lists them. The numeric check is str.isdigit on argv[2] — it is False for '-1', '3.5' and '', which is what you want here. Unpack the three items only after you know there are three. int() the count for the last comparison.
### Hint 3
A different tool, same shape:

```python
import sys

def main(argv):
    if len(argv) != 1:
        return 2                    # usage
    if not argv[0].endswith('.conf'):
        return 3                    # wrong kind of input
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

# $ python check.py a.conf b.conf ; echo $?
# 2
```

One function returns codes, one line turns the code into an exit.
