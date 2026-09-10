def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import pytest
from _lib import rng


def _gen(r):
    return (
        r.choice(["oak plank", "brass hinge", "steel bolt", "pine batten", "copper pipe"]),
        r.randint(1, 40),
        round(r.uniform(0.5, 90.0), 2),
    )


def _reference():
    class Quantity:
        def __set_name__(self, owner, name):
            self._name = name

        def __get__(self, instance, owner=None):
            if instance is None:
                return self
            return instance.__dict__[self._name]

        def __set__(self, instance, value):
            if value <= 0:
                raise ValueError(f"{self._name} must be > 0")
            instance.__dict__[self._name] = value

    class LineItem:
        weight = Quantity()
        price = Quantity()

        def __init__(self, description, weight, price):
            self.description = description
            self.weight = weight
            self.price = price

        def subtotal(self):
            return self.weight * self.price

    return Quantity, LineItem


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    assert len(got) == 2, "return the two classes as (Quantity, LineItem)"
    quantity, line_item = got
    _, want_item = want

    for _ in range(6):
        description, weight, price = _gen(r)
        mine, theirs = line_item(description, weight, price), want_item(description, weight, price)
        assert mine.subtotal() == theirs.subtotal(), f"subtotal for {(description, weight, price)}"
        assert mine.weight == weight and mine.price == price
        assert mine.description == description

    # the two attributes have to be the same descriptor, not two hand-written properties
    assert isinstance(vars(line_item).get("weight"), quantity), "weight must be a Quantity()"
    assert isinstance(vars(line_item).get("price"), quantity), "price must be a Quantity()"
    assert vars(line_item)["weight"] is not vars(line_item)["price"], "one instance per attribute"

    # `__set_name__` is what tells the two apart; a hard-coded storage name collides
    item = line_item("bolt", 3, 7.5)
    item.weight = 9
    assert item.price == 7.5, "setting weight must not disturb price"

    for bad in (0, -1):
        with pytest.raises(ValueError):
            line_item("bolt", bad, 7.5)
        with pytest.raises(ValueError):
            line_item("bolt", 3, bad)
    with pytest.raises(ValueError):
        item.weight = -2
