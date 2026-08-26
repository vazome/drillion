def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_PANTRY = ["onions", "tomatoes", "ginger paste", "garlic paste", "vegetable oil",
           "bay leaves", "cloves", "cardamom", "cilantro", "peppercorns", "cumin powder",
           "chickpeas", "coriander powder", "red chili powder", "ground turmeric",
           "garam masala", "ginger", "tofu", "soy sauce", "sesame seeds", "lemon juice",
           "brown sugar", "corn starch", "arugula", "pears", "blue cheese", "pine nuts",
           "balsamic vinegar", "black pepper", "honeydew", "coconut water", "mint leaves",
           "lime juice", "salt", "english cucumber", "pork tenderloin"]

_DISHES = ["Punjabi-Style Chole", "Ginger Glazed Tofu Cutlets", "Barley Risotto",
           "Arugula and Roasted Pork Salad", "Avocado Deviled Eggs", "Asparagus Puffs",
           "Kingfish Lettuce Cups", "Vegetarian Khoresh Bademjan", "Satay Steak Skewers",
           "Dahi Puri with Black Chickpeas", "Grilled Flank Steak with Caesar Salad"]


def _gen(r):
    dish_name = r.choice(_DISHES)
    picked = r.sample(_PANTRY, r.randint(4, 11))
    dish_ingredients = picked + [r.choice(picked) for _ in range(r.randint(1, 5))]
    r.shuffle(dish_ingredients)
    dishes = [set(r.sample(_PANTRY, r.randint(3, 9))) for _ in range(r.randint(0, 5))]
    menu = [r.choice(_DISHES) for _ in range(r.randint(4, 10))]
    appetizers = [r.choice(_DISHES) for _ in range(r.randint(1, 6))]
    return dish_name, dish_ingredients, dishes, menu, appetizers


def _reference():
    def clean_ingredients(dish_name, dish_ingredients):
        return dish_name, set(dish_ingredients)

    def compile_ingredients(dishes):
        combined_ingredients = set()
        for ingredients in dishes:
            combined_ingredients = combined_ingredients.union(ingredients)
        return combined_ingredients

    def separate_appetizers(dishes, appetizers):
        return list(set(dishes) - set(appetizers))

    return {"clean_ingredients": clean_ingredients,
            "compile_ingredients": compile_ingredients,
            "separate_appetizers": separate_appetizers}


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    for _ in range(6):
        dish_name, dish_ingredients, dishes, menu, appetizers = _gen(r)

        cleaned = got["clean_ingredients"](dish_name, list(dish_ingredients))
        assert cleaned == want["clean_ingredients"](dish_name, dish_ingredients), (
            f"clean_ingredients({dish_name!r}, {dish_ingredients!r})")

        assert (got["compile_ingredients"]([set(d) for d in dishes])
                == want["compile_ingredients"](dishes)), f"compile_ingredients({dishes!r})"

        left = got["separate_appetizers"](list(menu), list(appetizers))
        assert isinstance(left, list), f"separate_appetizers must return a list, got {type(left)}"
        assert sorted(left) == sorted(want["separate_appetizers"](menu, appetizers)), (
            f"separate_appetizers({menu!r}, {appetizers!r}) -> {left!r}")

    # canonical cases from exercism's cater-waiter instructions
    assert got["clean_ingredients"](
        "Punjabi-Style Chole",
        ["onions", "tomatoes", "ginger paste", "garlic paste", "ginger paste",
         "vegetable oil", "bay leaves", "cloves", "cardamom", "cilantro", "peppercorns",
         "cumin powder", "chickpeas", "coriander powder", "red chili powder",
         "ground turmeric", "garam masala", "chickpeas", "ginger", "cilantro"]) == (
        "Punjabi-Style Chole",
        {"garam masala", "bay leaves", "ground turmeric", "ginger", "garlic paste",
         "peppercorns", "ginger paste", "red chili powder", "cardamom", "chickpeas",
         "cumin powder", "vegetable oil", "tomatoes", "coriander powder", "onions",
         "cilantro", "cloves"})

    assert got["clean_ingredients"]("Simple Syrup", ["sugar", "water", "sugar"]) == (
        "Simple Syrup", {"sugar", "water"})

    assert got["compile_ingredients"](
        [{"tofu", "soy sauce", "ginger", "corn starch", "garlic", "brown sugar",
          "sesame seeds", "lemon juice"},
         {"pork tenderloin", "arugula", "pears", "blue cheese", "pine nuts",
          "balsamic vinegar", "onions", "black pepper"},
         {"honeydew", "coconut water", "mint leaves", "lime juice", "salt",
          "english cucumber"}]) == {
        "arugula", "brown sugar", "honeydew", "coconut water", "english cucumber",
        "balsamic vinegar", "mint leaves", "pears", "pork tenderloin", "ginger",
        "blue cheese", "soy sauce", "sesame seeds", "black pepper", "garlic",
        "lime juice", "corn starch", "pine nuts", "lemon juice", "onions", "salt", "tofu"}

    assert got["compile_ingredients"]([]) == set()

    canonical_menu = ["Avocado Deviled Eggs", "Flank Steak with Chimichurri and Asparagus",
                      "Kingfish Lettuce Cups", "Grilled Flank Steak with Caesar Salad",
                      "Vegetarian Khoresh Bademjan", "Avocado Deviled Eggs",
                      "Barley Risotto", "Kingfish Lettuce Cups"]
    canonical_appetizers = ["Kingfish Lettuce Cups", "Avocado Deviled Eggs",
                            "Satay Steak Skewers", "Dahi Puri with Black Chickpeas",
                            "Avocado Deviled Eggs", "Asparagus Puffs", "Asparagus Puffs"]
    plated = got["separate_appetizers"](canonical_menu, canonical_appetizers)
    assert isinstance(plated, list), f"separate_appetizers must return a list, got {type(plated)}"
    assert sorted(plated) == ["Barley Risotto",
                              "Flank Steak with Chimichurri and Asparagus",
                              "Grilled Flank Steak with Caesar Salad",
                              "Vegetarian Khoresh Bademjan"]
