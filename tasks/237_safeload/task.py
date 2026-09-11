import io
import pickle
from dataclasses import dataclass, field


@dataclass
class Snapshot:
    host: str
    checks: dict = field(default_factory=dict)


def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import collections
import os

import pytest
from _lib import rng

_HOSTS = ["web-01", "web-02", "db-primary", "cache-3", "edge-eu"]
_CHECKS = ["disk", "tls", "clock", "memory", "queue"]


def _gen(r):
    names = r.sample(_CHECKS, r.randint(0, 4))
    return Snapshot(r.choice(_HOSTS), {n: r.choice(["ok", "warn", "fail"]) for n in names})


def _reference():
    class _OnlySnapshot(pickle.Unpickler):
        def find_class(self, module, name):
            if (module, name) == (Snapshot.__module__, Snapshot.__qualname__):
                return Snapshot
            raise pickle.UnpicklingError(f"{module}.{name} is not allowed here")

    return pickle.dumps, lambda blob: _OnlySnapshot(io.BytesIO(blob)).load()


def test_solve():
    r = rng()
    got = solve()
    assert len(got) == 2, "return the two callables as (dump, load)"
    dump, load = got
    ref_dump, ref_load = _reference()

    for _ in range(8):
        snap = _gen(r)
        blob = dump(snap)
        assert isinstance(blob, bytes), f"dump must return bytes, got {type(blob).__name__}"
        back = load(blob)
        assert back == snap, f"round trip changed {snap}"
        assert back is not snap, "load must rebuild the object, not hand back the original"
        # the format has to be pickle: the grader's loader reads your bytes and yours reads its
        assert ref_load(blob) == snap, f"the grader could not read your bytes for {snap}"
        assert load(ref_dump(snap)) == snap, f"could not read the grader's pickle of {snap}"

    # three payloads the collector never wrote, none of them dangerous, all of them refused
    for hostile in (os.getcwd, collections.Counter("ab"), {"cls": pickle.Pickler}):
        with pytest.raises(pickle.UnpicklingError):
            load(pickle.dumps(hostile))
