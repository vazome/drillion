---
title: Knuth-Morris-Pratt — find every marker in a stream that arrives in chunks
difficulty: hard
tier: advanced
minutes: 25
prereqs: [10, 140]
tags: [strings, loops]
source: TheAlgorithms/Python strings/knuth_morris_pratt.py (MIT, adapted)
---
# Knuth-Morris-Pratt — find every marker in a stream that arrives in chunks

*A scan that never looks at the same character twice, and never has to hold more than one chunk, because a small table says where to resume after a mismatch.*

## Read first
- [Common string operations](https://devdocs.io/python~3.14/library/stdtypes#string-methods) — `str.find` is the search you are replacing, and it is worth knowing exactly what it cannot do here
- [Sequence slicing](https://devdocs.io/python~3.14/library/stdtypes#common-sequence-operations) — the failure table is built by comparing a prefix of the marker against its own later characters
- [`enumerate`](https://devdocs.io/python~3.14/library/functions#enumerate) — you need each character *and* where it sat in the chunk, because the answer is an offset into the whole stream
- [while](https://devdocs.io/python~3.14/reference/compound_stmts#the-while-statement) — the inner retreat on a mismatch is a `while`, not an `if`, and that is the part people get wrong

## Why
A device uploads a rolling capture and your collector reads it a buffer at a time: 4 KB here, 900 bytes there, whatever the socket hands over. Somewhere in that capture are records, each one introduced by a fixed marker, and you want the offset of every marker so a later pass can cut the capture into records.

The obvious loop — search each chunk as it arrives — quietly loses every marker that happened to be split across two reads, and the split is not rare: it is whatever the network decided. Joining the whole stream into one string first fixes the correctness and trades it for a memory bill that grows with the upload, which is the thing streaming was supposed to avoid.

What you actually need is a searcher that remembers how far into the marker it had got when the chunk ran out. Knuth-Morris-Pratt is that searcher. It precomputes, for each position in the marker, how far to fall back after a mismatch, and because of that table it never re-reads a character of the stream. The state it carries between chunks is one integer.

## You get
- `chunks` — a list of `str`, the stream in arrival order. Concatenated they are the whole capture. Any chunk may be empty, and the list may be empty.
- `marker` — a `str` of at least one character, the sequence you are looking for.

## You return
A `list` of `int` — the start offset of every occurrence of `marker`, counted from the beginning of the **whole stream**, in increasing order. An empty list when there are none.

## Rules
- offsets are absolute. `solve(["ab", "cab"], "ab")` is `[0, 3]`, not `[0, 1]`
- occurrences **overlap**. `solve(["AAAA"], "AA")` is `[0, 1, 2]`, three answers from four characters
- an occurrence that straddles a chunk boundary counts, and its offset is where it starts, which may be in an earlier chunk than the one that completed it
- a chunk boundary must change nothing about the answer: the same stream cut differently gives the same list
- build the failure table from `marker` once, before the scan. Rebuilding it per chunk is the same answer and a pointless one
- do not join `chunks` into one string. The whole point of the exercise is that you never hold more of the stream than the chunk in your hand

```python
solve(["AB", "ABAB"], "ABAB")   # -> [0, 2]
solve(["AAAA"], "AA")           # -> [0, 1, 2]
solve(["hello ", "world"], "o w")  # -> [4]
solve([], "x")                  # -> []
```

> [!WARNING]
> `[chunk.find(marker) for chunk in chunks]` and every variation of it is the wrong answer, and it is wrong in the way that matters: the first example above has a marker sitting at offset 0, spread across both chunks, and a per-chunk search reports only the one at offset 2. The test cuts the same stream at boundaries chosen by the seed, so a per-chunk search fails on data you did not pick.

> [!NOTE]
> After a full match, do not reset your position in the marker to zero. Falling back through the table instead is what finds the overlapping occurrence in `"AAAA"`.

## Hints
### Hint 1
Two pieces, and build them in this order. First the table: `failure[j]` is the length of the longest piece of `marker[:j+1]` that is both a prefix and a suffix of it. For `"ABAB"` that is `[0, 0, 1, 2]` — after matching all four characters, two of them (`"AB"`) are already a prefix, so a fresh attempt starts two characters in rather than from nothing. Build it by matching the marker against itself with the same two-index walk you are about to write for the stream.

### Hint 2
Then the scan. Keep one integer `j`, how many characters of the marker match so far, and let it live **outside** the `for chunk in chunks` loop — that is the whole trick, and it is the only state a chunk boundary has to survive. Keep a second integer for how many characters of the stream you have already passed, so you can turn a position inside a chunk into an absolute offset.

For each character: while `j` is greater than zero and the character does not match `marker[j]`, set `j = failure[j - 1]` and look again. Then if it matches, `j += 1`. When `j` reaches `len(marker)` you have a hit, its offset is the current absolute position minus `len(marker) - 1`, and `j = failure[j - 1]` sets you up for an overlap.

### Hint 3
Same table, different data — the rolling check a log shipper does for a multi-line traceback delimiter:

```python
def failure_table(pattern):
    table, i, j = [0], 0, 1
    while j < len(pattern):
        if pattern[i] == pattern[j]:
            i += 1
        elif i > 0:
            i = table[i - 1]
            continue
        j += 1
        table.append(i)
    return table

failure_table("aabaabaaa")   # -> [0, 1, 0, 1, 2, 3, 4, 5, 2]
failure_table("abcd")        # -> [0, 0, 0, 0]
```

The second one is all zeros: no prefix of `"abcd"` is also a suffix, so a mismatch always sends you back to the start. A marker with repetition in it is where the table earns its keep.

---
Adapted from TheAlgorithms/Python — MIT
