---
title: bytes and codecs — decode a log that is not quite UTF-8, and keep the line anyway
difficulty: medium
tier: advanced
minutes: 18
prereqs: [228]
tags: [bytes, files-text]
---
# bytes and codecs — decode a log that is not quite UTF-8, and keep the line anyway

*Decoding is a decision, not a formality: the same bytes are a crash, a mangled line or a silent lie depending on which codec and which error handler you named.*

## Read first
- [`bytes.decode`](https://devdocs.io/python~3.14/library/stdtypes#bytes.decode) and [`str.encode`](https://devdocs.io/python~3.14/library/stdtypes#str.encode) — the `encoding` and `errors` arguments
- [Error handlers](https://devdocs.io/python~3.14/library/codecs#error-handlers) — what `strict`, `replace` and `backslashreplace` each do
- [`UnicodeDecodeError`](https://devdocs.io/python~3.14/library/exceptions#UnicodeDecodeError) — the exception `strict` raises, and the byte it names

## Why
An ingest pipeline reads log lines from a dozen services. Eleven of them write UTF-8. The twelfth writes whatever a Windows box from 2011 wrote, and two lines an hour arrive with a byte that is not valid UTF-8 in any reading of it. Crashing is not an option — the other eleven services' lines are fine and the pipeline has to keep moving. Nor is quietly decoding everything as Latin-1, which never raises and therefore never tells anyone anything: the mangled line looks like ordinary text, gets indexed, and the team finds out two months later from a customer. What is wanted is both: every line comes through readable, and the ones that had to be repaired are counted, so somebody can go and fix the twelfth service.

## You get
`records`, a list of `bytes` — one log line each. Most are valid UTF-8, a few are not, and at least one of the valid ones legitimately contains the replacement character `�` because a service upstream already did this repair once.

## You return
a dict with exactly three keys:

| key | value |
|---|---|
| `text` | every record as a `str`, in order: decoded as UTF-8, repaired with the `replace` handler where that was needed |
| `bad` | the indexes of the records that are not valid UTF-8, ascending |
| `ascii` | `text` joined with `"\n"` and encoded to ASCII with the `backslashreplace` handler, as `bytes` |

## Rules
- A record is bad when decoding it as UTF-8 with the default strict handler **raises**. That is the only definition you may use.
- Searching the decoded text for `�` is not that definition. A record that was already valid UTF-8 and contained a replacement character is not bad, and there is one of those in every set.
- Nothing raises out of `solve`, and nothing is dropped: `text` is the same length as `records`, bad records included.
- `ascii` is real `bytes` and contains only bytes below 128. Every character that does not fit becomes its `\xNN` or `\uNNNN` escape rather than being lost or replaced.
- `bad` is a list of ints.

```python
solve([b"caf\xc3\xa9", b"caf\xe9", "already � here".encode()])
# -> {'text': ['café', 'caf�', 'already � here'],
#     'bad': [1],
#     'ascii': b'caf\\xe9\ncaf\\ufffd\nalready \\ufffd here'}
```

> [!NOTE]
> `b"caf\xe9"` is `café` in Latin-1 and invalid in UTF-8, and `"café".encode()` is `b"caf\xc3\xa9"`. Nothing in the bytes says which was meant — that is why the encoding is an argument and not a detail the decoder can work out for itself.

## Hints
### Hint 1
Two passes over the same record, and the first one is in a `try`. The strict decode tells you whether the record is bad; the lenient one gives you something to keep either way.
### Hint 2
`errors="replace"` never raises, so once you know the record is bad you can decode it again and be sure of the result. Decoding twice costs nothing worth thinking about here.
### Hint 3
Both directions, with the handler named each time:

```python
raw = b"temp=23\xb0C"

raw.decode("utf-8")                          # UnicodeDecodeError: invalid start byte at position 7
raw.decode("utf-8", errors="replace")        # -> 'temp=23�C'
raw.decode("latin-1")                        # -> 'temp=23°C' — plausible, and a guess

"temp=23°C".encode("ascii", "backslashreplace")   # -> b'temp=23\\xb0C'
"temp=23°C".encode("ascii", "replace")             # -> b'temp=23?C', and the degree sign is gone for good
```

`backslashreplace` is the one to reach for in a report, because it is the only handler here that loses nothing: the escape says exactly which character was there.
