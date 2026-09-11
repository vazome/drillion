import struct


def solve(blob: bytes, tag: bytes, reading: int) -> bytes:
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_RECORD = "<4sHI"


def _gen(r):
    tags = [b"CPU0", b"MEM1", b"NET2", b"DSK3", b"FAN4", b"PSU5"]
    present = r.sample(tags, r.randint(1, 4))
    blob = b"".join(
        struct.pack(_RECORD, t, r.randint(0, 500), r.randint(0, 50_000)) for t in present
    )
    # half the time aim at a station the log has never seen, so the append branch runs
    wanted = r.choice(present) if r.random() < 0.5 else r.choice([t for t in tags if t not in present] or tags)
    return blob, wanted, r.randint(0, 400)


def _reference(blob, tag, reading):
    records = [list(rec) for rec in struct.iter_unpack(_RECORD, blob)]
    for rec in records:
        if rec[0] == tag:
            rec[1] += 1
            rec[2] += reading
            break
    else:
        records.append([tag, 1, reading])
    return b"".join(struct.pack(_RECORD, *rec) for rec in records)


def test_solve():
    canonical = struct.pack(_RECORD, b"CPU0", 3, 90) + struct.pack(_RECORD, b"MEM1", 1, 12)
    got = solve(canonical, b"CPU0", 10)
    assert got == struct.pack(_RECORD, b"CPU0", 4, 100) + struct.pack(_RECORD, b"MEM1", 1, 12), (
        "raising CPU0 must leave MEM1 byte-for-byte where it was"
    )
    assert solve(canonical, b"NET2", 7) == canonical + struct.pack(_RECORD, b"NET2", 1, 7), (
        "an unknown tag appends a record with count 1"
    )

    r = rng()
    for _ in range(8):
        blob, tag, reading = _gen(r)
        mine = solve(blob, tag, reading)
        assert isinstance(mine, bytes), f"return bytes, not {type(mine).__name__}"
        # native alignment pads the record to 12 bytes; only "<" gives the 10 the format promises
        assert len(mine) % 10 == 0, f"a record is 10 bytes, got a log of {len(mine)} for tag {tag!r}"
        assert mine == _reference(blob, tag, reading), f"log after {tag!r} += {reading}"
