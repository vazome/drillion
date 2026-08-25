def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from copy import deepcopy

from _lib import rng

_GROCERIES = ["Apple", "Banana", "Orange", "Raspberry", "Blueberries",
              "Broccoli", "Kiwi", "Melon", "Pear", "Juice", "Milk", "Yoghurt"]
_RECIPES = ["Banana Bread", "Raspberry Pie", "Pasta Primavera", "Apple Pie",
            "Blueberry Crumble", "Lentil Soup"]


def _cart(r, size):
    return {item: r.randint(1, 9) for item in r.sample(_GROCERIES, size)}


def _gen(r):
    cart = _cart(r, r.randint(0, 4))
    items_to_add = [r.choice(_GROCERIES) for _ in range(r.randint(1, 6))]
    if r.random() < 0.5:
        items_to_add = tuple(items_to_add)
    notes = tuple(r.sample(_GROCERIES, r.randint(1, 5)))
    ideas = {recipe: _cart(r, r.randint(2, 4))
             for recipe in r.sample(_RECIPES, r.randint(1, 3))}
    updates = tuple((recipe, _cart(r, r.randint(2, 4)))
                    for recipe in r.sample(_RECIPES, r.randint(1, 3)))
    return cart, items_to_add, notes, ideas, updates


def _reference():
    def add_item(current_cart, items_to_add):
        for item in items_to_add:
            current_cart.setdefault(item, 0)
            current_cart[item] += 1
        return current_cart

    def read_notes(notes):
        return dict.fromkeys(notes, 1)

    def update_recipes(ideas, recipe_updates):
        ideas.update(recipe_updates)
        return ideas

    return {"add_item": add_item, "read_notes": read_notes,
            "update_recipes": update_recipes}


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    for _ in range(6):
        cart, items_to_add, notes, ideas, updates = _gen(r)
        assert (got["add_item"](deepcopy(cart), items_to_add)
                == want["add_item"](deepcopy(cart), items_to_add)), \
            f"add_item({cart!r}, {items_to_add!r})"
        assert got["read_notes"](notes) == want["read_notes"](notes), \
            f"read_notes({notes!r})"
        assert (got["update_recipes"](deepcopy(ideas), deepcopy(updates))
                == want["update_recipes"](deepcopy(ideas), deepcopy(updates))), \
            f"update_recipes({ideas!r}, {updates!r})"

    # canonical cases from exercism's dict_methods_test_data.py
    assert got["add_item"]({"Apple": 1, "Banana": 4},
                           ("Apple", "Banana", "Orange")) == {
        "Apple": 2, "Banana": 5, "Orange": 1}
    assert got["add_item"]({"Orange": 1, "Raspberry": 1, "Blueberries": 10},
                           ["Raspberry", "Blueberries", "Raspberry"]) == {
        "Orange": 1, "Raspberry": 3, "Blueberries": 11}
    assert got["read_notes"](("Apple", "Banana")) == {"Apple": 1, "Banana": 1}
    assert got["read_notes"](["Broccoli", "Kiwi", "Melon"]) == {
        "Broccoli": 1, "Kiwi": 1, "Melon": 1}
    assert got["update_recipes"](
        {"Apple Pie": {"Apple": 1, "Pie Crust": 1, "Cream Custard": 1},
         "Blueberry Pie": {"Blueberries": 1, "Pie Crust": 1,
                           "Cream Custard": 1}},
        (("Blueberry Pie", {"Blueberries": 2, "Pie Crust": 1,
                            "Cream Custard": 1}),
         ("Apple Pie", {"Apple": 1, "Pie Crust": 1,
                        "Cream Custard": 1}))) == {
        "Apple Pie": {"Apple": 1, "Pie Crust": 1, "Cream Custard": 1},
        "Blueberry Pie": {"Blueberries": 2, "Pie Crust": 1,
                          "Cream Custard": 1}}
    assert got["update_recipes"](
        {"Banana Bread": {"Banana": 1, "Walnuts": 1}},
        (("Blueberry Crumble", {"Blueberries": 2, "Yogurt": 3}),)) == {
        "Banana Bread": {"Banana": 1, "Walnuts": 1},
        "Blueberry Crumble": {"Blueberries": 2, "Yogurt": 3}}
