---
title: base64 — a token safe in a URL, and the round trip back to bytes
difficulty: medium
tier: core
minutes: 15
prereqs: [76]
tags: [stdlib-ops, bytes]
---
# base64 — a token safe in a URL, and the round trip back to bytes

*Base64 turns arbitrary bytes into text; the URL-safe alphabet swaps the two characters that a URL would mangle, and the padding is the part everyone forgets.*

## Read first
- [`base64`](https://devdocs.io/python~3.14/library/base64) — the module, and why there is more than one alphabet
- [`base64.urlsafe_b64encode`](https://devdocs.io/python~3.14/library/base64#base64.urlsafe_b64encode) — the `-` and `_` variant
- [`bytes.decode`](https://devdocs.io/python~3.14/library/stdtypes#bytes.decode) — bytes out of the encoder, text into your response

## Why
The reset link the service mails out carries a signed blob of bytes in its path, and the bytes are whatever the signer produced — any of the 256 values. Standard Base64 spells two of its characters `+` and `/`, and both change meaning inside a URL: a proxy reads the slash as another path segment, and a form decoder turns the plus into a space. The link still looks fine in the mail client and fails only for the subset of users whose token happened to contain those bytes, which is the worst kind of bug to be handed. The URL-safe alphabet spells those two `-` and `_` instead. The trailing `=` padding is stripped because it is ugly in a link and, more to the point, is one more character with its own meaning in a query string — which means the decoder on the other end has to put it back.

## You get
- `blobs` — a list of `bytes` objects to turn into tokens.
- `tokens` — a list of tokens already in the wire format, to turn back into `bytes`.

## You return
a tuple `(encoded, decoded)`.

- `encoded` is a list of `str`, one per blob: URL-safe Base64 with every trailing `=` removed.
- `decoded` is a list of `bytes`, one per token: the original bytes each token stands for.

## Rules
- `encoded` holds `str`, not `bytes`. The encoder hands you `bytes`; the output is ASCII, so decoding it is safe.
- Use the URL-safe alphabet in both directions. The two alphabets agree on most inputs and disagree exactly when a blob needs the 62nd or 63rd character, which is when it matters.
- Strip only the `=` padding, and only from the end.
- A token arrives with its padding already gone, and the decoder will refuse a string whose length is not a multiple of four. Put back as many `=` as it takes.

```python
encoded, decoded = solve([b"\xfb\xff?~"], ["-_8_fg"])
encoded   # -> ['-_8_fg']
decoded   # -> [b'\xfb\xff?~']
```

> [!NOTE]
> The number of `=` to add back is `-len(token) % 4` — zero, one or two, never three. Python's `%` on a negative number gives you the non-negative remainder, so this is the whole calculation.

## Hints
### Hint 1
`base64.urlsafe_b64encode(blob)` returns `bytes`, and `bytes.decode("ascii")` turns it into the string you need. `str.rstrip("=")` takes the padding off.
### Hint 2
`base64.urlsafe_b64decode` accepts `str` as well as `bytes`, but it counts characters strictly: three characters in and it raises `binascii.Error` rather than guessing. Re-pad to a multiple of four before you hand it over.
### Hint 3
The two alphabets side by side:

```python
import base64

blob = bytes([251, 255, 63, 126])
base64.b64encode(blob)          # -> b'+/8/fg=='   two characters a URL will not survive
base64.urlsafe_b64encode(blob)  # -> b'-_8_fg=='   same bits, safe spelling
```

Same 64 values, same padding, two characters spelled differently.
