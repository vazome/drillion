---
title: 'DRILL: mini-grep with argparse flags'
minutes: 25
prereqs: [29]
tags: [whole-task]
practices: [29, 37, 28]
---
# DRILL: mini-grep with argparse flags

*Whole-task drill: rebuild grep, flags and all.*

Combines topics 29 (regex), 37 (argparse), 28 (str methods).

## Why
grep is the command-line tool every engineer uses to pull matching lines out of a log. Interviewers ask you to rebuild a small version of it because it combines two everyday skills: reading command-line options the standard way, and searching lines for a pattern. The ignore-case, invert and line-number options are the ones people reach for most on a real shell.

## You get
`lines` — a list of strings, one per log line, with no newline characters, like `["INFO ok", "ERROR boom"]`.

`argv` — the command-line arguments as a list of strings, exactly what a user typed after the program name, like `["-n", "-i", "error"]`. The test builds both and hands them to you.

## You return
a list of the lines that were kept, as strings, in their original order. When the line-number option is on, each kept line is prefixed with its number and a colon, like `"2:ERROR boom"`.

## Rules
Write the guts of grep.

`lines` is a list of strings with no trailing newlines. `argv` is the command line as a list, exactly what `sys.argv[1:]` would hand you.

| argument | what it does |
| --- | --- |
| `pattern` | positional, a regex |
| `-i`, `--ignore-case` | match without regard to case |
| `-v`, `--invert-match` | keep the lines that do NOT match |
| `-n`, `--line-number` | prefix each kept line with `"<number>:"`, 1-based |

Return the kept lines as a list of strings.

```python
solve(["INFO ok", "ERROR boom", "warn slow"], ["-n", "-i", "error"])
# -> ["2:ERROR boom"]
```

Flags arrive in any order, long or short form, and the pattern may come before or after them. A hit anywhere in the line counts, the pattern does not have to match the whole line.

> [!TIP]
> Parse `argv` with argparse — do not pick the flags apart by hand.

> [!TIP]
> Interviewers like this one because the invert flag catches people. Say out loud what `-v` does to the decision before you code it.

## Hints
### Hint 1
Two halves. First turn argv into settings — that is argparse's whole job, and hand-rolling `if '-i' in argv` is the answer that loses points. Then one pass over the lines. Invert is the flag that trips people: it does not change the pattern or the search, it flips the keep-or-drop decision at the end.
### Hint 2
add_argument('pattern') for the positional, then each flag with action='store_true' — argparse turns --ignore-case into args.ignore_case for you. parse_args(argv), not parse_args(). Compile once with re.compile(pattern, re.IGNORECASE) when the flag is set and no flags otherwise. Then per line: matched = rx.search(line) is not None, and keep it when matched != args.invert_match. enumerate(lines, start=1) and an f-string give you the numbered form.
### Hint 3
Different data, both halves:

```python
import argparse
p = argparse.ArgumentParser()
p.add_argument('word')
p.add_argument('-c', '--count', action='store_true')
args = p.parse_args(['--count', 'pod'])
print(args.word, args.count)       # pod True

for matched, invert in [(True, False), (True, True), (False, True)]:
    print(matched != invert)        # True, False, True
```

That second loop is the whole invert rule: not-equal is exclusive or, and it reads better than four branches.
