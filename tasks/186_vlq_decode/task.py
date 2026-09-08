def solve(stream: list[int]) -> list[int]:
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import pytest
from _lib import rng


def _encode(n):
    """One number as VLQ bytes: seven bits each, top bit set on all but the last."""
    out = [n & 0x7F]
    n >>= 7
    while n:
        out.append(n & 0x7F | 0x80)
        n >>= 7
    return out[::-1]


def _gen(r):
    """A handful of numbers spread across the byte widths, already encoded."""
    numbers = [
        r.choice([r.randint(0, 127), r.randint(128, 16383), r.randint(16384, 2**28 - 1)])
        for _ in range(r.randint(1, 6))
    ]
    return numbers, [b for n in numbers for b in _encode(n)]


def _reference(stream):
    numbers, value, pending = [], 0, False
    for byte in stream:
        value = (value << 7) | (byte & 0x7F)
        pending = bool(byte & 0x80)
        if not pending:
            numbers.append(value)
            value = 0
    if pending:
        raise ValueError("stream ended mid-number")
    return numbers


def test_solve():
    r = rng()
    known = [
        ([0x00], [0]),
        ([0x7F], [127]),
        ([0x81, 0x00], [128]),
        ([0xC0, 0x00], [8192]),
        ([0xFF, 0x7F], [16383]),
        ([0x81, 0x80, 0x00], [16384]),
        ([0x8F, 0xFF, 0xFF, 0xFF, 0x7F], [4294967295]),
        ([0x40, 0x81, 0x00], [64, 128]),
    ]
    for stream, want in known:
        assert solve(list(stream)) == want, f"{[hex(b) for b in stream]} is {want}"

    for _ in range(40):
        numbers, stream = _gen(r)
        assert solve(list(stream)) == _reference(list(stream)) == numbers

    for truncated in ([0x81], [0x40, 0xFF], [0x8F, 0xFF, 0xFF]):
        with pytest.raises(ValueError):
            solve(list(truncated))
