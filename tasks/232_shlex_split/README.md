---
title: shlex — split a command line the way the shell would, quotes and all
difficulty: medium
tier: core
minutes: 12
prereqs: [179]
tags: [strings, stdlib-ops]
---
# shlex — split a command line the way the shell would, quotes and all

*`str.split()` breaks on every space. `shlex.split()` breaks the way a POSIX shell does: quoted runs stay whole, backslashes escape, and `#` starts a comment.*

## Read first
- [`shlex`](https://devdocs.io/python~3.14/library/shlex) — the module and its parsing rules
- [`shlex.split`](https://devdocs.io/python~3.14/library/shlex#shlex.split) — the `comments` and `posix` keywords
- [`subprocess`](https://devdocs.io/python~3.14/library/subprocess#security-considerations) — why a list of arguments is the safe way to run something

## Why
The runbook file lists the commands to execute, one per line, written by people who write shell for a living: paths with spaces are quoted, and half the lines carry a trailing `#` note explaining why. Feeding those lines to `subprocess.run` as one string means asking a shell to re-parse them, which is exactly how a path someone controls turns into a command someone controls. Feeding them as a list is safe — but building that list with `line.split()` chops `"/var/log/last run"` into two arguments and the command fails on a file that does not exist. The parser that already knows these rules is one import away, and it is the same one the shell's own lexer is modelled on.

## You get
`lines`, a list of command lines as strings, straight out of the runbook.

## You return
a list with one entry per input line, in order:

- the line's arguments as a list of strings, or
- `None` if the line cannot be parsed.

## Rules
- Quoted runs — single or double — are one argument, and the quotes themselves are not part of it.
- Everything from an unquoted `#` to the end of the line is a comment and is dropped. A `#` inside quotes is an ordinary character.
- A line that is blank, or is nothing but a comment, gives the empty list. That is a parse, not a failure.
- A line with a quote that never closes cannot be parsed. That line's entry is `None`, and the lines after it are parsed as normal.

```python
solve([
    'cp -r "/var/log/last run" /backup  # nightly',
    '   # just a note',
    'echo "unterminated',
])
# -> [['cp', '-r', '/var/log/last run', '/backup'], [], None]
```

> [!NOTE]
> Comment handling is off by default — `shlex.split` leaves `#` as an ordinary character unless you ask for it. The runbook expects shell behaviour, so ask.

## Hints
### Hint 1
`shlex.split(line)` already handles the quoting. The one thing it does not do without being told is treat `#` as a comment.
### Hint 2
The unclosed quote is signalled the normal Python way, as a raised exception — `ValueError`, with a message about no closing quotation. Catch it per line so one bad line does not lose the rest.
### Hint 3
The three behaviours side by side:

```python
import shlex

'a "b c" # note'.split()                        # -> ['a', '"b', 'c"', '#', 'note']
shlex.split('a "b c" # note')                    # -> ['a', 'b c', '#', 'note']
shlex.split('a "b c" # note', comments=True)     # -> ['a', 'b c']
shlex.split('a "b c')                            # -> ValueError: No closing quotation
```
