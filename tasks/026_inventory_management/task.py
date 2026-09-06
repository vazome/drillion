def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from copy import deepcopy

from _lib import rng

_ITEMS = ["coal", "wood", "iron", "diamond", "gold", "silver", "copper",
          "emerald", "quartz", "obsidian"]


def _gen(r):
    inventory = {item: r.randint(0, 12)
                 for item in r.sample(_ITEMS, r.randint(1, 6))}
    if r.random() < 0.7:
        item = r.choice(list(inventory))
    else:
        item = r.choice(_ITEMS)
    return inventory, item


def _reference():
    def remove_item(inventory, item):
        if item in inventory:
            inventory.pop(item)
        return inventory

    def list_inventory(inventory):
        return [pair for pair in sorted(inventory.items()) if pair[1] > 0]

    return {"remove_item": remove_item, "list_inventory": list_inventory}


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    for _ in range(6):
        inventory, item = _gen(r)
        assert (got["remove_item"](deepcopy(inventory), item)
                == want["remove_item"](deepcopy(inventory), item)), \
            f"remove_item({inventory!r}, {item!r})"
        assert (got["list_inventory"](deepcopy(inventory))
                == want["list_inventory"](deepcopy(inventory))), \
            f"list_inventory({inventory!r})"

    # canonical cases from exercism's dicts_test.py
    assert got["remove_item"]({"iron": 1, "diamond": 2, "gold": 1},
                              "diamond") == {"iron": 1, "gold": 1}
    assert got["remove_item"]({"iron": 1, "diamond": 2, "gold": 1}, "wood") == {
        "iron": 1, "gold": 1, "diamond": 2}
    assert got["remove_item"]({}, "wood") == {}
    assert got["list_inventory"](
        {"coal": 15, "diamond": 3, "wood": 67, "silver": 0}) == [
            ("coal", 15), ("diamond", 3), ("wood", 67)]
    assert got["list_inventory"]({"wood": 0}) == []
