def solve(phrase):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    pool = ["lumberjacks", "background", "downstream", "subdermatoglyphic", "isograms",
            "eleven", "accentor", "angola", "alphabet", "thumbscrew-japingly", "zzyzx",
            "thumbscrew-jappingly", "six-year-old", "up-to-date", "emily jung schwartzkopf", ""]
    word = r.choice(pool)
    if r.random() < 0.5:
        word = "".join(c.upper() if r.random() < 0.3 else c for c in word)
    if r.random() < 0.25:
        word = f"{word} {r.randrange(100)}"
    return word


def _reference(phrase):
    letters = [char.lower() for char in phrase if char.isalpha()]
    return len(set(letters)) == len(letters)


def test_solve():
    r = rng()
    for _ in range(6):
        phrase = _gen(r)
        assert solve(phrase) == _reference(phrase), f"phrase {phrase!r}"

    # canonical cases (exercism/python practice/isogram)
    assert solve("") is True
    assert solve("isogram") is True
    assert solve("eleven") is False
    assert solve("subdermatoglyphic") is True
    assert solve("Alphabet") is False
    assert solve("six-year-old") is True
