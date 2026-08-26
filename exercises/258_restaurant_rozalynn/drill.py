def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_NAMES = ["Walter", "Frank", "Jenny", "Carol", "Alice", "George", "Mort", "Suze",
          "Phillip", "Tony", "Rozalynn", "Bethany", "Eric", "Gloria", "Bob", "Occupied"]

# values that are falsy but NOT None: a truthiness test would call these seats empty
_FALSY = [0, ""]


def _gen(r):
    size = r.randint(1, 24)
    chart = {}
    for seat in range(1, size + 1):
        roll = r.random()
        if roll < 0.45:
            chart[seat] = None
        elif roll < 0.9:
            chart[seat] = r.choice(_NAMES)
        else:
            chart[seat] = r.choice(_FALSY)
    return chart


def _reference():
    def find_all_available_seats(seats):
        available = []
        for seat_number, guest in seats.items():
            if guest is None:
                available.append(seat_number)
        return available

    def current_empty_seat_capacity(seats):
        count = 0
        for guest in seats.values():
            if guest is None:
                count += 1
        return count

    return {"find_all_available_seats": find_all_available_seats,
            "current_empty_seat_capacity": current_empty_seat_capacity}


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    for _ in range(6):
        chart = _gen(r)
        free = got["find_all_available_seats"](dict(chart))
        assert isinstance(free, list), f"find_all_available_seats must return a list, got {type(free)}"
        assert free == want["find_all_available_seats"](chart), (
            f"find_all_available_seats({chart!r}) -> {free!r}")
        capacity = got["current_empty_seat_capacity"](dict(chart))
        assert isinstance(capacity, int), (
            f"current_empty_seat_capacity must return an int, got {type(capacity)}")
        assert capacity == want["current_empty_seat_capacity"](chart), (
            f"current_empty_seat_capacity({chart!r}) -> {capacity!r}")

    # canonical cases from exercism's none_test.py
    assert got["find_all_available_seats"](
        {1: None, 2: "Frank", 3: "Jenny", 4: None, 5: "Alice", 6: "George", 7: None,
         8: "Carol", 9: None, 10: None, 11: None, 12: "Walter"}) == [1, 4, 7, 9, 10, 11]
    assert got["find_all_available_seats"](
        {1: None, 2: None, 3: None, 4: None, 5: "Alice", 6: None, 7: None, 8: None,
         9: None, 10: None, 11: None, 12: None}) == [1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12]
    assert got["current_empty_seat_capacity"](
        {1: "Occupied", 2: None, 3: "Occupied"}) == 1
    assert got["current_empty_seat_capacity"](
        {1: "Occupied", 2: "Occupied", 3: None, 4: "Occupied", 5: None}) == 2
    assert got["current_empty_seat_capacity"]({1: "Alice"}) == 0
