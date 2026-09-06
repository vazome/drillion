---
title: conditionals — are the brackets balanced and nested right?
difficulty: hard
tier: core
minutes: 15
prereqs: [18]
tags: [conditionals]
source: exercism/python practice/matching-brackets (MIT, adapted)
---
# conditionals — are the brackets balanced and nested right?

*matching-brackets — the stack, in its smallest useful form.*

## Read first
- [Using lists as stacks](https://devdocs.io/python~3.14/tutorial/datastructures#using-lists-as-stacks) — `append()` and `pop()` are push and pop; that is the entire data structure
- [list.pop()](https://devdocs.io/python~3.14/library/stdtypes#mutable-sequence-types) — with no argument it removes and returns the **last** item, which is exactly "most recently opened"
- [Mapping types: dict](https://devdocs.io/python~3.14/library/stdtypes#mapping-types-dict) — one small dict maps each closer to the opener it expects, so there is no three-branch `if`
- [Truth value testing](https://devdocs.io/python~3.14/library/stdtypes#truth-value-testing) — an empty list is falsey, which makes "is anything still open?" a one-liner

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
Your editor greys out a mismatched brace, your JSON parser says "unexpected end of input", your shell complains about an unterminated quote — all of them are running this check. It is also the smallest honest example of a stack: a problem where you must remember what you opened, in order, and match the most recent one first. Counting alone cannot do it, and finding out *why* counting fails is the point of the task.

## Introduction
You're given the opportunity to write software for the Bracketeer™, an ancient but powerful mainframe.
The software that runs on it is written in a proprietary language.
Much of its syntax is familiar, but you notice _lots_ of brackets, braces and parentheses.
Despite the Bracketeer™ being powerful, it lacks flexibility.
If the source code has any unbalanced brackets, braces or parentheses, the Bracketeer™ crashes and must be rebooted.
To avoid such a scenario, you start writing code that can verify that brackets, braces, and parentheses are balanced before attempting to run it on the Bracketeer™.

## Instructions
Given a string containing brackets `[]`, braces `{}`, parentheses `()`, or any combination thereof, verify that any and all pairs are matched and nested correctly.
Any other characters should be ignored.
For example, `"{what is (42)}?"` is balanced and `"[text}"` is not.

## You get
`text` — a string that may contain `()`, `[]`, `{}` and any other characters at all, e.g. `"(((185 + 223.85) * 15) - 543)/2"`. It may be empty.

> [!NOTE]
> Exercism's stub is `def is_paired(input_string)`. Here the function is `solve(text)`; nothing else about the task changes.

## You return
`True` if every bracket is matched and correctly nested, `False` otherwise. A real boolean.

## Rules
- three pairs count: `(` with `)`, `[` with `]`, `{` with `}`
- every other character is ignored completely — letters, digits, spaces, backslashes, everything
- a closing bracket must match the **most recently opened** bracket that is still open
- at the end nothing may still be open
- the empty string is balanced, and so is a string with no brackets in it

| text | result | why |
| --- | --- | --- |
| `{what is (42)}?` | `True` | nested correctly, the rest is ignored |
| `{}[]` | `True` | two pairs side by side |
| `[text}` | `False` | `}` does not close `[` |
| `[({]})` | `False` | correct counts, wrong nesting |
| `{}[` | `False` | something is still open at the end |
| `[]]` | `False` | a closing bracket with nothing open |

```python
solve("([{}({}[])])")  # -> True
solve("{[])")          # -> False
solve(")()")           # -> False   closes before anything opened
solve("")              # -> True
```

> [!WARNING]
> Counting openers and closers is not enough: `[({]})` has one of each and is still wrong, and `)(` has one of each and is wrong too. You need the *order*, which means remembering what you opened.

## Hints
### Hint 1
Work through `[({]})` by hand, character by character, saying out loud what you are still waiting to close. The moment you reach `]` you already know it is wrong — and what tells you is the thing you opened most recently, not the total count. So: what do you need to keep, and in what order?
### Hint 2
Keep a list of the openers you have seen and not yet closed. On an opening bracket, append it. On a closing bracket: if the list is empty, you have a closer with nothing open, so return `False` immediately; otherwise `pop()` the last opener and check it is the partner of this closer — if not, `False`. Ignore every other character. When the loop finishes, the answer is "the list is empty". A dict like `{')': '(', ']': '[', '}': '{'}` gives you both "is this a closer?" and "which opener does it want?" in one place.
### Hint 3
Different data, same stack — checking that the blocks in a config file close in the right order:

```python
lines = ['BEGIN db', 'BEGIN pool', 'END pool', 'END db']
open_blocks = []
for line in lines:
    keyword, name = line.split()
    if keyword == 'BEGIN':
        open_blocks.append(name)
    elif not open_blocks or open_blocks.pop() != name:
        print('mismatch at', line)
        break
open_blocks   # -> [] means every block was closed
```

Push what you open, pop and compare when you close, and check the pile is empty at the end. Once you recognise the shape you will see it in parsers, in undo buttons and in call stacks.
