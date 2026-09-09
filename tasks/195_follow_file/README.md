---
title: context managers — follow only newly appended lines
difficulty: medium
tier: core
minutes: 20
prereqs: [73, 102]
tags: [context-managers, file-tailing]
---
# context managers — follow only newly appended lines

*Open a tail reader for one block and guarantee that it closes afterward.*

## Read first
- [contextlib.contextmanager](https://devdocs.io/python~3.14/library/contextlib#contextlib.contextmanager) — turn one `yield` into enter and exit behavior
- [Text I/O](https://devdocs.io/python~3.14/library/io#text-i-o) — `seek`, `read`, and closing a stream

## Why
A log watcher should ignore history and read only lines appended after it starts. It also holds a file descriptor, so its lifetime should be the `with` block rather than an easy-to-forget manual `close()`.

## You get
`path`, a `Path` naming an existing UTF-8 text file.

## You return
A context manager. Entering it yields a zero-argument `read_new` callable. Each call returns only lines appended since the previous call. Leaving the block closes the underlying reader, including when the body raises.

```python
with solve(path) as read_new:
    with path.open("a", encoding="utf-8") as stream:
        stream.write("new\n")
    read_new()  # -> ["new"]
```

## Rules
Open the path for reading and seek to the end before yielding. Define `read_new` to call `read().splitlines()`. Put the `yield read_new` inside `try` and close the stream in `finally`.

## Hints
### Hint 1
This is tailing by cursor position: one open reader remembers where its last `read()` stopped.
### Hint 2
Decorate `solve` with `@contextmanager`, open the stream, and call `stream.seek(0, 2)` before defining the callable.
### Hint 3
`try: yield read_new` hands control to the `with` body. `finally: stream.close()` is the exit path that runs on success and error.
