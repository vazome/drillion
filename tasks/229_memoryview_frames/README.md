---
title: memoryview — cut a buffer into frames without copying a single byte
difficulty: medium
tier: advanced
minutes: 15
prereqs: [8]
tags: [slicing, bytes]
---
# memoryview — cut a buffer into frames without copying a single byte

*Slicing a `bytes` or `bytearray` copies it. Slicing a `memoryview` of it does not — you get a window onto the same memory, and writing through the window changes the original.*

## Read first
- [`memoryview`](https://devdocs.io/python~3.14/library/stdtypes#memoryview) — the type, its slicing, and `.obj`
- [Buffer protocol](https://devdocs.io/python~3.14/c-api/buffer) — what "supports the buffer protocol" means
- [`bytearray`](https://devdocs.io/python~3.14/library/stdtypes#bytearray) — the mutable one

## Why
The capture card hands you one flat buffer holding a few hundred fixed-size frames, and the worker that stamps a checksum into each frame's header wants them one at a time. Written the obvious way — `buf[i:i+size]` — every frame is a fresh copy, so a buffer read once is now allocated twice, and the stamp the worker writes lands on the copy and is thrown away with it. The bug does not look like a memory bug: it looks like the checksums silently never arriving. A `memoryview` is a window rather than a copy, which fixes both halves at once, and slicing a window gives you a smaller window.

## You get
- `buf`, a `bytearray` holding the whole capture.
- `frame_size`, how many bytes one frame occupies.

## You return
a list of `memoryview` objects, one per frame, in order, each one a window onto `buf`.

## Rules
- Every element is a `memoryview`, and every one of them views `buf` itself. Copying the bytes out and wrapping the copy passes a naive comparison and fails the point of the task.
- `buf` is not always a whole number of frames. The trailing partial frame is a frame too, shorter than the others; do not drop it and do not pad it.
- Do not modify `buf`. The caller does that later, through the windows you hand back.
- The list is in buffer order: the frame starting at byte 0 first.

```python
buf = bytearray(b"ABCDEFGHIJ")
frames = solve(buf, 4)
[bytes(f) for f in frames]   # -> [b'ABCD', b'EFGH', b'IJ']
frames[1][0] = 0x7A
bytes(buf)                   # -> b'ABCDzFGHIJ'
```

> [!WARNING]
> `memoryview(buf[0:4])` and `memoryview(buf)[0:4]` read the same four bytes and are not the same object at all. The first copies four bytes out and views the copy — the original is untouched by anything written through it. Build the view once, then slice the view.

## Hints
### Hint 1
`memoryview(buf)` is cheap and does not copy. Slicing that view with `view[a:b]` is also cheap and also does not copy — a slice of a view is a view.
### Hint 2
`range(0, len(buf), frame_size)` gives you every frame's starting offset, and a slice that runs off the end of a sequence stops at the end rather than raising. That is the trailing partial frame, for free.
### Hint 3
A view remembers what it is looking at:

```python
buf = bytearray(b"hello world")
view = memoryview(buf)
window = view[6:]
window.obj is buf     # -> True, no copy anywhere in the chain
window[0] = ord("W")
bytes(buf)            # -> b'hello World'

memoryview(buf[6:]).obj is buf   # -> False, the bytearray slice already copied
```
