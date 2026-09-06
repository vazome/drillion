def solve(secret: bytes, body: bytes, signature: str):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import hashlib
import hmac

from _lib import rng


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
