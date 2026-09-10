---
title: struct — update one record inside a fixed-width binary log
difficulty: medium
tier: advanced
minutes: 20
prereqs: [24]
tags: [stdlib-ops]
---
# struct — update one record inside a fixed-width binary log

*`struct` is the translator between Python values and the exact bytes a binary format says they must be.*

## Read first
- [`struct`](https://devdocs.io/python~3.14/library/struct) — `pack`, `unpack`, `iter_unpack` and `calcsize`
- [Byte order, size, and alignment](https://devdocs.io/python~3.14/library/struct#struct-alignment) — what the leading `<` changes
- [Format characters](https://devdocs.io/python~3.14/library/struct#format-characters) — what `4s`, `H` and `I` each cost

## Why
A meter on a factory floor writes one ten-byte record per station into a file: the station tag, how many readings it has taken, and the running total. The file is read by a C program on the controller, so its layout is fixed and nobody gets to add a comma. When a new reading arrives you have to open the file, find that station's record, add to it, and write the whole thing back with every other record byte-for-byte where it was.

## You get
`blob` — a `bytes` object holding zero or more back-to-back records. Each record is ten bytes: a 4-byte ASCII station tag, then an unsigned 16-bit count, then an unsigned 32-bit total, all little-endian.

`tag` — a `bytes` object of exactly four bytes, the station this reading came from.

`reading` — a non-negative `int`.

## You return
a `bytes` object: the whole log again, updated.

## Rules
- Read the records out of `blob`, in order.
- The record whose tag equals `tag` gets its count raised by one and its total raised by `reading`. Only the first such record, and tags in a log are unique anyway.
- If no record carries that tag, append a new one at the end with count `1` and total `reading`.
- Every other record comes back unchanged, in its original position.
- The format string is `<4sHI`. Counts and totals never overflow their fields.

```python
blob = struct.pack("<4sHI", b"CPU0", 3, 90) + struct.pack("<4sHI", b"MEM1", 1, 12)
solve(blob, b"CPU0", 10)   # -> CPU0 becomes (4, 100), MEM1 untouched
solve(blob, b"NET2", 7)    # -> a third record, (b"NET2", 1, 7), at the end
```

> [!WARNING]
> Drop the `<` and you are asking for native size and alignment, which pads the record out to twelve bytes to keep the 32-bit total on a four-byte boundary. `struct.calcsize("4sHI")` is 12; `struct.calcsize("<4sHI")` is 10. The bytes you write then do not line up with the bytes the controller reads, and `iter_unpack` refuses a blob whose length is not a multiple of what it expects.

> [!NOTE]
> `iter_unpack` walks a buffer record by record and yields a tuple for each one, so you do not have to slice by hand.

## Hints
### Hint 1
`struct.iter_unpack("<4sHI", blob)` yields one `(tag, count, total)` tuple per record. Turn each into a list if you want to change a field in place.
### Hint 2
A `for` loop with an `else` clause is the tidy way to say "I found it, or I never did": the `else` runs only when no `break` happened, which is exactly when the new record has to be appended.
### Hint 3
Packing is the same call in reverse, once per record:

```python
b"".join(struct.pack("<4sHI", tag, count, total) for tag, count, total in records)
```

`4s` takes exactly four bytes: a shorter value is padded with NUL, a longer one is truncated.
