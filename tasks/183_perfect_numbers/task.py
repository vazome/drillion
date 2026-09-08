def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from enum import Enum

from _lib import rng

_NAMES = ("PERFECT", "ABUNDANT", "DEFICIENT")


def _gen(r):
    """A mix of the three kinds: perfects are rare, so they are drawn on purpose."""
    return r.choice(
        [r.choice([6, 28, 496, 8128]), r.randint(1, 40), r.randint(41, 400)]
    )


def _reference():
    class Kind(Enum):
        PERFECT = "perfect"
        ABUNDANT = "abundant"
        DEFICIENT = "deficient"

        @classmethod
        def of(cls, n):
            total = sum(d for d in range(1, n) if n % d == 0)
            if total == n:
                return cls.PERFECT
            return cls.ABUNDANT if total > n else cls.DEFICIENT

    return Kind


def test_solve():
    r = rng()
    mine, reference = solve(), _reference()

    assert issubclass(mine, Enum), "solve() must return an Enum class"
    assert [m.name for m in mine] == list(_NAMES), (
        f"Kind must hold {_NAMES} in that order, got {[m.name for m in mine]}"
    )
    assert [m.value for m in mine] == [m.value for m in reference], (
        "the member values must be the lowercase words"
    )

    for n in [1, 2, 6, 12, 13, 28, 496, *(_gen(r) for _ in range(40))]:
        got, want = mine.of(n), reference.of(n)
        assert got.name == want.name, f"Kind.of({n}) is {want.name}, got {got.name}"
        assert isinstance(got, mine), f"Kind.of({n}) must return a member of Kind"
