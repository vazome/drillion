import secrets


def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import random
import string

import pytest
from _lib import rng

_URLSAFE = set(string.ascii_letters + string.digits + "-_")


def _gen(r):
    return r.choice([8, 16, 24, 32, 48])


def _reference():
    def make_token(nbytes):
        return secrets.token_urlsafe(nbytes)

    def check_token(a, b):
        return secrets.compare_digest(a, b)

    return make_token, check_token


def test_solve():
    got = solve()
    assert len(got) == 2, "return the two functions as (make_token, check_token)"
    make_token, check_token = got
    want_make, _ = _reference()

    r = rng()
    for _ in range(6):
        nbytes = _gen(r)
        token = make_token(nbytes)
        assert isinstance(token, str), f"make_token({nbytes}) returned {type(token).__name__}"
        assert len(token) == len(want_make(nbytes)), (
            f"make_token({nbytes}) is {len(token)} characters; "
            f"{nbytes} bytes URL-safe encoded is {len(want_make(nbytes))}"
        )
        assert set(token) <= _URLSAFE, f"{token!r} carries characters a URL would have to escape"
        assert token != make_token(nbytes), f"two calls at {nbytes} bytes returned the same token"

    # the whole difference between the two modules: random replays from a seed, secrets cannot
    random.seed(20260910)
    first = make_token(32)
    random.seed(20260910)
    assert make_token(32) != first, (
        "reseeding random reproduced the token, so it came from random and is predictable"
    )

    token = make_token(24)
    assert check_token(token, token) is True, "a token matches itself, and the answer is a real bool"
    assert check_token(token, token[:-1] + ("a" if token[-1] != "a" else "b")) is False, (
        "a token differing in its last character only must not match"
    )
    assert check_token("a" + token[1:], token) is False, "differing in the first character either"

    with pytest.raises(TypeError):
        check_token(token, token.encode())
    with pytest.raises(TypeError):
        check_token("café", "café")
