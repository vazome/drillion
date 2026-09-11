def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import pytest
from _lib import rng

_NAMES = ["db_host", "log_level", "retry_after", "queue_url", "region", "timeout"]


def _gen(r):
    stored = {}
    for name in r.sample(_NAMES, r.randint(2, 5)):
        key = name.upper() if r.random() < 0.5 else name
        stored[key] = f"v{r.randint(10, 99)}"
    lookups = [r.choice(_NAMES) for _ in range(4)]
    return stored, lookups + [k.upper() for k in lookups] + [7]


def _reference():
    class Env(dict):
        def __missing__(self, key):
            if not isinstance(key, str) or key == key.upper():
                raise KeyError(key)
            return self[key.upper()]

        def get(self, key, default=None):
            try:
                return self[key]
            except KeyError:
                return default

        def __contains__(self, key):
            return key in self.keys() or (isinstance(key, str) and key.upper() in self.keys())

    return Env


def _lookup(env, key):
    try:
        return env[key]
    except KeyError as e:
        return ("KeyError", e.args)


def test_solve():
    r = rng()
    env_cls, want_cls = solve(), _reference()

    for _ in range(8):
        stored, lookups = _gen(r)
        mine, theirs = env_cls(stored), want_cls(stored)
        for key in lookups:
            assert _lookup(mine, key) == _lookup(theirs, key), f"{key!r} in {stored}"
            assert mine.get(key, "-") == theirs.get(key, "-"), f".get({key!r}) in {stored}"
            assert (key in mine) == (key in theirs), f"{key!r} in {stored} (membership)"

    settings = env_cls({"DB_HOST": "db.internal", "log_level": "debug"})
    assert settings["DB_HOST"] == "db.internal", "an exact upper-case key"
    assert settings["db_host"] == "db.internal", "a lower-case key gets a second chance"
    # normalising inside __getitem__ turns this hit into a lookup for LOG_LEVEL, and a KeyError
    assert settings["log_level"] == "debug", "an exact match must never be normalised away"
    with pytest.raises(KeyError):
        settings["LOG_LEVEL"]
    with pytest.raises(KeyError):
        settings[7]

    assert settings.get("db_host") == "db.internal" and settings.get("nope", "") == ""
    assert "db_host" in settings and "log_level" in settings and "nope" not in settings
    assert dict(settings) == {"DB_HOST": "db.internal", "log_level": "debug"}, "storage is untouched"

    assert issubclass(env_cls, dict), "Env must subclass dict"
    assert "__missing__" in vars(env_cls), "the second chance belongs in __missing__"
    assert "__getitem__" not in vars(env_cls), "__getitem__ would intercept hits as well as misses"
