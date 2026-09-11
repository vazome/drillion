def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import pytest
from _lib import rng


def _gen(r):
    return (
        r.choice(["billing", "search", "auth", "ingest", "mailer"]),
        r.choice([400, 404, 429, 500, 502, 503]),
    )


def _reference():
    class AlertKey:
        def __init__(self, service, code):
            self.__service = service
            self.__code = code

        @property
        def service(self):
            return self.__service

        @property
        def code(self):
            return self.__code

        def __eq__(self, other):
            if isinstance(other, AlertKey):
                return (self.service, self.code) == (other.service, other.code)
            return NotImplemented

        def __hash__(self):
            return hash((self.service, self.code))

        def __repr__(self):
            return f"AlertKey({self.service!r}, {self.code!r})"

    return AlertKey


def test_solve():
    r = rng()
    key, want = solve(), _reference()

    drawn = [_gen(r) for _ in range(12)]
    for service, code in drawn:
        mine, theirs = key(service, code), want(service, code)
        assert (mine.service, mine.code) == (theirs.service, theirs.code), f"fields for {service}"
        assert repr(mine) == repr(theirs), f"repr for {(service, code)}"

    # defining __eq__ alone withdraws hashing, so a set of these raises rather than dedupes
    twins = [key(*pair) for pair in drawn] + [key(*pair) for pair in drawn]
    assert len(set(twins)) == len(set(drawn)), "equal keys must collapse to one set entry"
    assert len({key(*p): p for p in drawn + drawn}) == len(set(drawn)), "and to one dict entry"

    a, b = key("billing", 503), key("billing", 503)
    assert a == b and a is not b, "two separately built keys with the same fields are equal"
    assert hash(a) == hash(b), "equal keys must hash the same"
    assert {a: "paged"}[b] == "paged", "an equal key must find the entry"
    assert a != key("search", 503) and a != key("billing", 500), "either field apart is not equal"

    # a hash that can move after filing is a key that can never be found again
    for field, value in (("service", "search"), ("code", 500)):
        with pytest.raises(AttributeError):
            setattr(a, field, value)

    assert a.__eq__("billing") is NotImplemented, "__eq__ declines foreign types"
    assert (a == "billing") is False, "comparing to a string is False, not an error"
