def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    unit = r.choice([1, 1, 1, 0.5])
    roll = r.random()
    if roll < 0.20:
        side = r.randint(0, 10) * unit
        sides = [side, side, side]
    elif roll < 0.55:
        pair = r.randint(1, 10) * unit
        other = r.randint(0, 20) * unit
        sides = [pair, pair, other]
    else:
        sides = [r.randint(0, 12) * unit for _ in range(3)]
    r.shuffle(sides)
    return sides


def _reference():
    def valid(sides):
        ordered = sorted(sides)
        return ordered[0] > 0 and ordered[0] + ordered[1] >= ordered[2]

    def equilateral(sides):
        return valid(sides) and len(set(sides)) == 1

    def isosceles(sides):
        return valid(sides) and len(set(sides)) < 3

    def scalene(sides):
        return valid(sides) and len(set(sides)) == 3

    return {"equilateral": equilateral, "isosceles": isosceles, "scalene": scalene}


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    for _ in range(6):
        sides = _gen(r)
        for name in ("equilateral", "isosceles", "scalene"):
            assert got[name](list(sides)) is want[name](list(sides)), f"{name} {sides!r}"

    # canonical cases (exercism/python practice/triangle)
    for sides, expected in [([2, 2, 2], True), ([2, 3, 2], False), ([5, 4, 6], False),
                            ([0, 0, 0], False), ([0.5, 0.5, 0.5], True)]:
        assert got["equilateral"](sides) is expected, f"equilateral {sides!r}"
    for sides, expected in [([3, 4, 4], True), ([4, 4, 3], True), ([4, 3, 4], True),
                            ([4, 4, 4], True), ([2, 3, 4], False), ([1, 1, 3], False),
                            ([1, 3, 1], False), ([3, 1, 1], False), ([0.5, 0.4, 0.5], True)]:
        assert got["isosceles"](sides) is expected, f"isosceles {sides!r}"
    for sides, expected in [([5, 4, 6], True), ([4, 4, 4], False), ([4, 4, 3], False),
                            ([3, 4, 3], False), ([4, 3, 3], False), ([7, 3, 2], False),
                            ([0.5, 0.4, 0.6], True)]:
        assert got["scalene"](sides) is expected, f"scalene {sides!r}"
