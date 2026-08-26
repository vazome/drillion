def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import inspect

from _lib import rng

_ALLERGENS = ("eggs", "peanuts", "shellfish", "strawberries", "tomatoes",
              "chocolate", "pollen", "cats")


def _gen(r):
    roll = r.random()
    if roll < 0.15:
        score = r.choice([0, 255])
    elif roll < 0.45:
        score = r.randrange(256) | r.choice([256, 512, 1024, 4096])
    else:
        score = r.randrange(256)
    return score, r.sample(_ALLERGENS, 3)


def _reference():
    class Allergies:
        _allergens = _ALLERGENS

        def __init__(self, score):
            self.score = score

        def allergic_to(self, item):
            return bool(self.score & 1 << self._allergens.index(item))

        @property
        def lst(self):
            return [item for item in self._allergens if self.allergic_to(item)]

    return Allergies


def test_solve():
    r = rng()
    Allergies = solve()
    assert inspect.isclass(Allergies), "solve() must return a class"
    Reference = _reference()
    for _ in range(6):
        score, items = _gen(r)
        mine, theirs = Allergies(score), Reference(score)
        for item in items:
            assert mine.allergic_to(item) is theirs.allergic_to(item), \
                f"Allergies({score}).allergic_to({item!r}) — and it must be a real bool"
        assert mine.lst == theirs.lst, f"Allergies({score}).lst"
        assert mine.lst == theirs.lst, f"Allergies({score}).lst must be repeatable"

    # canonical cases (exercism/python practice/allergies)
    assert Allergies(0).allergic_to("peanuts") is False
    assert Allergies(5).allergic_to("peanuts") is False
    assert Allergies(7).allergic_to("peanuts") is True
    assert Allergies(255).allergic_to("cats") is True
    assert Allergies(64).allergic_to("cats") is False
    assert Allergies(0).lst == []
    assert Allergies(1).lst == ["eggs"]
    assert Allergies(248).lst == ["strawberries", "tomatoes", "chocolate", "pollen", "cats"]
    assert Allergies(255).lst == list(_ALLERGENS)
    assert Allergies(509).lst == ["eggs", "shellfish", "strawberries", "tomatoes",
                                  "chocolate", "pollen", "cats"]
    assert Allergies(257).lst == ["eggs"]
