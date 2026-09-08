---
title: walrus — decode a stream whose numbers end when a bit says so
difficulty: medium
tier: core
minutes: 14
prereqs: [163, 180]
tags: [walrus, bitwise]
source: exercism/python practice/variable-length-quantity (MIT, adapted)
---
# walrus — decode a stream whose numbers end when a bit says so

*The loop needs the byte to decide whether to keep going, so the test is where the byte is read.*

## Read first
- [Assignment expressions](https://devdocs.io/python~3.14/reference/expressions#assignment-expressions) — `:=`, and why it needs parentheses nearly everywhere
- [Bitwise operations](https://devdocs.io/python~3.14/library/stdtypes#bitwise-operations-on-integer-types) — `&`, `|` and `<<`, which are the whole decoder

## Why
MIDI files, protocol buffers and Git packfiles all store numbers the same way: seven bits of value per byte, and the top bit means "another byte follows". A small number costs one byte, a large one costs as many as it needs. Decoding it is the loop that `while` was not designed for, because you cannot test the byte until you have read it, and you need it afterwards. Written without an assignment expression it becomes read-once-before-the-loop and read-again-at-the-bottom, with the same line in two places and a bug waiting for whichever one you forget to change.

## You get
`stream` — a list of whole numbers from 0 to 255, the encoded bytes, back to back with no separator. The test creates it and hands it to you; you never build it yourself.

## You return
a list of the decoded numbers, in order.

## Rules
Decode the stream into the numbers it holds.

Each number is one or more bytes:

- the low seven bits of each byte are part of the value, most significant group first
- the top bit (`0x80`) is set on every byte **except the last one of that number**

So `0x81 0x00` is two bytes: `0x81` has the top bit set, so more follows; the value so far is `1`, shifted up seven and joined with `0x00`, giving `128`.

```python
solve([0x00])                    # -> [0]
solve([0x7F])                    # -> [127]
solve([0x81, 0x00])              # -> [128]
solve([0xC0, 0x00])              # -> [8192]
solve([0x40, 0x81, 0x00])        # -> [64, 128]
```

If the stream ends while a number is still expecting another byte, raise `ValueError`.

> [!WARNING]
> The bytes of one number arrive most significant group first, so each new byte shifts what you already have **up** by seven and adds itself. Building it the other way round gives the right answer for one-byte numbers and the wrong one for every other, which is the half of the test that a quick check misses.

## Hints
### Hint 1
Two loops, or one loop and a counter. Walk the stream once; keep a running value for the number being built; when a byte arrives with the top bit clear, that number is finished, so append it and reset the running value to zero. The `ValueError` is simply "the stream ran out while the running value was still being built".
### Hint 2
`byte & 0x80` is truthy exactly when more follows, and `byte & 0x7F` is the seven bits of value. Building up is `value = (value << 7) | (byte & 0x7F)`. The walrus earns its place in the inner loop over an iterator: `while (byte := next(it, None)) is not None and byte & 0x80:` reads the byte, keeps it, and decides in the same line.
### Hint 3
Different data — reading length-prefixed records from a byte iterator, the same shape:

```python
data = iter([0x81, 0x2C, 0x03])

value = 0
while (byte := next(data, None)) is not None:
    value = (value << 7) | (byte & 0x7F)
    if not byte & 0x80:          # top bit clear: this number is done
        print(value)             # 172, then 3
        value = 0

print(0x81 & 0x80, 0x81 & 0x7F)  # 128 1   <- more follows, and the value is 1
print((1 << 7) | 0x2C)           # 172
```

`next(it, None)` is the version that returns a default instead of raising, which is what makes the `is not None` test possible.
