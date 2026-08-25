def solve(number):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    base = r.choice([1, 2, 3, 5, 7, 15, 21, 35, 105])
    return base * r.randrange(1, 40)


def _reference(number):
    sounds = "".join(word for factor, word in ((3, "Pling"), (5, "Plang"), (7, "Plong"))
                     if number % factor == 0)
    return sounds or str(number)


def test_solve():
    r = rng()
    for _ in range(6):
        number = _gen(r)
        assert solve(number) == _reference(number), f"number {number}"

    # canonical cases (exercism/python practice/raindrops)
    assert solve(1) == "1"
    assert solve(3) == "Pling"
    assert solve(15) == "PlingPlang"
    assert solve(21) == "PlingPlong"
    assert solve(52) == "52"
    assert solve(105) == "PlingPlangPlong"
