def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_NAMES = ["Walter", "Frank", "Jenny", "Carol", "Alice", "George", "Mort", "Suze",
          "Phillip", "Tony", "Rozalynn", "Bethany", "Eric", "Gloria", "Bob"]


def _gen(r):
    size = r.randint(3, 22)
    names = r.sample(_NAMES, min(len(_NAMES), size))
    chart = {}
    for seat in range(1, size + 1):
        chart[seat] = None if r.random() < 0.5 else names[(seat - 1) % len(names)]
    free = sum(1 for guest in chart.values() if guest is None)
    walk_ins = r.sample(_NAMES, min(len(_NAMES), max(0, free + r.randint(-2, 2))))
    to_free = r.sample(sorted(chart), r.randint(0, min(4, size)))
    return chart, walk_ins, to_free


def _reference():
    def accommodate_waiting_guests(seats, guests):
        available = [number for number, guest in seats.items() if guest is None]
        if len(guests) <= len(available):
            for index, guest in enumerate(guests):
                seats[available[index]] = guest
        return seats

    def empty_seats(seats, seat_numbers):
        for seat in seat_numbers:
            seats[seat] = None
        return seats

    return {"accommodate_waiting_guests": accommodate_waiting_guests,
            "empty_seats": empty_seats}


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    for _ in range(6):
        chart, walk_ins, to_free = _gen(r)
        seated = got["accommodate_waiting_guests"](dict(chart), list(walk_ins))
        assert seated == want["accommodate_waiting_guests"](dict(chart), walk_ins), (
            f"accommodate_waiting_guests({chart!r}, {walk_ins!r}) -> {seated!r}")
        cleared = got["empty_seats"](dict(chart), list(to_free))
        assert cleared == want["empty_seats"](dict(chart), to_free), (
            f"empty_seats({chart!r}, {to_free!r}) -> {cleared!r}")

    # canonical cases from exercism's none_test.py
    full = {1: "Carol", 2: "Alice", 3: "George", 4: None, 5: None, 6: None,
            7: "Frank", 8: "Walter"}
    assert got["accommodate_waiting_guests"](
        dict(full), ["Mort", "Suze", "Phillip", "Tony"]) == full, (
        "four guests do not fit into three empty seats — the chart must come back unchanged")

    roomy = {1: None, 2: None, 3: None, 4: "Carol", 5: "Alice", 6: "George", 7: None,
             8: None, 9: None, 10: None, 11: None, 12: None, 13: None, 14: None,
             15: None, 16: None, 17: None, 18: "Frank", 19: "Jenny", 20: None,
             21: None, 22: "Walter"}
    assert got["accommodate_waiting_guests"](
        dict(roomy), ["Mort", "Suze", "Phillip", "Tony"]) == {
        1: "Mort", 2: "Suze", 3: "Phillip", 4: "Carol", 5: "Alice", 6: "George",
        7: "Tony", 8: None, 9: None, 10: None, 11: None, 12: None, 13: None, 14: None,
        15: None, 16: None, 17: None, 18: "Frank", 19: "Jenny", 20: None, 21: None,
        22: "Walter"}

    tables = {1: "Alice", 2: None, 3: "Bob", 4: "George", 5: "Gloria"}
    assert got["empty_seats"](dict(tables), [5, 3, 1]) == {
        1: None, 2: None, 3: None, 4: "George", 5: None}
    assert got["empty_seats"](dict(tables), []) == tables
