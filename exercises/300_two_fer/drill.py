def solve(name="you"):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    first = ["Alice", "Bohdan", "Zaphod", "Do-yun", "Mei", "Olamide", "Ingrid", "Rafa"]
    last = ["Ngo", "Ferrer", "O'Neill", "Adeyemi", "Kowalski"]
    name = r.choice(first)
    if r.random() < 0.4:
        name = f"{name} {r.choice(last)}"
    return name


def _reference(name="you"):
    return f"One for {name}, one for me."


def test_solve():
    r = rng()
    for _ in range(5):
        name = _gen(r)
        assert solve(name) == _reference(name), f"name {name!r}"

    # canonical cases (exercism/python practice/two-fer)
    assert solve() == "One for you, one for me."
    assert solve("Alice") == "One for Alice, one for me."
    assert solve("Bob") == "One for Bob, one for me."
