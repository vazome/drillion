---
title: list-methods — turn a five-bit code into a list of actions
difficulty: medium
tier: core
minutes: 10
prereqs: [3, 11, 18]
tags: [list-methods]
source: exercism/python practice/secret-handshake (MIT, adapted)
---
# list-methods — turn a five-bit code into a list of actions

*secret-handshake — each bit switches one action on, and the top bit reverses the lot.*

## Read first
- [Data structure: lists](https://devdocs.io/python~3.14/tutorial/datastructures#more-on-lists) — `append`, `reverse`, and the difference between reversing in place and returning a reversed copy
- [Common sequence operations](https://devdocs.io/python~3.14/library/stdtypes#common-sequence-operations) — `[::-1]`, which reads a sequence backwards without touching it
- [zip()](https://devdocs.io/python~3.14/library/functions#zip) — walking two sequences side by side, here bits and the actions they stand for
- [String indexing and slicing](https://devdocs.io/python~3.14/library/stdtypes#text-sequence-type-str) — `binary_str[-1]` is the rightmost character; negative indices count from the end

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
A bitmask is how a system packs a set of yes/no options into one small value: Linux file permissions, feature flags in a config integer, the status word a device driver hands back, the `flags` column somebody added to a table instead of six booleans. Decoding one is always the same job — walk the bits from the least significant end, and for each bit that is set, add the thing it stands for. The twist here is a bit that does not name an action but changes how the others are assembled, which is exactly how a real protocol grows a "reverse order" or "negate" flag. Once you have done this by hand, `chmod 0755` stops being a magic number.

## You get
`binary_str` — a string of exactly five characters, each `"0"` or `"1"`, most significant bit first:

```python
"10011"
```

You never have to convert a number to binary yourself; the grader has already done it, always padded to five characters.

> [!NOTE]
> Exercism's stub is `def commands(binary_str)`. Here the function is `solve(binary_str)`; nothing else about the task changes.

## You return
A `list` of action strings, in the order they should be performed. When no action bit is set, that list is empty.

## Rules
The four action bits are read from the **right-hand end** of the string:

| position from the right | character in `"10011"` | action |
| --- | --- | --- |
| 1st | `1` | `"wink"` |
| 2nd | `1` | `"double blink"` |
| 3rd | `0` | `"close your eyes"` |
| 4th | `0` | `"jump"` |
| 5th (leftmost) | `1` | reverse the whole list |

- the action strings are exactly `"wink"`, `"double blink"`, `"close your eyes"`, `"jump"` — lower case, spaces as written
- an action whose bit is `0` does not appear at all
- the leftmost bit adds no action; when it is `1` the finished list is reversed
- reversing a list of one action, or of none, changes nothing

```python
solve("00001")  # -> ["wink"]
solve("00011")  # -> ["wink", "double blink"]
solve("10011")  # -> ["double blink", "wink"]
solve("01111")  # -> ["wink", "double blink", "close your eyes", "jump"]
solve("11111")  # -> ["jump", "close your eyes", "double blink", "wink"]
solve("10000")  # -> []
```

> [!WARNING]
> The order is a list order, not a set: `["wink", "double blink"]` and `["double blink", "wink"]` are different answers and only one is right for a given code.

## Hints
### Hint 1
The string reads left to right and the actions read right to left, so one of the two has to be turned around before they can be lined up. Decide which and write it down; doing it in your head is how you end up with `jump` and `wink` swapped. Then treat the leftmost character separately — it is not an action at all, it is an instruction about the list you are building.

### Hint 2
Keep the four action names in a list, in the order the bits assign them, and pair each name with its bit. Once both sequences run the same way, `zip` walks them together and you collect the names whose bit is `"1"`. The fifth character never joins that pairing: pull it off first, and use it at the very end to decide whether to hand back the list as built or the same list reversed. `[::-1]` gives you the reversed copy without mutating anything, which keeps the two branches symmetrical.

### Hint 3
Different data, same bits-to-names decoding — reading a Unix permission triad out of a three-bit string:

```python
NAMES = ['read', 'write', 'execute']

def permissions(bits):
    return [name for name, bit in zip(NAMES, bits) if bit == '1']

permissions('101')   # -> ['read', 'execute']
```

One list of names, one string of bits, zipped so position lines them up, and a filter that keeps only the set ones. This task adds two wrinkles: the bits arrive in the opposite order to the names, and one of them is a modifier rather than a name.
