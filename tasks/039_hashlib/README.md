---
title: hashlib — checksum files against a known digest
difficulty: easy
tier: core
minutes: 10
prereqs: []
tags: [stdlib-ops]
---
# hashlib — checksum files against a known digest

*A checksum is how you prove the artifact you deployed is the artifact you built.*

## Why
The release pipeline publishes a checksum (a short fingerprint string computed from a file's bytes) next to every build artifact. Before deploying, you must prove the files that arrived on the server are the exact ones that were built: a single changed byte, from a corrupted download or tampering, must be caught. You compute each file's fingerprint and compare it with the published one.

## You get
`paths` — a list of file path strings, like `["/tmp/x/build-0.bin", "/tmp/x/build-1.bin"]`. The test writes the files and hands you the paths; you never build them yourself.

`known_good` — a string, the correct fingerprint in lowercase hex, like `"9f86d0..."`.

## You return
a dict with `"digests"` (filename to fingerprint), `"match"` and `"bad"` (sorted lists of filenames), as in the rules below.

## Rules
`paths` is a list of file paths (strings). `known_good` is the sha256 hex digest of the artifact you were supposed to receive.

Return exactly:

```python
solve(paths, known_good)
# -> {"digests": {"build-0.bin": "9f86d0...", "build-1.bin": "3a7bd3..."},
#     "match":   ["build-0.bin"],     # digest equals known_good, sorted
#     "bad":     ["build-1.bin"]}     # everything else, sorted
```

- Keys in `"digests"` are basenames, not full paths.
- Digests are lowercase hex strings, which is what `.hexdigest()` already gives you.

> [!WARNING]
> Read each file as BYTES — open in `"rb"`, not text mode. A hash function eats bytes; handing it a decoded string is the usual first error, and on a real binary artifact decoding would fail outright.

These files are small, so read each one whole. For a multi-gigabyte image you would loop over chunks and call `.update()` on the hash object instead of holding the file in memory.

Some of these files differ from the good one by a single byte. A digest turns that one byte into a completely different string, with no way to tell a typo from sabotage — that property is why release pipelines publish checksums at all.

## Hints
### Hint 1
A hash reads bytes and returns a short fixed-length fingerprint. Same bytes in, same fingerprint out, every time and on every machine; one bit different and the fingerprint is unrecognisable. So you never compare files by size or by name — you compare their digests, as strings.
### Hint 2
hashlib.sha256(data) where data is bytes, then .hexdigest() on the result for the lowercase hex string. Open with open(path, 'rb') and .read(), or use pathlib's read_bytes. os.path.basename turns the path into the key. Then it is one pass over the digests dict to split matching from non-matching, sorted at the end.
### Hint 3
Different data, same idea:

```python
import hashlib
print(hashlib.sha256(b'ok').hexdigest()[:16])    # 2689367b205c16ce
print(hashlib.sha256(b'Ok').hexdigest()[:16])    # 843ac01149cced78

with open('/etc/hostname', 'rb') as f:
    print(hashlib.sha256(f.read()).hexdigest())
```

One flipped bit in the input, nothing in common in the output.
