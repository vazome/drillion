def solve(buf, frame_size):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    frame_size = r.randint(3, 9)
    frames = r.randint(4, 9)
    # a deliberate remainder so the trailing partial frame is exercised
    length = frame_size * frames + r.choice([0, 1, frame_size - 1])
    return bytearray(r.randrange(256) for _ in range(length)), frame_size


def _reference(buf, frame_size):
    view = memoryview(buf)
    return [view[i : i + frame_size] for i in range(0, len(buf), frame_size)]


def test_solve():
    r = rng()
    buf, frame_size = _gen(r)
    original = bytes(buf)

    frames = solve(buf, frame_size)
    want = _reference(buf, frame_size)

    assert len(frames) == len(want), f"{len(buf)} bytes at {frame_size} each is {len(want)} frames"
    for i, (got, expected) in enumerate(zip(frames, want)):
        assert isinstance(got, memoryview), f"frame {i} must be a memoryview"
        assert bytes(got) == bytes(expected), f"frame {i} contents"
        assert got.obj is buf, f"frame {i} views a copy — slice the view, not the bytearray"
    assert bytes(buf) == original, "solve must not modify the buffer"

    # the reason for all of this: a write through a window lands in the caller's buffer
    frames[1][0] = (original[frame_size] + 1) % 256
    assert buf[frame_size] == (original[frame_size] + 1) % 256, (
        "writing through a frame must change the original buffer"
    )

    canonical = solve(bytearray(b"ABCDEFGHIJ"), 4)
    assert [bytes(f) for f in canonical] == [b"ABCD", b"EFGH", b"IJ"], (
        "the trailing partial frame is a frame too"
    )
