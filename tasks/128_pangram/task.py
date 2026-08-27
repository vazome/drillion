def solve(sentence: str):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from string import ascii_lowercase

from _lib import rng


def _gen(r):
    base = r.choice(["the quick brown fox jumps over the lazy dog",
                     "pack my box with five dozen liquor jugs",
                     "five quacking zephyrs jolt my wax bed",
                     "how vexingly quick daft zebras jump",
                     "a quick movement of the enemy will jeopardize five gunboats"])
    if r.random() < 0.5:                       # knock a letter out, or replace it with a digit
        base = base.replace(r.choice(ascii_lowercase), r.choice(["", "3", "_", "7"]))
    if r.random() < 0.4:
        base = base.replace(" ", r.choice(["_", "  "]))
    if r.random() < 0.4:
        base = "".join(c.upper() if r.random() < 0.3 else c for c in base)
    if r.random() < 0.3:
        base = f'"{base}." {r.randrange(10)}'
    return base


def _reference(sentence):
    return set(ascii_lowercase) <= set(sentence.lower())


def test_solve():
    r = rng()
    for _ in range(6):
        sentence = _gen(r)
        assert solve(sentence) == _reference(sentence), f"sentence {sentence!r}"

    # canonical cases (exercism/python practice/pangram)
    assert solve("") is False
    assert solve("abcdefghijklmnopqrstuvwxyz") is True
    assert solve("the quick brown fox jumps over the lazy dog") is True
    assert solve("five boxing wizards jump quickly at it") is False
    assert solve('"Five quacking Zephyrs jolt my wax bed."') is True
    assert solve("abcdefghijklm ABCDEFGHIJKLM") is False
