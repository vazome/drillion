---
title: secrets — issue an unguessable token and compare it without leaking the answer
difficulty: medium
tier: core
minutes: 18
prereqs: [42]
tags: [stdlib-ops, functions]
---
# secrets — issue an unguessable token and compare it without leaking the answer

*`random` is a machine for producing numbers you can reproduce, which is the whole reason it must never issue a secret.*

## Read first
- [`secrets`](https://devdocs.io/python~3.14/library/secrets) — the module, and the note at the top of it about `random`
- [`token_urlsafe`](https://devdocs.io/python~3.14/library/secrets#secrets.token_urlsafe) — bytes of entropy in, a string safe for a URL out
- [`compare_digest`](https://devdocs.io/python~3.14/library/secrets#secrets.compare_digest) — comparing two secrets in constant time

## Why
A service emails a one-time link so somebody can reset a password. Two things have to be true about the token in that link, and both of them are about an attacker rather than about a user. It has to be unguessable: `random` is seeded from a value an attacker can often work out, and given a few tokens you can reconstruct its state and predict every future one — the module's own documentation says not to use it for this. And checking it has to take the same time whether the first character is wrong or only the last one is, because `==` stops at the first difference and the microseconds it saves are enough to recover the token one character at a time.

## You get
nothing to start — you return two functions. The test calls them itself, like

```python
make_token, check_token = solve()
token = make_token(32)
check_token(token, submitted)
```

## You return
a tuple of the two functions, in the order `(make_token, check_token)`.

## Rules
`make_token(nbytes)` returns a fresh token:

- a `str`, safe to put in a URL, carrying `nbytes` bytes of randomness.
- drawn from the operating system's source of randomness, so two calls never agree and seeding `random` has no effect on it whatsoever.

`check_token(a, b)` returns whether two tokens match:

- a real `bool` — `True` or `False`, not a truthy value.
- compared in constant time, so the answer takes as long to reach when the first character differs as when the last one does.
- it does **not** paper over a type mismatch: comparing a `str` to a `bytes`, or handing it a `str` with a character outside ASCII, raises `TypeError` rather than quietly answering `False`.

```python
make_token, check_token = solve()
make_token(16)                    # -> e.g. 'ZQpv7X0kL2mA-fRnCw3tYQ', a different one each call
check_token("abc123", "abc123")   # -> True
check_token("abc123", "abc124")   # -> False
check_token("abc123", b"abc123")  # -> TypeError
```

> [!WARNING]
> `"".join(random.choice(alphabet) for _ in range(n))` produces a string that looks exactly as random as the right answer and is not. The test seeds `random` to the same value twice and asks for a token each time; a token drawn from `random` comes back identical both times, and that is the whole difference between the two modules made visible.

> [!NOTE]
> The last rule is not an inconvenience to work around. `compare_digest` raises on a type mismatch because silently answering `False` would hide the real bug — a token that arrived as bytes and was checked against a string would fail every login for a reason nobody could find.

## Hints
### Hint 1
Both functions are one call each, from the same module. You are choosing the right two names out of `secrets`, not implementing anything.
### Hint 2
`secrets.token_urlsafe(nbytes)` is the token: base64 with a URL-safe alphabet, so it survives being pasted into a link, and roughly four characters for every three bytes you asked for.
### Hint 3
`compare_digest` already returns a `bool` and already raises `TypeError` on mixed types, so
whatever it hands back is what your function hands back. Here is the same pair of ideas doing a
different job — signing a webhook rather than checking a link:

```python
import hashlib
import hmac
import secrets

key = secrets.token_bytes(32)                      # the shared secret, never from random
sent = hmac.new(key, b"payload", hashlib.sha256).hexdigest()
mine = hmac.new(key, b"payload", hashlib.sha256).hexdigest()
secrets.compare_digest(sent, mine)                 # -> True, in constant time
```

`token_bytes` and `token_urlsafe` draw from the same source and differ only in what they hand
you; `compare_digest` is the same call either way.
