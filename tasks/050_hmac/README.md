---
title: webhooks — verify an HMAC signature
difficulty: medium
tier: core
minutes: 12
prereqs: [18]
tags: [http]
---
# webhooks — verify an HMAC signature

*A webhook endpoint that skips the signature check is an open door into your pipeline.*

## Read first
- [hmac](https://devdocs.io/python~3.14/library/hmac) — signing, and `compare_digest` for the constant-time check

## Why
Your CI pipeline has a web address that GitHub calls every time code is pushed (a webhook), and that call triggers a deploy. Anyone on the internet can send a request to that address. To prove a message is really from GitHub, both sides share a secret; GitHub computes a fingerprint of the message using that secret and sends it in a header. You recompute the fingerprint yourself and compare. Skip the check and anyone can trigger deploys; compare carelessly and an attacker can guess the fingerprint one character at a time by timing your replies. The security team asks you to write the check.

## You get
`secret` — bytes: the shared secret both sides know, like `b"s3cr3t"`.

`body` — bytes: the exact raw message as it arrived, like `b'{"action":"deploy"}'`.

`signature` — a string from the request header, normally `"sha256="` followed by 64 hex characters. The test also hands in junk, truncated, wrong and empty values.

## You return
`True` if the signature proves the message is genuine, `False` in every other case. Never raise an error.

## Rules
Decide whether this webhook really came from someone holding the secret.

Arguments:

- `secret`: bytes, the shared secret both sides know.
- `body`: bytes, the exact raw request body as it arrived.
- `signature`: str, the value of the signature header. GitHub-style, it looks like `"sha256="` followed by 64 lowercase hex characters.

Return `True` or `False` (a bool, nothing else).

What to do:

- If `signature` does not start with `"sha256="`, return `False`. Junk in the header is not an error to raise, it is a failed check.
- Compute the HMAC-SHA256 of `body` under `secret` and take its hexdigest. That is the value the sender should have produced.
- Compare it with the hex part of the header using `hmac.compare_digest`.

```python
secret = b"s3cr3t"
body   = b'{"action":"deploy"}'
good   = "sha256=" + hmac.new(secret, body, hashlib.sha256).hexdigest()
solve(secret, body, good)          # -> True
solve(secret, body + b" ", good)   # -> False
solve(secret, body, "deadbeef")    # -> False
```

Two things worth being able to say out loud:

**Why not `==`.** String comparison returns the moment two characters differ, so a wrong signature that shares a longer prefix takes measurably longer to reject. An attacker who can time your endpoint guesses the signature one character at a time — 64 * 16 tries instead of 16 ** 64. `compare_digest` takes the same time either way.

**Why the raw bytes.** Sign what arrived, not the result of parsing and re-serialising it. One reordered key or one space of difference and the digest no longer matches.

## Hints
### Hint 1
You are not decrypting anything. HMAC is one-way: the same secret over the same bytes always gives the same digest, so you recompute it and see whether it matches what the caller claimed. Two details do the damage here — the header is not bare hex, and the comparison itself has a security requirement.
### Hint 2
hmac.new(secret, body, hashlib.sha256).hexdigest() gives you 64 lowercase hex characters. Use str.startswith for the 'sha256=' label and slice past it, or signature.split('=', 1). Finish with hmac.compare_digest(claimed, computed) — it takes two str or two bytes, returns a bool, and does not raise on a length mismatch.
### Hint 3
Different data — signing a tiny message:

```python
import hmac, hashlib
key, msg = b'key', b'ping'
sig = hmac.new(key, msg, hashlib.sha256).hexdigest()
print(sig[:8])                                   # 774ebd4d
print(hmac.compare_digest(sig, sig))             # True
print(hmac.compare_digest(sig, '0' * len(sig)))  # False
print(hmac.new(key, msg + b'!', hashlib.sha256).hexdigest()[:8])
#  a totally different digest — one byte changes everything
```

Your version does the same three moves after peeling the label off the header.
