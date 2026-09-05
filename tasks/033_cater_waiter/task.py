# given — do not edit: the two reference lists Exercism keeps in sets_categories_data.py
ALCOHOLS = {'almond liqueur', 'aperol', 'bourbon', 'brandy', 'champagne', 'coffee liqueur',
            'dark rum', 'dry vermouth', 'gin', 'mezcal', 'orange curacao', 'prosecco', 'rum',
            'rye', 'scotch', 'sweet vermouth', 'tequila', 'triple sec', 'vodka', 'whiskey',
            'whisky', 'white rum'}

SPECIAL_INGREDIENTS = {'almonds', 'anchovy fillets', 'baby scallops', 'baby squid', 'bacon',
                       'beef', 'blue cheese', 'brie cheese', 'bulgur', 'butter', 'cashews',
                       'cheddar cheese', 'cherry tomatoes', 'chocolate', 'clams',
                       'cotija cheese', 'couscous', 'crab legs', 'cream', 'crema', 'eggs',
                       'feta cheese', 'filo pastry', 'firm tofu', 'fish', 'fish stock', 'flour',
                       'fresh cherry bocconcini', 'fresh cherry tomatoes', 'fresh ricotta',
                       'garlic', 'garlic cloves', 'gluten', 'greek yogurt', 'grilled king fish',
                       'ground almonds', 'ground pork', 'hazelnuts', 'heavy cream', 'honey',
                       'lobster', 'milk', 'mozzarella cheese', 'mussels', 'oaxaca cheese',
                       'onions', 'oyster sauce', 'oysters', 'paneer', 'parmesan',
                       'parmesan cheese', 'peanuts', 'pecans', 'pine nuts', 'pork belly',
                       'pork chops', 'pork tenderloin', 'prawns', 'red onion',
                       'roasted peanuts', 'roma tomatoes', 'salmon fillets', 'semolina',
                       'shelled large shrimp', 'shrimp', 'silken tofu', 'slivered almonds',
                       'smoked tofu', 'soy sauce', 'spaghetti', 'sprint onion', 'strawberries',
                       'swiss cheese', 'tilapia', 'toasted bread', 'toasted peanuts', 'tofu',
                       'tomato paste', 'tomato puree', 'tomatoes', 'walnuts', 'whey',
                       'whole-milk yogurt', 'yellow onion', 'yogurt'}


def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_MIXERS = ["club soda", "pomegranate juice", "sugar", "ginger", "whole cloves",
           "cinnamon stick", "honeydew", "coconut water", "mint leaves", "lime juice",
           "salt", "english cucumber", "grapefruit juice", "tonic water", "egg white",
           "simple syrup", "angostura bitters", "orange zest", "cold brew coffee"]

_DRINKS = ["Honeydew Cucumber", "Shirley Tonic", "Paloma", "Espresso Martini",
           "Cranberry Spritz", "Old Fashioned", "Summer Cooler", "Negroni Sbagliato"]

_PANTRY = ["ginger", "corn starch", "brown sugar", "sesame seeds", "lemon juice",
           "arugula", "pears", "balsamic vinegar", "black pepper", "olive oil",
           "cilantro", "bay leaves", "chickpeas", "sea salt", "guajillo chile",
           "tofu", "soy sauce", "garlic", "onions", "blue cheese", "pine nuts",
           "pork tenderloin", "bacon", "eggs", "butter", "shrimp", "walnuts", "flour"]

_DISHES = ["Ginger Glazed Tofu Cutlets", "Arugula and Roasted Pork Salad",
           "Sticky Lemon Tofu", "Barley Risotto", "Avocado Deviled Eggs",
           "Kingfish Lettuce Cups", "Vegetarian Khoresh Bademjan"]


def _gen(r):
    drink_name = r.choice(_DRINKS)
    drink_ingredients = r.sample(_MIXERS, r.randint(3, 6))
    if r.random() < 0.5:
        drink_ingredients.append(r.choice(sorted(ALCOHOLS)))
        r.shuffle(drink_ingredients)
    dish_name = r.choice(_DISHES)
    dish_ingredients = r.sample(_PANTRY, r.randint(4, 10))
    if r.random() < 0.3:
        dish_ingredients = set(dish_ingredients)
    else:
        dish_ingredients = dish_ingredients + [r.choice(dish_ingredients)]
        r.shuffle(dish_ingredients)
    return drink_name, drink_ingredients, (dish_name, dish_ingredients)


def _reference():
    def check_drinks(drink_name, drink_ingredients):
        if not ALCOHOLS.isdisjoint(drink_ingredients):
            return drink_name + " Cocktail"
        return drink_name + " Mocktail"

    def tag_special_ingredients(dish):
        return dish[0], (SPECIAL_INGREDIENTS & set(dish[1]))

    return {"check_drinks": check_drinks,
            "tag_special_ingredients": tag_special_ingredients}


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    for _ in range(6):
        drink_name, drink_ingredients, dish = _gen(r)
        assert (got["check_drinks"](drink_name, list(drink_ingredients))
                == want["check_drinks"](drink_name, drink_ingredients)), (
            f"check_drinks({drink_name!r}, {drink_ingredients!r})")
        assert (got["tag_special_ingredients"]((dish[0], type(dish[1])(dish[1])))
                == want["tag_special_ingredients"](dish)), f"tag_special_ingredients({dish!r})"

    # canonical cases from exercism's cater-waiter instructions
    assert got["check_drinks"]("Honeydew Cucumber",
                               ["honeydew", "coconut water", "mint leaves", "lime juice",
                                "salt", "english cucumber"]) == "Honeydew Cucumber Mocktail"
    assert got["check_drinks"]("Shirley Tonic",
                               ["cinnamon stick", "scotch", "whole cloves", "ginger",
                                "pomegranate juice", "sugar",
                                "club soda"]) == "Shirley Tonic Cocktail"
    assert got["tag_special_ingredients"](
        ("Ginger Glazed Tofu Cutlets",
         ["tofu", "soy sauce", "ginger", "corn starch", "garlic", "brown sugar",
          "sesame seeds", "lemon juice"])) == (
        "Ginger Glazed Tofu Cutlets", {"garlic", "soy sauce", "tofu"})
    assert got["tag_special_ingredients"](
        ("Arugula and Roasted Pork Salad",
         ["pork tenderloin", "arugula", "pears", "blue cheese", "pine nuts",
          "balsamic vinegar", "onions", "black pepper"])) == (
        "Arugula and Roasted Pork Salad",
        {"pork tenderloin", "blue cheese", "pine nuts", "onions"})
    assert got["tag_special_ingredients"](
        ("Cucumber Salad", {"english cucumber", "rice vinegar"})) == (
        "Cucumber Salad", set())
