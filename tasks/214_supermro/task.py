import collections


def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    name = r.choice(["checkout_v2", "dark_mode", "new_pricing", "fast_search", "beta_upload"])
    return " " * r.randint(0, 2) + (name.upper() if r.random() < 0.5 else name) + " " * r.randint(0, 2)


def _reference():
    def _trim(key):
        return key.strip() if isinstance(key, str) else key

    def _upper(key):
        return key.upper() if isinstance(key, str) else key

    class Trimmed:
        def __setitem__(self, key, item):
            super().__setitem__(_trim(key), item)

        def __getitem__(self, key):
            return super().__getitem__(_trim(key))

        def __contains__(self, key):
            return super().__contains__(_trim(key))

    class Upper:
        def __setitem__(self, key, item):
            super().__setitem__(_upper(key), item)

        def __getitem__(self, key):
            return super().__getitem__(_upper(key))

        def __contains__(self, key):
            return super().__contains__(_upper(key))

    class Registry(Trimmed, Upper, collections.UserDict):
        pass

    return Trimmed, Upper, Registry


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    assert len(got) == 3, "return the three classes as (Trimmed, Upper, Registry)"
    trimmed, upper, registry = got
    _, _, want_registry = want

    for _ in range(6):
        keys = [_gen(r) for _ in range(4)]
        mine, theirs = registry(), want_registry()
        for i, key in enumerate(keys):
            mine[key] = i
            theirs[key] = i
        assert list(mine) == list(theirs), f"stored keys for {keys}"
        for key in keys:
            assert mine[key] == theirs[key], f"lookup of {key!r}"
            assert (key in mine) == (key in theirs), f"membership of {key!r}"

    flags = registry()
    flags["  checkout_v2 "] = True
    assert list(flags) == ["CHECKOUT_V2"], "both mixins get a turn on the way in"
    assert flags["checkout_v2"] is True and flags[" CHECKOUT_V2"] is True
    assert " checkout_v2 " in flags and "CHECKOUT_V2" in flags
    assert flags.get("checkout_v2") is True, ".get must agree with []"
    flags[7] = "numbered"
    assert flags[7] == "numbered", "a non-string key passes through both mixins untouched"

    assert registry.__mro__[:3] == (registry, trimmed, upper), "Registry(Trimmed, Upper, UserDict)"
    assert not vars(registry).get("__setitem__"), "Registry's body is empty; the mixins do the work"
    assert not issubclass(trimmed, collections.UserDict), "a mixin is mixed in, not derived"
    assert not issubclass(upper, collections.UserDict), "a mixin is mixed in, not derived"

    # naming UserDict directly instead of super() works here and breaks above
    class OnlyUpper(upper, collections.UserDict):
        pass

    only = OnlyUpper()
    only["  dark_mode "] = 1
    assert list(only) == ["  DARK_MODE "], "Upper alone must upper-case and nothing else"

    class OnlyTrimmed(trimmed, collections.UserDict):
        pass

    only = OnlyTrimmed()
    only["  dark_mode "] = 1
    assert list(only) == ["dark_mode"], "Trimmed alone must trim and nothing else"
