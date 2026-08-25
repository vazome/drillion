def solve(text):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    pool = ["robot", "Ramen", "racecar", "drawer", "stressed", "strops", "子猫",
            "I'm hungry!", "påsklilja", "", "ops on call", "déjà vu", "42 nodes down"]
    text = r.choice(pool)
    if r.random() < 0.4:
        text = " ".join(r.sample(pool, r.randint(2, 3)))
    return text


def _reference(text):
    return text[::-1]


def test_solve():
    r = rng()
    for _ in range(6):
        text = _gen(r)
        assert solve(text) == _reference(text), f"text {text!r}"

    # canonical cases (exercism/python practice/reverse-string)
    assert solve("") == ""
    assert solve("robot") == "tobor"
    assert solve("Ramen") == "nemaR"
    assert solve("I'm hungry!") == "!yrgnuh m'I"
    assert solve("drawer") == "reward"
    assert solve("子猫") == "猫子"
