---
title: class-inheritance — a fixed-size queue that reuses its own slots
difficulty: hard
tier: core
minutes: 20
prereqs: [35]
tags: [class-inheritance, function-arguments, user-defined-errors]
source: exercism/python practice/circular-buffer (MIT, adapted)
---
# class-inheritance — a fixed-size queue that reuses its own slots

*circular-buffer — the storage never grows, so the interesting code is what happens at the two edges.*

## Read first
- [User-defined exceptions](https://devdocs.io/python~3.14/tutorial/errors#user-defined-exceptions) — why an exception class is usually nothing but a name and a base class
- [Raising exceptions](https://devdocs.io/python~3.14/tutorial/errors#raising-exceptions) — `raise Something("message")`, and where that message ends up
- [`BufferError`](https://devdocs.io/python~3.14/library/exceptions#BufferError) — the built-in base class both given exceptions inherit from
- [`%` on integers](https://devdocs.io/python~3.14/reference/expressions#binary-arithmetic-operations) — `(index + 1) % capacity` is how a position walks off the end and reappears at the start
- [`collections.deque`](https://devdocs.io/python~3.14/library/collections#collections.deque) — a ready-made double-ended queue, and `maxlen` if you would rather not do the index arithmetic yourself

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
A log shipper reads lines faster than the network can send them, so it parks them in a buffer. That buffer cannot be allowed to grow — an agent that swallows memory whenever the network hiccups takes the host down with it, which is worse than losing log lines. So you fix the size up front, reuse the slots as they free up, and then make a decision the caller can actually act on when you hit an edge: refuse the write and say so, or drop the oldest line to make room. Audio buffers, serial ports, ring buffers in a kernel, bounded queues in a worker pool — all the same object. The part people get wrong is never the arithmetic; it is telling "full" apart from "empty" and reporting each one clearly enough that the caller knows which one happened.

## You get
Nothing to start — you return a **class**. The grader builds it as `CircularBuffer(capacity)`, e.g. `CircularBuffer(3)`. `capacity` is an `int` of `1` or more and never changes afterwards. The values written in are single-character strings, e.g. `"7"`.

The two exception classes are **already written for you** at the top of `task.py`, marked `# given — do not edit`:

```python
class BufferFullException(BufferError): ...
class BufferEmptyException(BufferError): ...
```

Use them by name — the grader imports nothing, it uses the very same two classes from this file. Defining your own copies inside `solve()` would create different classes that only look the same, and the grader would not recognise them.

> [!NOTE]
> Exercism's stub is a `class CircularBuffer` in `circular_buffer.py`, and there you write the two exception classes yourself. Here the entry point is `solve()`, which takes **no arguments** and returns the buffer class itself — not an instance — and the two exception classes are given so that both you and the grader mean the same ones.

## You return
The class. The grader uses it like this:

```python
CircularBuffer = solve()
buffer = CircularBuffer(2)
buffer.write("1")
buffer.write("2")
buffer.read()            # -> "1"
buffer.overwrite("3")    # room again, so this behaves exactly like write
buffer.read()            # -> "2"
buffer.read()            # -> "3"
```

| member | is | behaviour |
| --- | --- | --- |
| `CircularBuffer(capacity)` | constructor | a new, empty buffer holding at most `capacity` unread items |
| `read()` | method | remove and return the oldest unread item; raises when there is none |
| `write(data)` | method | store one item; raises when there is no free slot; returns nothing |
| `overwrite(data)` | method | store one item, discarding the oldest unread item if that is the only way; never raises; returns nothing |
| `clear()` | method | forget everything unread, leaving a buffer as empty as a new one; returns nothing |

## Rules
- items come back out oldest-first — a queue, not a stack
- `read()` on an empty buffer raises `BufferEmptyException("Circular buffer is empty")`
- `write(data)` on a full buffer raises `BufferFullException("Circular buffer is full")` and stores nothing
- both messages are compared exactly, capital `C` included, and each is passed as the single argument to the exception, so that `err.args[0]` is the message
- `overwrite(data)` on a buffer that still has room does exactly what `write` does; on a full buffer it discards the oldest unread item and stores the new one, which makes the second-oldest item the new oldest
- `clear()` works on an empty buffer too, and never raises
- a read frees a slot, so `write` works again afterwards; so does `clear()`
- capacity is fixed at construction — the buffer never grows, no matter how many items pass through it

```python
CircularBuffer = solve()
buffer = CircularBuffer(3)
for item in "123":
    buffer.write(item)
buffer.read()            # -> "1"
buffer.write("4")        # the slot "1" left behind is free again
buffer.overwrite("5")    # full, so the oldest unread item ("2") is dropped
buffer.read()            # -> "3"
buffer.read()            # -> "4"
buffer.read()            # -> "5"
```

> [!WARNING]
> "Where do I read next" and "where do I write next" are the same position both when the buffer is empty and when it is full. If those two positions are the only state you keep, the two edges are indistinguishable and one of the two exceptions will fire at the wrong moment. Keep something that tells them apart.

> [!WARNING]
> `overwrite` on a full buffer does not just replace the value in a slot — it also means the item that was dropped is gone from the reading order. After it, the next `read()` must return the item that was *second* oldest, not the one you just wrote.

## Hints
### Hint 1
Start from the two edges rather than from the storage. Write down, in words, the exact condition under which `read` must refuse and the exact condition under which `write` must refuse. Whatever answers both of those questions is the state your class has to keep — and once you have it, `overwrite` turns out to be "if the write condition would refuse, make room first, then write".

### Hint 2
A fixed-size list of slots plus two facts — where the oldest unread item sits, and how many unread items there are — answers everything, and `read`/`write` both end with the same one-line move: step a position forward and wrap it round with a remainder, so it never runs off the end of the list. Note that you do **not** need a separate "where do I write" position; it is the oldest position plus the count, wrapped the same way. Two things to be deliberate about: `clear` has to reset the count as well as the slots, or an emptied buffer will still refuse to be written to; and dropping the oldest item during `overwrite` means moving the oldest position forward, not just replacing a value.

### Hint 3
Different data, same shape — handing work to three lanes in turn:

```python
LANES = ["north", "east", "south"]
lane = 0
for job in range(7):
    print(job, LANES[lane])
    lane = (lane + 1) % len(LANES)

# 0 north / 1 east / 2 south / 3 north / 4 east / 5 south / 6 north
```

That single `% len(...)` is the whole "circular" part; there is no other trick to it. And here is why counting matters, on the same three lanes: if all you record is "the next lane to hand work to" and "the next lane to collect from", then *no jobs outstanding* and *all three lanes busy* both look like `next_hand == next_collect`, and you cannot tell whether the next thing to do is hand out work or refuse. One extra number — how many are outstanding — separates them, and it is the same number that tells your buffer whether to raise `BufferEmptyException` or `BufferFullException`.
