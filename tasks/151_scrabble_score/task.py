def solve(word: str):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_GROUPS = {1: "AEIOULNRST", 2: "DG", 3: "BCMP", 4: "FHVWY", 5: "K", 8: "JX", 10: "QZ"}
_POINTS = {letter.lower(): points
           for points, letters in _GROUPS.items()
           for letter in letters}

_WORDS = ["cabbage", "quirky", "street", "pinata", "zoo", "at", "jazz", "kayak",
          "oxyphenbutazone", "wax", "queue", "fizzbuzz", "deploy", "rollback",
          "kubernetes", "python", "a", "f", ""]


def _gen(r):
    if r.random() < 0.35:
        word = "".join(r.choice("abcdefghijklmnopqrstuvwxyz")
                       for _ in range(r.randint(0, 14)))
    else:
        word = r.choice(_WORDS)
    roll = r.random()
    if roll < 0.2:
        word = word.upper()
    elif roll < 0.4:
        word = "".join(char.upper() if r.random() < 0.5 else char for char in word)
    return word


def _reference(word):
    return sum(_POINTS[letter] for letter in word.lower())


def test_solve():
    r = rng()
    for _ in range(6):
        word = _gen(r)
        assert solve(word) == _reference(word), f"word {word!r}"

    # canonical cases (exercism/python practice/scrabble-score)
    assert solve("a") == 1
    assert solve("A") == 1
    assert solve("f") == 4
    assert solve("at") == 2
    assert solve("zoo") == 12
    assert solve("street") == 6
    assert solve("quirky") == 22
    assert solve("OxyphenButazone") == 41
    assert solve("pinata") == 8
    assert solve("") == 0
    assert solve("abcdefghijklmnopqrstuvwxyz") == 87
