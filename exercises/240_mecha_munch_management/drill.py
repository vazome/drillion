def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from copy import deepcopy

from _lib import rng

_GROCERIES = ["Apple", "Banana", "Orange", "Raspberry", "Blueberries",
              "Broccoli", "Kiwi", "Melon", "Pear", "Juice", "Milk", "Yoghurt"]
_CHILLED = {"Milk", "Yoghurt", "Juice"}


def _gen(r):
    chosen = r.sample(_GROCERIES, r.randint(1, 6))
    cart = {item: r.randint(1, 9) for item in chosen}
    aisle_mapping = {item: [f"Aisle {r.randint(1, 6)}", item in _CHILLED]
                     for item in _GROCERIES}
    fulfillment_cart = {item: [cart[item]] + aisle_mapping[item]
                        for item in chosen}
    store_inventory = {}
    for item in r.sample(_GROCERIES, len(_GROCERIES)):
        stock = r.randint(1, 15)
        if item in cart:
            stock = cart[item] + r.choice([0, 0, 1, 3, 7])
        store_inventory[item] = [stock] + aisle_mapping[item]
    return cart, aisle_mapping, fulfillment_cart, store_inventory


def _reference():
    def sort_entries(cart):
        return dict(sorted(cart.items()))

    def send_to_store(cart, aisle_mapping):
        fulfillment_cart = {}
        for key, quantity in cart.items():
            fulfillment_cart[key] = [quantity] + aisle_mapping[key]
        return dict(sorted(fulfillment_cart.items(), reverse=True))

    def update_store_inventory(fulfillment_cart, store_inventory):
        for key, values in fulfillment_cart.items():
            store_inventory[key][0] = store_inventory[key][0] - values[0]
            if store_inventory[key][0] == 0:
                store_inventory[key][0] = "Out of Stock"
        return store_inventory

    return {"sort_entries": sort_entries, "send_to_store": send_to_store,
            "update_store_inventory": update_store_inventory}


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    for _ in range(6):
        cart, aisle_mapping, fulfillment_cart, store_inventory = _gen(r)
        assert (list(got["sort_entries"](deepcopy(cart)).items())
                == list(want["sort_entries"](deepcopy(cart)).items())), \
            f"sort_entries({cart!r})"
        assert (list(got["send_to_store"](deepcopy(cart),
                                          deepcopy(aisle_mapping)).items())
                == list(want["send_to_store"](deepcopy(cart),
                                              deepcopy(aisle_mapping)).items())), \
            f"send_to_store({cart!r}, {aisle_mapping!r})"
        assert (got["update_store_inventory"](deepcopy(fulfillment_cart),
                                              deepcopy(store_inventory))
                == want["update_store_inventory"](deepcopy(fulfillment_cart),
                                                  deepcopy(store_inventory))), \
            f"update_store_inventory({fulfillment_cart!r}, {store_inventory!r})"

    # canonical cases from exercism's dict_methods_test_data.py
    assert list(got["sort_entries"](
        {"Banana": 4, "Apple": 2, "Orange": 1, "Pear": 12}).items()) == [
            ("Apple", 2), ("Banana", 4), ("Orange", 1), ("Pear", 12)]
    assert list(got["sort_entries"](
        {"Apple": 3, "Orange": 5, "Banana": 1, "Avocado": 2}).items()) == [
            ("Apple", 3), ("Avocado", 2), ("Banana", 1), ("Orange", 5)]
    assert list(got["send_to_store"](
        {"Banana": 3, "Apple": 2, "Orange": 1, "Milk": 2},
        {"Banana": ["Aisle 5", False], "Apple": ["Aisle 4", False],
         "Orange": ["Aisle 4", False], "Milk": ["Aisle 2", True]}).items()) == [
            ("Orange", [1, "Aisle 4", False]), ("Milk", [2, "Aisle 2", True]),
            ("Banana", [3, "Aisle 5", False]), ("Apple", [2, "Aisle 4", False])]
    assert list(got["send_to_store"](
        {"Orange": 1},
        {"Banana": ["Aisle 5", False], "Apple": ["Aisle 4", False],
         "Orange": ["Aisle 4", False], "Milk": ["Aisle 2", True]}).items()) == [
            ("Orange", [1, "Aisle 4", False])]
    assert got["update_store_inventory"](
        {"Orange": [1, "Aisle 4", False], "Milk": [2, "Aisle 2", True],
         "Banana": [3, "Aisle 5", False], "Apple": [2, "Aisle 4", False]},
        {"Banana": [15, "Aisle 5", False], "Apple": [12, "Aisle 4", False],
         "Orange": [1, "Aisle 4", False], "Milk": [4, "Aisle 2", True]}) == {
        "Banana": [12, "Aisle 5", False], "Apple": [10, "Aisle 4", False],
        "Orange": ["Out of Stock", "Aisle 4", False],
        "Milk": [2, "Aisle 2", True]}
    assert got["update_store_inventory"](
        {"Kiwi": [3, "Aisle 6", False]},
        {"Kiwi": [3, "Aisle 6", False], "Juice": [5, "Aisle 5", False],
         "Yoghurt": [2, "Aisle 2", True], "Milk": [5, "Aisle 2", True]}) == {
        "Juice": [5, "Aisle 5", False], "Yoghurt": [2, "Aisle 2", True],
        "Milk": [5, "Aisle 2", True],
        "Kiwi": ["Out of Stock", "Aisle 6", False]}
