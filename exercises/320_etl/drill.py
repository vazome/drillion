def solve(legacy_data):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_SCORES = [1, 2, 3, 4, 5, 6, 8, 10, 12, 20]


def _gen(r):
    letters = list(_ALPHABET)
    r.shuffle(letters)
    legacy_data = {}
    taken = 0
    for score in sorted(r.sample(_SCORES, r.randint(1, 6))):
        size = r.randint(1, 5)
        group = letters[taken:taken + size]
        taken += size
        if group:
            legacy_data[score] = group
    return legacy_data


def _reference(legacy_data):
    return {letter.lower(): points
            for points, letters in legacy_data.items()
            for letter in letters}


def test_solve():
    r = rng()
    for _ in range(6):
        legacy_data = _gen(r)
        assert solve(legacy_data) == _reference(legacy_data), f"legacy_data {legacy_data!r}"

    # canonical cases (exercism/python practice/etl)
    assert solve({1: ["A"]}) == {"a": 1}
    assert solve({1: ["A", "E", "I", "O", "U"]}) == {"a": 1, "e": 1, "i": 1, "o": 1, "u": 1}
    assert solve({1: ["A", "E"], 2: ["D", "G"]}) == {"a": 1, "d": 2, "e": 1, "g": 2}
    assert solve({1: ["A", "E", "I", "O", "U", "L", "N", "R", "S", "T"],
                  2: ["D", "G"], 3: ["B", "C", "M", "P"], 4: ["F", "H", "V", "W", "Y"],
                  5: ["K"], 8: ["J", "X"], 10: ["Q", "Z"]}) == {
        "a": 1, "b": 3, "c": 3, "d": 2, "e": 1, "f": 4, "g": 2, "h": 4, "i": 1,
        "j": 8, "k": 5, "l": 1, "m": 3, "n": 1, "o": 1, "p": 3, "q": 10, "r": 1,
        "s": 1, "t": 1, "u": 1, "v": 4, "w": 4, "x": 8, "y": 4, "z": 10}

    original = {1: ["A", "E"], 2: ["D"]}
    solve(original)
    assert original == {1: ["A", "E"], 2: ["D"]}, "legacy_data must not be modified"
