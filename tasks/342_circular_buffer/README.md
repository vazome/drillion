---
title: circular-buffer — a fixed-size queue that reuses its own slots
minutes: 20
prereqs: [200, 203, 206, 209, 215, 221, 224, 227, 236, 248]
tags: [exercism, class-inheritance, function-arguments, user-defined-errors, errors]
source: exercism/python practice/circular-buffer (MIT, adapted)
---
# circular-buffer — a fixed-size queue that reuses its own slots

*circular-buffer — the storage never grows, so the interesting code is what happens at the two edges.*

## Why
A log shipper reads lines faster than the network can send them, so it parks them in a buffer. That buffer cannot be allowed to grow — an agent that swallows memory whenever the network hiccups takes the host down with it, which is worse than losing log lines. So you fix the size up front, reuse the slots as they free up, and then make a decision the caller can actually act on when you hit an edge: refuse the write and say so, or drop the oldest line to make room. Audio buffers, serial ports, ring buffers in a kernel, bounded queues in a worker pool — all the same object. The part people get wrong is never the arithmetic; it is telling "full" apart from "empty" and reporting each one clearly enough that the caller knows which one happened.

## Instructions
A circular buffer, cyclic buffer or ring buffer is a data structure that uses a single, fixed-size buffer as if it were connected end-to-end.

A circular buffer first starts empty and of some predefined length.
For example, this is a 7-element buffer:

```text
[ ][ ][ ][ ][ ][ ][ ]
```

Assume that a 1 is written into the middle of the buffer (exact starting location does not matter in a circular buffer):

```text
[ ][ ][ ][1][ ][ ][ ]
```

Then assume that two more elements are added — 2 & 3 — which get appended after the 1:

```text
[ ][ ][ ][1][2][3][ ]
```

If two elements are then removed from the buffer, the oldest values inside the buffer are removed.
The two elements removed, in this case, are 1 & 2, leaving the buffer with just a 3:

```text
[ ][ ][ ][ ][ ][3][ ]
```

If the buffer has 7 elements then it is completely full:

```text
[5][6][7][8][9][3][4]
```

When the buffer is full an error will be raised, alerting the client that further writes are blocked until a slot becomes free.

When the buffer is full, the client can opt to overwrite the oldest data with a forced write.
In this case, two more elements — A & B — are added and they overwrite the 3 & 4:

```text
[5][6][7][8][9][A][B]
```

3 & 4 have been replaced by A & B making 5 now the oldest data in the buffer.
Finally, if two elements are removed then what would be returned is 5 & 6 yielding the buffer:

```text
[ ][ ][7][8][9][A][B]
```

Because there is space available, if the client again uses overwrite to store C & D then the space where 5 & 6 were stored previously will be used not the location of 7 & 8.
7 is still the oldest element and the buffer is once again full.

```text
[C][D][7][8][9][A][B]
```

### Customizing and Raising Exceptions

Sometimes it is necessary to both [customize](https://docs.python.org/3/tutorial/errors.html#user-defined-exceptions) and [`raise`](https://docs.python.org/3/tutorial/errors.html#raising-exceptions) exceptions in your code. When you do this, you should always include a **meaningful error message** to indicate what the source of the error is. This makes your code more readable and helps significantly with debugging.

Custom exceptions can be created through new exception classes (see [`classes`](https://docs.python.org/3/tutorial/classes.html#tut-classes) for more detail.) that are typically subclasses of [`Exception`](https://docs.python.org/3/library/exceptions.html#Exception).

For situations where you know the error source will be a derivative of a certain exception type, you can choose to inherit from one of the [`built in error types`](https://docs.python.org/3/library/exceptions.html#base-classes) under the _Exception_ class. When raising the error, you should still include a meaningful message.

This particular exercise requires that you create two _custom exceptions_.  One exception to be [raised](https://docs.python.org/3/reference/simple_stmts.html#the-raise-statement)/"thrown" when your circular buffer is **full**, and one for when it is **empty**. The tests will only pass if you customize appropriate exceptions, `raise` those exceptions, and include appropriate error messages.

To customize a `built-in exception`, create a `class` that inherits from that exception. When raising the custom exception with a message, write the message as an argument to the `exception` type:

```python
# subclassing the built-in BufferError to create BufferFullException
class BufferFullException(BufferError):
    """Exception raised when CircularBuffer is full.

    message: explanation of the error.

    """
    def __init__(self, message):
        self.message = message


# raising a BufferFullException
raise BufferFullException("Circular buffer is full")
```

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

## Read first
- [User-defined exceptions](https://docs.python.org/3/tutorial/errors.html#user-defined-exceptions) — why an exception class is usually nothing but a name and a base class
- [Raising exceptions](https://docs.python.org/3/tutorial/errors.html#raising-exceptions) — `raise Something("message")`, and where that message ends up
- [`BufferError`](https://docs.python.org/3/library/exceptions.html#BufferError) — the built-in base class both given exceptions inherit from
- [`%` on integers](https://docs.python.org/3/reference/expressions.html#binary-arithmetic-operations) — `(index + 1) % capacity` is how a position walks off the end and reappears at the start
- [`collections.deque`](https://docs.python.org/3/library/collections.html#collections.deque) — a ready-made double-ended queue, and `maxlen` if you would rather not do the index arithmetic yourself

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

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
