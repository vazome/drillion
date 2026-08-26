def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import inspect

from _lib import rng

_NAMES = ["Jerimiah", "Eric", "Bethany", "Byte", "SqueekyBoots", "Bob", "Adele", "Björk",
          "Rozalynn", "Ellen", "Guido", "Carol", "Alice", "George", "Frank", "Jenny",
          "Walter", "Mort", "Suze", "Phillip", "Tony"]

_FLIGHTS = ["KL1022", "DL1002", "CO1234", "HA80085", "BA17", "LX38", "AF1234"]


def _gen(r):
    letter_count = r.randint(1, 14)
    seat_count = r.choice([r.randint(1, 12), r.randint(13, 60), 4 * r.randint(1, 20)])
    passengers = r.sample(_NAMES, r.randint(0, 9))
    seat_numbers = [f"{r.randint(1, 120)}{r.choice('ABCD')}" for _ in range(r.randint(1, 5))]
    return letter_count, seat_count, passengers, seat_numbers, r.choice(_FLIGHTS)


def _reference():
    seats_in_row = ["A", "B", "C", "D"]

    def generate_seat_letters(number):
        for seat in range(number):
            yield seats_in_row[seat % 4]

    def generate_seats(number):
        letters = generate_seat_letters(number)
        row_number = 1
        for seat in range(number):
            if seat and seat % 4 == 0:
                row_number += 1
                if row_number == 13:
                    row_number = 14
            yield f"{row_number}{next(letters)}"

    def assign_seats(passengers):
        return dict(zip(passengers, generate_seats(len(passengers))))

    def generate_codes(seat_numbers, flight_id):
        for seat in seat_numbers:
            base = f"{seat}{flight_id}"
            yield base + "0" * (12 - len(base))

    return {"generate_seat_letters": generate_seat_letters,
            "generate_seats": generate_seats,
            "assign_seats": assign_seats,
            "generate_codes": generate_codes}


def test_solve():
    r = rng()
    got, want = solve(), _reference()

    for name in ("generate_seat_letters", "generate_seats"):
        assert inspect.isgenerator(got[name](5)), f"{name}() must return a generator"
    assert inspect.isgenerator(got["generate_codes"](["1A"], "KL1022")), (
        "generate_codes() must return a generator")

    for _ in range(6):
        letter_count, seat_count, passengers, seat_numbers, flight_id = _gen(r)
        assert (list(got["generate_seat_letters"](letter_count))
                == list(want["generate_seat_letters"](letter_count))), (
            f"generate_seat_letters({letter_count})")
        assert (list(got["generate_seats"](seat_count))
                == list(want["generate_seats"](seat_count))), f"generate_seats({seat_count})"
        assert (got["assign_seats"](list(passengers)) == want["assign_seats"](passengers)), (
            f"assign_seats({passengers!r})")
        assert (list(got["generate_codes"](list(seat_numbers), flight_id))
                == list(want["generate_codes"](seat_numbers, flight_id))), (
            f"generate_codes({seat_numbers!r}, {flight_id!r})")

    # canonical cases from exercism's generators_test.py
    for number, expected in [(1, ["A"]), (2, ["A", "B"]), (3, ["A", "B", "C"]),
                             (4, ["A", "B", "C", "D"]), (5, ["A", "B", "C", "D", "A"])]:
        assert list(got["generate_seat_letters"](number)) == expected, (
            f"generate_seat_letters({number})")
    for number, expected in [(1, ["1A"]), (2, ["1A", "1B"]), (3, ["1A", "1B", "1C"]),
                             (4, ["1A", "1B", "1C", "1D"]),
                             (5, ["1A", "1B", "1C", "1D", "2A"])]:
        assert list(got["generate_seats"](number)) == expected, f"generate_seats({number})"
    assert list(got["generate_seats"](14 * 4)) == [
        "1A", "1B", "1C", "1D", "2A", "2B", "2C", "2D", "3A", "3B", "3C", "3D",
        "4A", "4B", "4C", "4D", "5A", "5B", "5C", "5D", "6A", "6B", "6C", "6D",
        "7A", "7B", "7C", "7D", "8A", "8B", "8C", "8D", "9A", "9B", "9C", "9D",
        "10A", "10B", "10C", "10D", "11A", "11B", "11C", "11D", "12A", "12B", "12C", "12D",
        "14A", "14B", "14C", "14D", "15A", "15B", "15C", "15D"], "row 13 must be skipped"

    assert got["assign_seats"](["Passenger1", "Passenger2", "Passenger3",
                                "Passenger4", "Passenger5"]) == {
        "Passenger1": "1A", "Passenger2": "1B", "Passenger3": "1C",
        "Passenger4": "1D", "Passenger5": "2A"}
    assert got["assign_seats"]([]) == {}

    assert list(got["generate_codes"](["12A", "38B", "69C", "102B"], "KL1022")) == [
        "12AKL1022000", "38BKL1022000", "69CKL1022000", "102BKL102200"]
    assert list(got["generate_codes"](["22C", "88B", "33A", "44B"], "DL1002")) == [
        "22CDL1002000", "88BDL1002000", "33ADL1002000", "44BDL1002000"]
