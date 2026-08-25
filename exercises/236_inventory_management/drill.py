def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from copy import deepcopy

from _lib import rng

_ITEMS = ["coal", "wood", "iron", "diamond", "gold", "silver", "copper",
          "emerald", "quartz", "obsidian"]


def _gen(r):
    inventory = {item: r.randint(0, 5)
                 for item in r.sample(_ITEMS, r.randint(0, 5))}
    items = [r.choice(_ITEMS) for _ in range(r.randint(0, 9))]
    return inventory, items


def _reference():
    def add_items(inventory, items):
        for item in items:
            inventory.setdefault(item, 0)
            inventory[item] += 1
        return inventory

    def create_inventory(items):
        return add_items({}, items)

    def decrement_items(inventory, items):
        for item in items:
            if item in inventory:
                inventory[item] = max(inventory[item] - 1, 0)
        return inventory

    return {"create_inventory": create_inventory, "add_items": add_items,
            "decrement_items": decrement_items}


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    for _ in range(6):
        inventory, items = _gen(r)
        assert (got["create_inventory"](list(items))
                == want["create_inventory"](list(items))), \
            f"create_inventory({items!r})"
        assert (got["add_items"](deepcopy(inventory), list(items))
                == want["add_items"](deepcopy(inventory), list(items))), \
            f"add_items({inventory!r}, {items!r})"
        assert (got["decrement_items"](deepcopy(inventory), list(items))
                == want["decrement_items"](deepcopy(inventory), list(items))), \
            f"decrement_items({inventory!r}, {items!r})"

    # canonical cases from exercism's dicts_test.py
    assert got["create_inventory"](
        ["wood", "iron", "iron", "diamond", "diamond"]) == {
            "wood": 1, "iron": 2, "diamond": 2}
    assert got["add_items"]({"wood": 4, "iron": 2}, ["iron", "iron"]) == {
        "wood": 4, "iron": 4}
    assert got["add_items"]({"iron": 1, "diamond": 2},
                            ["iron", "wood", "wood"]) == {
        "iron": 2, "diamond": 2, "wood": 2}
    assert got["add_items"]({}, ["iron", "iron", "diamond"]) == {
        "iron": 2, "diamond": 1}
    assert got["decrement_items"](
        {"iron": 3, "diamond": 4, "gold": 2},
        ["iron", "iron", "diamond", "gold", "gold"]) == {
            "iron": 1, "diamond": 3, "gold": 0}
    assert got["decrement_items"](
        {"wood": 2, "iron": 3, "diamond": 1},
        ["wood", "wood", "wood", "iron", "diamond", "diamond"]) == {
            "wood": 0, "iron": 2, "diamond": 0}
    assert got["decrement_items"](
        {"iron": 3, "gold": 2},
        ["iron", "wood", "iron", "diamond"]) == {"iron": 1, "gold": 2}
