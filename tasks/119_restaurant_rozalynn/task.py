def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_NAMES = ["Walter", "Frank", "Jenny", "Carol", "Alice", "George", "Mort", "Suze",
          "Phillip", "Tony", "Rozalynn", "Bethany", "Eric", "Gloria", "Bob"]


def _gen(r):
    size = r.randint(1, 30)
    if r.random() < 0.25:
        guests = None
    elif r.random() < 0.2:
        guests = []
    else:
        guests = r.sample(_NAMES, r.randint(1, 12))
    return size, guests


def _reference():
    def new_seating_chart(size=22):
        return {number: None for number in range(1, size + 1)}

    def arrange_reservations(guests=None):
        seats = new_seating_chart()
        if guests:
            for index, guest in enumerate(guests):
                seats[index + 1] = guest
        return seats

    return {"new_seating_chart": new_seating_chart,
            "arrange_reservations": arrange_reservations}


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    for _ in range(6):
        size, guests = _gen(r)
        assert got["new_seating_chart"](size) == want["new_seating_chart"](size), (
            f"new_seating_chart({size})")
        if guests is None:
            assert got["arrange_reservations"]() == want["arrange_reservations"](), (
                "arrange_reservations() with no argument")
        else:
            assert (got["arrange_reservations"](list(guests))
                    == want["arrange_reservations"](guests)), (
                f"arrange_reservations({guests!r})")

    assert got["new_seating_chart"]() == want["new_seating_chart"](), (
        "new_seating_chart() with no argument must lay out 22 seats")

    # canonical cases from exercism's none_test.py and instructions.md
    assert got["new_seating_chart"](3) == {1: None, 2: None, 3: None}
    empty_22 = {number: None for number in range(1, 23)}
    assert got["new_seating_chart"]() == empty_22
    assert got["arrange_reservations"]() == empty_22
    assert got["arrange_reservations"]([]) == empty_22
    # the instructions' own example: the FIRST guest sits in seat 1
    assert got["arrange_reservations"](
        ["Walter", "Frank", "Jenny", "Carol", "Alice", "George"]) == {
        1: "Walter", 2: "Frank", 3: "Jenny", 4: "Carol", 5: "Alice", 6: "George",
        7: None, 8: None, 9: None, 10: None, 11: None, 12: None, 13: None, 14: None,
        15: None, 16: None, 17: None, 18: None, 19: None, 20: None, 21: None, 22: None}
