def solve(binary_str):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_GESTURES = ["jump", "close your eyes", "double blink", "wink"]


def _gen(r):
    return "".join(r.choice("01") for _ in range(5))


def _reference(binary_str):
    reverse, *bits = [digit == "1" for digit in binary_str]
    actions = [gesture for gesture, bit in zip(_GESTURES, bits) if bit]
    return actions if reverse else actions[::-1]


def test_solve():
    r = rng()
    for _ in range(6):
        binary_str = _gen(r)
        assert solve(binary_str) == _reference(binary_str), f"binary_str {binary_str!r}"

    # canonical cases (exercism/python practice/secret-handshake)
    assert solve("00001") == ["wink"]
    assert solve("00010") == ["double blink"]
    assert solve("00100") == ["close your eyes"]
    assert solve("01000") == ["jump"]
    assert solve("00011") == ["wink", "double blink"]
    assert solve("10011") == ["double blink", "wink"]
    assert solve("11000") == ["jump"]
    assert solve("10000") == []
    assert solve("01111") == ["wink", "double blink", "close your eyes", "jump"]
    assert solve("11111") == ["jump", "close your eyes", "double blink", "wink"]
    assert solve("00000") == []
