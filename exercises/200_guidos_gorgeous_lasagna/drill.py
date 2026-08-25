def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    return r.randint(0, 40), r.randint(1, 25)


def _reference():
    EXPECTED_BAKE_TIME = 40
    PREPARATION_TIME = 2

    def bake_time_remaining(elapsed_bake_time):
        return EXPECTED_BAKE_TIME - elapsed_bake_time

    def preparation_time_in_minutes(number_of_layers):
        return number_of_layers * PREPARATION_TIME

    def elapsed_time_in_minutes(number_of_layers, elapsed_bake_time):
        return preparation_time_in_minutes(number_of_layers) + elapsed_bake_time

    return {"EXPECTED_BAKE_TIME": EXPECTED_BAKE_TIME,
            "bake_time_remaining": bake_time_remaining,
            "preparation_time_in_minutes": preparation_time_in_minutes,
            "elapsed_time_in_minutes": elapsed_time_in_minutes}


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    assert got["EXPECTED_BAKE_TIME"] == want["EXPECTED_BAKE_TIME"]
    for _ in range(5):
        elapsed, layers = _gen(r)
        assert got["bake_time_remaining"](elapsed) == want["bake_time_remaining"](elapsed)
        assert (got["preparation_time_in_minutes"](layers)
                == want["preparation_time_in_minutes"](layers))
        assert (got["elapsed_time_in_minutes"](layers, elapsed)
                == want["elapsed_time_in_minutes"](layers, elapsed))

    # canonical cases from exercism's lasagna_test.py + instructions.md
    assert got["EXPECTED_BAKE_TIME"] == 40
    for elapsed, expected in [(1, 39), (23, 17), (33, 7)]:
        assert got["bake_time_remaining"](elapsed) == expected
    for layers, expected in [(2, 4), (11, 22), (15, 30)]:
        assert got["preparation_time_in_minutes"](layers) == expected
    for layers, elapsed, expected in [(1, 3, 5), (3, 20, 26), (11, 15, 37)]:
        assert got["elapsed_time_in_minutes"](layers, elapsed) == expected
