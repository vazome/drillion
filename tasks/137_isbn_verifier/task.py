def solve(isbn: str):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _check_char(body):
    total = sum(int(char) * (10 - index) for index, char in enumerate(body))
    remainder = (-total) % 11
    return "X" if remainder == 10 else str(remainder)


def _gen(r):
    body = "".join(str(r.randrange(10)) for _ in range(9))
    isbn = body + (_check_char(body) if r.random() < 0.5 else str(r.randrange(10)))
    roll = r.random()
    if roll < 0.12:
        spot = r.randrange(len(isbn))
        isbn = isbn[:spot] + r.choice("APBX?") + isbn[spot + 1:]
    elif roll < 0.2:
        isbn = isbn[:r.randint(1, 9)]
    elif roll < 0.28:
        isbn += str(r.randrange(10))
    if r.random() < 0.5:
        chars = list(isbn)
        for _ in range(r.randint(1, 3)):
            chars.insert(r.randrange(1, len(chars) + 1) if len(chars) > 1 else 1, "-")
        isbn = "".join(chars)
    return isbn


def _reference(isbn):
    chars = isbn.replace("-", "")
    if len(chars) != 10:
        return False
    total = 0
    for index, char in enumerate(chars):
        if char.isdigit():
            value = int(char)
        elif char == "X" and index == 9:
            value = 10
        else:
            return False
        total += value * (10 - index)
    return total % 11 == 0


def test_solve():
    r = rng()
    for _ in range(6):
        isbn = _gen(r)
        assert solve(isbn) == _reference(isbn), f"isbn {isbn!r}"

    # canonical cases (exercism/python practice/isbn-verifier)
    assert solve("3-598-21508-8") is True
    assert solve("3-598-21508-9") is False
    assert solve("3-598-21507-X") is True
    assert solve("3-598-2X507-9") is False
    assert solve("3598215088") is True
    assert solve("359821507") is False
    assert solve("3598215078X") is False
    assert solve("") is False
