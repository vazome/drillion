def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    wagon_ids = tuple(r.sample(range(2, 40), r.randint(0, 9)))
    train = [r.randint(2, 30), r.randint(2, 30), 1]
    train += r.sample(range(2, 40), r.randint(0, 10))
    missing = r.sample(range(2, 40), r.randint(0, 7))
    return wagon_ids, train, missing


def _reference():
    def get_list_of_wagons(*args):
        return list(args)

    def fix_list_of_wagons(each_wagons_id, missing_wagons):
        first, second, locomotive, *rest = each_wagons_id
        return [locomotive, *missing_wagons, *rest, first, second]

    return {"get_list_of_wagons": get_list_of_wagons,
            "fix_list_of_wagons": fix_list_of_wagons}


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    for _ in range(6):
        wagon_ids, train, missing = _gen(r)
        assert (got["get_list_of_wagons"](*wagon_ids)
                == want["get_list_of_wagons"](*wagon_ids)), \
            f"get_list_of_wagons{wagon_ids!r}"
        assert (got["fix_list_of_wagons"](list(train), list(missing))
                == want["fix_list_of_wagons"](list(train), list(missing))), \
            f"fix_list_of_wagons({train!r}, {missing!r})"

    # canonical cases from exercism's locomotive_engineer_test.py
    assert got["get_list_of_wagons"](1, 5, 2, 7, 4) == [1, 5, 2, 7, 4]
    assert got["get_list_of_wagons"](1) == [1]
    assert got["get_list_of_wagons"](
        1, 10, 6, 3, 9, 8, 4, 14, 24, 7) == [1, 10, 6, 3, 9, 8, 4, 14, 24, 7]
    assert got["fix_list_of_wagons"](
        [2, 5, 1, 7, 4, 12, 6, 3, 13],
        [3, 17, 6, 15]) == [1, 3, 17, 6, 15, 7, 4, 12, 6, 3, 13, 2, 5]
    assert got["fix_list_of_wagons"]([4, 2, 1], [8, 6, 15]) == [1, 8, 6, 15, 4, 2]
    assert got["fix_list_of_wagons"](
        [3, 14, 1, 25, 7, 19, 10],
        [8, 6, 4, 5, 9, 21, 2, 13]) == [1, 8, 6, 4, 5, 9, 21, 2, 13,
                                        25, 7, 19, 10, 3, 14]
