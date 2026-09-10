def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from collections import abc

import pytest
from _lib import rng


def _gen(r):
    return {
        "host": r.choice(["10.0.0.4", "db.internal", "127.0.0.1"]),
        "port": r.choice([5432, 3306, 6379]),
        "pool": {"max": r.randint(2, 64), "idle": {"seconds": r.randint(1, 90)}},
        "regions": [{"id": code} for code in r.sample(["eu", "us", "ap", "sa"], 2)] + ["global"],
    }


def _reference():
    class Config:
        def __init__(self, mapping):
            object.__setattr__(self, "_data", dict(mapping))

        def keys(self):
            return self._data.keys()

        def __getattr__(self, name):
            try:
                value = self._data[name]
            except KeyError:
                raise AttributeError(name) from None
            return _wrap(value)

        def __setattr__(self, name, value):
            raise AttributeError(f"{name!r} is read-only")

    def _wrap(value):
        if isinstance(value, abc.Mapping):
            return Config(value)
        if isinstance(value, list):
            return [_wrap(item) for item in value]
        return value

    return Config


def test_solve():
    r = rng()
    config, want = solve(), _reference()

    for _ in range(6):
        raw = _gen(r)
        mine, theirs = config(raw), want(raw)
        assert sorted(mine.keys()) == sorted(theirs.keys()), f"keys for {sorted(raw)}"
        assert mine.host == theirs.host and mine.port == theirs.port, f"scalars for {raw['host']}"
        assert mine.pool.max == theirs.pool.max, "a nested mapping is wrapped too"
        assert mine.pool.idle.seconds == theirs.pool.idle.seconds, "and so is one nested in that"
        assert type(mine.pool) is config, "a nested mapping comes back as a Config"
        assert [x.id for x in mine.regions[:-1]] == [x.id for x in theirs.regions[:-1]], "list items"
        assert mine.regions[-1] == "global", "a non-mapping in a list is left alone"

    cfg = config({"db": {"host": "10.0.0.4"}, "timeout": 30})

    # returning None for a missing name makes hasattr lie, and the misconfiguration silent
    with pytest.raises(AttributeError):
        _ = cfg.retries
    assert not hasattr(cfg, "retries"), "a missing setting must not answer hasattr"
    assert not hasattr(cfg.db, "port"), "the same holds one level down"

    # without the guard the assignment shadows the lookup, and the next read returns the shadow
    with pytest.raises(AttributeError):
        cfg.timeout = 45
    assert cfg.timeout == 30, "the config still reads what the mapping said"
    with pytest.raises(AttributeError):
        cfg.brand_new = 1
    assert not hasattr(cfg, "brand_new"), "and nothing was stored"
