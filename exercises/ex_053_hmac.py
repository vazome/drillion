"""A webhook endpoint that skips the signature check is an open door into your pipeline."""

import hashlib
import hmac

from _lib import rng

META = {"topic": 53, "title": "webhooks — verify an HMAC signature",
        "tier": 3, "minutes": 12, "prereqs": []}


def solve(secret, body, signature):
    """Decide whether this webhook really came from someone holding the secret.

    Arguments:
      - secret: bytes, the shared secret both sides know.
      - body: bytes, the exact raw request body as it arrived.
      - signature: str, the value of the signature header. GitHub-style,
        it looks like "sha256=" followed by 64 lowercase hex characters.

    Return True or False (a bool, nothing else).

    What to do:
      - If signature does not start with "sha256=", return False. Junk
        in the header is not an error to raise, it is a failed check.
      - Compute the HMAC-SHA256 of body under secret and take its
        hexdigest. That is the value the sender should have produced.
      - Compare it with the hex part of the header using
        hmac.compare_digest.

        secret = b"s3cr3t"
        body   = b'{"action":"deploy"}'
        good   = "sha256=" + hmac.new(secret, body, hashlib.sha256).hexdigest()
        solve(secret, body, good)               -> True
        solve(secret, body + b" ", good)        -> False
        solve(secret, body, "deadbeef")         -> False

    Two things worth being able to say out loud:

    Why not `==`. String comparison returns the moment two characters
    differ, so a wrong signature that shares a longer prefix takes
    measurably longer to reject. An attacker who can time your endpoint
    guesses the signature one character at a time — 64 * 16 tries
    instead of 16 ** 64. compare_digest takes the same time either way.

    Why the raw bytes. Sign what arrived, not the result of parsing and
    re-serialising it. One reordered key or one space of difference and
    the digest no longer matches.
    """
    raise NotImplementedError


HINTS = [
    "You are not decrypting anything. HMAC is one-way: the same secret over "
    "the same bytes always gives the same digest, so you recompute it and "
    "see whether it matches what the caller claimed. Two details do the "
    "damage here — the header is not bare hex, and the comparison itself "
    "has a security requirement.",
    "hmac.new(secret, body, hashlib.sha256).hexdigest() gives you 64 "
    "lowercase hex characters. Use str.startswith for the 'sha256=' label "
    "and slice past it, or signature.split('=', 1). Finish with "
    "hmac.compare_digest(claimed, computed) — it takes two str or two "
    "bytes, returns a bool, and does not raise on a length mismatch.",
    "Different data — signing a tiny message:\n"
    "    import hmac, hashlib\n"
    "    key, msg = b'key', b'ping'\n"
    "    sig = hmac.new(key, msg, hashlib.sha256).hexdigest()\n"
    "    print(sig[:8])                                   # 774ebd4d\n"
    "    print(hmac.compare_digest(sig, sig))             # True\n"
    "    print(hmac.compare_digest(sig, '0' * len(sig)))  # False\n"
    "    print(hmac.new(key, msg + b'!', hashlib.sha256).hexdigest()[:8])\n"
    "    #  a totally different digest — one byte changes everything\n"
    "Your version does the same three moves after peeling the label off "
    "the header.",
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _payload(r):
    secret = bytes(r.randrange(256) for _ in range(r.randint(8, 24)))
    body = (b'{"repo":"' + r.choice([b"api", b"web", b"infra"])
            + b'","run":' + str(r.randint(1, 9999)).encode() + b"}")
    return secret, body


def _gen(r):
    secret, body = _payload(r)
    good = hmac.new(secret, body, hashlib.sha256).hexdigest()
    case = r.choice(["valid", "valid", "tampered", "wrong-secret", "no-prefix",
                     "truncated", "forged", "empty", "label-only"])
    if case == "valid":
        return secret, body, "sha256=" + good
    if case == "tampered":                       # body edited after signing
        return secret, body + b" ", "sha256=" + good
    if case == "wrong-secret":
        other = bytes(r.randrange(256) for _ in range(12))
        return secret, body, "sha256=" + hmac.new(other, body, hashlib.sha256).hexdigest()
    if case == "no-prefix":
        return secret, body, good
    if case == "truncated":
        return secret, body, "sha256=" + good[:-1]
    if case == "forged":
        return secret, body, "sha256=" + f"{r.randrange(16 ** 64):064x}"
    if case == "empty":
        return secret, body, ""
    return secret, body, "sha256="


def _reference(secret, body, signature):
    prefix = "sha256="
    if not signature.startswith(prefix):
        return False
    expected = hmac.new(secret, body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature[len(prefix):], expected)


def test_solve():
    r = rng()
    for _ in range(8):
        case = _gen(r)
        assert solve(*case) == _reference(*case)

    # a function that always answers False must not pass
    secret, body = _payload(r)
    good = "sha256=" + hmac.new(secret, body, hashlib.sha256).hexdigest()
    assert solve(secret, body, good) is True
    assert solve(secret, body + b"x", good) is False
