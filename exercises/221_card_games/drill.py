def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    number = r.randrange(0, 900)
    rounds_1 = [r.randrange(0, 60) for _ in range(r.randint(0, 4))]
    rounds_2 = [r.randrange(0, 60) for _ in range(r.randint(0, 4))]
    rounds = sorted(r.sample(range(1, 60), r.randint(0, 6)))
    wanted = r.choice(rounds) if rounds and r.random() < 0.5 else r.randrange(0, 60)
    return number, rounds_1, rounds_2, rounds, wanted


def _reference():
    def get_rounds(number):
        return [number, number + 1, number + 2]

    def concatenate_rounds(rounds_1, rounds_2):
        return rounds_1 + rounds_2

    def list_contains_round(rounds, number):
        return number in rounds

    return {"get_rounds": get_rounds, "concatenate_rounds": concatenate_rounds,
            "list_contains_round": list_contains_round}


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    for _ in range(6):
        number, rounds_1, rounds_2, rounds, wanted = _gen(r)
        assert got["get_rounds"](number) == want["get_rounds"](number), f"get_rounds({number})"
        assert (got["concatenate_rounds"](list(rounds_1), list(rounds_2))
                == want["concatenate_rounds"](list(rounds_1), list(rounds_2))), \
            f"concatenate_rounds({rounds_1}, {rounds_2})"
        assert (got["list_contains_round"](list(rounds), wanted)
                == want["list_contains_round"](list(rounds), wanted)), \
            f"list_contains_round({rounds}, {wanted})"

    # canonical cases from exercism's lists_test.py
    assert got["get_rounds"](27) == [27, 28, 29]
    assert got["get_rounds"](0) == [0, 1, 2]
    assert got["get_rounds"](666) == [666, 667, 668]
    assert got["concatenate_rounds"]([27, 28, 29], [35, 36]) == [27, 28, 29, 35, 36]
    assert got["concatenate_rounds"]([], []) == []
    assert got["concatenate_rounds"]([0, 1], []) == [0, 1]
    assert got["concatenate_rounds"]([], [1, 2]) == [1, 2]
    assert got["list_contains_round"]([27, 28, 29, 35, 36], 29) is True
    assert got["list_contains_round"]([27, 28, 29, 35, 36], 30) is False
    assert got["list_contains_round"]([], 1) is False
    assert got["list_contains_round"]([1], 1) is True
