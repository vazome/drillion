def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from typing import Protocol, runtime_checkable

from _lib import rng


def _gen(r):
    return [
        (r.random() < 0.6, round(r.uniform(1.0, 400.0), 2))
        for _ in range(r.randint(0, 7))
    ]


def _reference():
    @runtime_checkable
    class Charged(Protocol):
        def amount_due(self) -> float: ...

    def total_due(items):
        return round(sum(i.amount_due() for i in items if isinstance(i, Charged)), 2)

    return Charged, total_due


# defined out here so they are plainly nobody's subclasses
class _Subscription:
    def __init__(self, amount):
        self.amount = amount

    def amount_due(self):
        return self.amount


class _Coupon:
    def __init__(self, amount):
        self.code = f"SAVE{int(amount)}"


def _build(spec):
    return [(_Subscription if chargeable else _Coupon)(amount) for chargeable, amount in spec]


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    assert len(got) == 2, "return them as (Charged, total_due)"
    charged, total_due = got
    _, want_total = want

    for _ in range(8):
        spec = _gen(r)
        items = _build(spec)
        assert total_due(items) == want_total(items), f"total for {spec}"

    assert total_due([]) == 0.0, "an empty list totals 0.0"
    assert total_due(_build([(False, 9.0), (False, 3.0)])) == 0.0, "nothing chargeable totals 0.0"

    # an abstract base class would say False here, and the invoice would come out short
    assert isinstance(_Subscription(1.0), charged), "anything with amount_due() is Charged"
    assert not isinstance(_Coupon(1.0), charged), "a coupon has no amount_due() and is not Charged"
    assert issubclass(_Subscription, charged), "the class itself qualifies too"
    assert not issubclass(_Coupon, charged)

    assert getattr(charged, "_is_protocol", False), "Charged must be a typing.Protocol"
    assert Protocol in charged.__mro__, "Charged must subclass Protocol, not object"
