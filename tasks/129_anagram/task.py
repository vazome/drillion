def solve(word: str, candidates: list[str]):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    families = [("listen", ["silent", "enlist", "tinsel", "inlets"]),
                ("stone", ["tones", "notes", "seton"]),
                ("allergy", ["gallery", "regally", "largely"]),
                ("solemn", ["lemons", "melons"]),
                ("orchestra", ["carthorse"]),
                ("nose", ["eons", "ones"])]
    distractors = ["banana", "google", "cherry", "radishes", "dog", "goody", "patter",
                   "last", "mass", "clergy", "leading", "cashregister", "zombies"]
    word, mates = r.choice(families)
    picked = (r.sample(mates, r.randint(1, len(mates)))
              + r.sample(distractors, r.randint(1, 3))
              + [word])
    cased = [w.upper() if r.random() < 0.3 else w.capitalize() if r.random() < 0.3 else w
             for w in picked]
    r.shuffle(cased)
    return (word.upper() if r.random() < 0.5 else word), cased


def _reference(word, candidates):
    target = word.lower()
    letters = sorted(target)
    return [candidate for candidate in candidates
            if candidate.lower() != target and sorted(candidate.lower()) == letters]


def test_solve():
    r = rng()
    for _ in range(5):
        word, candidates = _gen(r)
        assert solve(word, list(candidates)) == _reference(word, candidates), f"word {word}"

    # canonical cases (exercism/python practice/anagram)
    assert solve("diaper", ["hello", "world", "zombies", "pants"]) == []
    assert solve("solemn", ["lemons", "cherry", "melons"]) == ["lemons", "melons"]
    assert solve("listen", ["enlists", "google", "inlets", "banana"]) == ["inlets"]
    assert solve("good", ["dog", "goody"]) == []
    assert solve("nose", ["Eons", "ONES"]) == ["Eons", "ONES"]
    assert solve("BANANA", ["Banana"]) == []
