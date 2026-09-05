---
title: argparse — declare a CLI, get validation free
difficulty: medium
tier: core
minutes: 15
prereqs: []
tags: [stdlib-ops]
---
# argparse — declare a CLI, get validation free

*Every internal tool grows a CLI; argparse is the one interviewers expect you to know.*

## Why
The team has an internal deploy tool people run from the terminal: `deployctl web -r 3 --env prod`. It must accept a service name, a replica count, an environment, a dry-run switch and some tags, and it must reject bad input (a typo in the environment, a replica count that is not a number) with a clear message and a non-zero exit. Writing those checks by hand is tedious and buggy; you declare what the arguments are and let the standard library enforce them.

## You get
nothing — you build the thing from scratch.

## You return
the parser object itself, not yet used on anything. The test feeds it its own argument lists and checks what it accepts and what it rejects.

## Rules
Build and return an `argparse.ArgumentParser` for a tool called `deployctl`. The command line looks like:

```bash
deployctl web -r 3 --env prod --dry-run --tag canary blue
```

> [!WARNING]
> Return the parser itself. Do not parse anything, do not read `sys.argv`, do not print. The test calls `parser.parse_args([...])` with its own lists.

Declare exactly these, with these dest names:

| Argument | Declaration |
| --- | --- |
| `service` | positional, required, a string |
| `--replicas` (also spelled `-r`) | `int`, default `1` |
| `--env` | `str`, default `"dev"`, only `"dev"` / `"stage"` / `"prod"` allowed |
| `--dry-run` | a flag: absent → `False`, present → `True` (dest is `dry_run`) |
| `--tag` | zero or more strings, default `[]` |

```python
parser = solve()
parser.parse_args(["web"])
# -> Namespace(service='web', replicas=1, env='dev', dry_run=False, tag=[])
```

Bad input must raise `SystemExit`: an unknown flag, a missing service, a `--replicas` that is not a number, an `--env` outside the three choices. You do not write any of those checks. You declare the type and the choices, and argparse does the rejecting, the exit code 2 and the `--help` text for you.

## Hints
### Hint 1
An argparse parser is a declaration, not code you step through. Each add_argument line states one argument's name, what it should be converted to, and what it defaults to. From those lines argparse builds the parsing, the error messages, the --help output and the exit code. A hand-rolled loop over sys.argv gets none of that and is the thing an interviewer is checking you have outgrown.
### Hint 2
Five add_argument calls on an ArgumentParser. A name without dashes is a positional. type=int converts and rejects. default= supplies the fallback. choices=[...] restricts the allowed values. action='store_true' makes a flag. nargs='*' collects zero or more values into a list. argparse converts a leading -- and inner dashes into the attribute name, so --dry-run lands on .dry_run.
### Hint 3
A different tool, same moves:

```python
import argparse
p = argparse.ArgumentParser(prog='backupctl')
p.add_argument('bucket')
p.add_argument('-n', '--keep', type=int, default=7)
p.add_argument('--mode', default='full', choices=['full', 'incr'])
p.add_argument('--verbose', action='store_true')
p.add_argument('--skip', nargs='*', default=[])
print(p.parse_args(['logs', '-n', '3', '--skip', 'tmp', 'cache']))
# Namespace(bucket='logs', keep=3, mode='full', verbose=False,
#           skip=['tmp', 'cache'])
```

Return the parser; let the caller do the parsing.
