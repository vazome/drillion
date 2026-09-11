---
title: zipfile — build an archive in memory and read one member back
difficulty: medium
tier: core
minutes: 15
prereqs: [54, 75]
tags: [files-text, bytes]
---
# zipfile — build an archive in memory and read one member back

*An archive does not need a directory to live in. `zipfile` writes into any file-like object, and `io.BytesIO` is one.*

## Read first
- [`zipfile.ZipFile`](https://devdocs.io/python~3.14/library/zipfile#zipfile.ZipFile) — the modes, the compression constants, and using it as a context manager
- [`ZipFile.writestr`](https://devdocs.io/python~3.14/library/zipfile#zipfile.ZipFile.writestr) — add a member from a string, with no file on disk
- [`io.BytesIO`](https://devdocs.io/python~3.14/library/io#io.BytesIO) — an in-memory binary file

## Why
The report service has to hand back a zip of four generated files. Writing them into a temporary directory, zipping the directory, reading the zip back and deleting the directory means four chances to leave litter on a disk that is not yours, and a race with the next request doing the same thing. The archive is a few kilobytes and it is on its way out over a socket, so it never has to touch a filesystem at all: a `BytesIO` is a file as far as `zipfile` is concerned.

## You get
- `files`, a dict mapping a member name to its text content, in the order the members should be written.
- `wanted`, one of those names.

## You return
a tuple `(blob, text)`:

- `blob` — the finished archive as `bytes`.
- `text` — the content of `wanted`, read back **out of the finished archive**, as a `str`.

```python
solve({"report.txt": "all clear", "notes.md": "# résumé"}, "notes.md")
# -> (b'PK\x03\x04...', '# résumé')
```

## Rules
- Write the members in the order `files` gives them, compressed with `zipfile.ZIP_DEFLATED`.
- Member content is text; it goes in as UTF-8 and comes back out as UTF-8.
- Read `wanted` back by opening the archive you just built, not by returning the string you already had.

> [!WARNING]
> A zip file is only a zip file once its central directory has been written, and that happens when the `ZipFile` is closed — the moment the `with` block ends. Calling `.getvalue()` while you are still inside the block hands back a truncated blob that no reader will accept.

## Hints
### Hint 1
`io.BytesIO()` gives you the file. `zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED)` writes into it, and `archive.writestr(name, text)` adds a member without touching a disk.
### Hint 2
Two `with` blocks, one after the other: the first writes and closes, and only then is `buffer.getvalue()` a complete archive. The second opens a fresh `ZipFile` over those bytes in read mode.
### Hint 3
Reading a member gives bytes, and decoding is yours to do:

```python
import io, zipfile

buffer = io.BytesIO()
with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
    archive.writestr("a.txt", "ready")
blob = buffer.getvalue()

with zipfile.ZipFile(io.BytesIO(blob)) as archive:
    print(archive.namelist())              # -> ['a.txt']
    print(archive.read("a.txt").decode())  # -> ready
```
