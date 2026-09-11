def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import pytest
from _lib import rng


def _gen(r):
    return {
        "mode": r.choice(["live", "readonly", "degraded"]),
        "region": r.choice(["eu-west-1", "us-east-2", "ap-south-1"]),
        "replicas": r.randint(1, 8),
    }


def _reference():
    class Window:
        def __init__(self, settings):
            self.settings = settings

        def __enter__(self):
            self.previous = self.settings["mode"]
            self.settings["mode"] = "maintenance"
            return self.previous

        def __exit__(self, exc_type, exc_value, traceback):
            self.settings["mode"] = self.previous
            if exc_type is TimeoutError:
                return True

    return Window


def test_solve():
    r = rng()
    window = solve()

    for _ in range(6):
        settings = _gen(r)
        before = dict(settings)
        with window(settings) as previous:
            assert previous == before["mode"], f"__enter__ must return the old mode for {before}"
            assert settings["mode"] == "maintenance", f"mode inside the block for {before}"
            assert settings["region"] == before["region"], f"no other key moves for {before}"
        assert settings == before, f"everything restored after a clean block for {before}"

    settings = _gen(r)
    before = dict(settings)
    with window(settings):
        raise TimeoutError("queue still draining")
    assert settings == before, "the mode goes back even when the block times out"

    # `return True` at the end of __exit__ passes every test above and swallows this one
    settings = _gen(r)
    before = dict(settings)
    with pytest.raises(ValueError), window(settings):
        raise ValueError("bad payload")
    assert settings == before, "the mode goes back even when the block raises"

    settings = _gen(r)
    manager = window(settings)
    manager.__enter__()
    absorbed = manager.__exit__(TimeoutError, TimeoutError("drain"), None)
    assert absorbed is True, "__exit__ must return True for TimeoutError"
    manager = window(settings)
    manager.__enter__()
    passed_on = manager.__exit__(KeyError, KeyError("region"), None)
    assert not passed_on, "__exit__ must not report a KeyError as handled"
