def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from collections import Counter

from _lib import rng

_INGREDIENTS = ["tofu", "soy sauce", "salt", "black pepper", "cornstarch", "vegetable oil",
                "garlic", "ginger", "water", "vegetable stock", "lemon juice", "lemon zest",
                "sugar", "shrimp", "bacon", "avocado", "chickpeas", "fresh tortillas",
                "sea salt", "guajillo chile", "slivered almonds", "olive oil", "butter",
                "onion", "spaghetti", "mushrooms", "red onion", "honey", "cashews",
                "nutritional yeast", "parsley", "breadcrumbs", "celeriac", "yeast"]

_DISHES = ["Sticky Lemon Tofu", "Barley Risotto", "Vegetarian Khoresh Bademjan",
           "Kingfish Lettuce Cups", "Avocado Deviled Eggs", "Satay Steak Skewers",
           "Punjabi-Style Chole", "Grilled Flank Steak with Caesar Salad"]

_CATEGORY_NAMES = ("VEGAN", "VEGETARIAN", "KETO", "PALEO", "OMNIVORE")

# Exercism's own reference data — used only by the canonical cases below
_VEGAN = {'allspice powder', 'apples', 'baking soda', 'balsamic vinegar', 'barberries',
          'barley malt', 'basmati rice', 'bell pepper', 'black pepper', 'black peppercorn',
          'black-eyed peas', 'brandy', 'breadcrumbs', 'brown sugar', 'bulgur',
          'butternut squash', 'calabash nutmeg', 'cardamom powder', 'carrot', 'cashews',
          'cayenne pepper', 'celeriac', 'chickpea flour', 'chili flakes', 'chinese eggplants',
          'chives', 'chopped parsley', 'cilantro', 'cinnamon powder', 'clove powder', 'cloves',
          'coconut oil', 'coriander', 'coriander powder', 'coriander seeds', 'corn',
          'corn flour', 'cornstarch', 'cumin', 'cumin powder', 'cumin seeds', 'currants',
          'curry leaves', 'dill', 'dried blueberries', 'dried cherries', 'dried cranberries',
          'eggplants', 'figs', 'firm tofu', 'flour', 'fresh basil', 'fresh ginger',
          'fresh red chili', 'garam masala', 'garlic', 'garlic paste', 'garlic powder',
          'ginger', 'grains of selim', 'green beans', 'green onions', 'ground almonds',
          'ground turmeric', 'harissa', 'hing', 'honey', 'hot water', 'khmeli suneli',
          'kosher salt', 'lemon', 'lemon juice', 'lemon zest', 'mango powder', 'mangoes',
          'mashed potatoes', 'mixed herbs', 'mushrooms', 'mustard seeds', 'nigella seeds',
          'nutritional yeast', 'oil', 'olive oil', 'onion', 'orange juice', 'orange zest',
          'oregano', 'parev shortcrust pastry', 'pareve puff pastry', 'parsley', 'peanuts',
          'pecans', 'persian cucumber', 'pomegranate concentrate', 'pomegranate molasses',
          'pomegranate seeds', 'raisins', 'red bell pepper', 'red chili powder', 'red onion',
          'red pepper flakes', 'rice vinegar', 'ripe plantains', 'rosemary', 'saffron powder',
          'salt', 'scallions', 'serrano chili', 'sesame oil', 'sesame seeds', 'silken tofu',
          'siracha', 'slivered almonds', 'smoked paprika', 'smoked tofu', 'sorghum stems',
          'soy sauce', 'spaghetti', 'spring onion', 'spring onions', 'sugar', 'sunflower oil',
          'thyme', 'tofu', 'tomato', 'tomato paste', 'tomatoes', 'turmeric', 'turmeric powder',
          'vegan butter', 'vegan unsweetened yoghurt', 'vegetable oil', 'vegetable stock',
          'vegetarian worcestershire sauce', 'vinegar', 'walnuts', 'water', 'white rice',
          'yeast', 'yellow onion', 'yellow onions', 'yellow split peas', 'yukon gold potato',
          "za'atar", 'zucchini'}

_OMNIVORE = {'anaheim chili', 'anchovy fillets', 'apple cider vinegar', 'arborio risotto rice',
             'avocado', 'baby carrot', 'baby scallops', 'baby squid', 'bacon',
             'balsamic vinegar', 'bay leaves', 'beef brisket', 'beer', 'bell pepper',
             'black cardamom', 'black chickpeas', 'black pepper', 'black peppercorns',
             'brown sugar', 'butter', 'carrot', 'celery', 'celery seeds', 'chaat masala',
             'cherry tomatoes', 'chicken', 'chicken wings', 'chickpeas', 'chile manzano',
             'chiles de árbol', 'chili powder', 'chipotle adobo sauce', 'cilantro',
             'cinnamon sticks', 'clams', 'cloves', 'coriander', 'couscous', 'crab legs',
             'crushed red pepper flakes', 'cumin', 'date syrup', 'fennel bulbs', 'filo pastry',
             'fish stock', 'flat-leaf parsley', 'fresh corn tortillas', 'fresh mint',
             'fresh ricotta', 'fresh thyme', 'fresh tortillas', 'garlic', 'garlic cloves',
             'ginger', 'green bell pepper', 'green cabbage', 'green cardamom', 'guajillo chile',
             'harissa', 'hazelnuts', 'honey', 'kosher salt', 'leg of lamb', 'lemon',
             'lemon juice', 'lime juice', 'limes', 'maggi cubes', 'marjoram', 'mayonnaise',
             'mexican crema', 'mint', 'mussels', 'oaxaca cheese', 'olive oil', 'onion',
             'onions', 'oranges', 'oregano', 'pani puri', 'parmesan cheese', 'parsley',
             'pepitas', 'poblano chili', 'prawns', 'red bell pepper', 'red cabbage',
             'red onion', 'red pepper flakes', 'red snapper', 'rhubarb', 'rice',
             'roasted chicken', 'roma tomatoes', 'rosemary', 'salsa', 'salt',
             'scallion chutney', 'scotch bonnet pepper', 'sea salt', 'serrano chili',
             'sesame seeds', 'shelled large shrimp', 'shrimp', 'slivered almonds', 'soy sauce',
             'sriracha', 'sugar', 'summer squash', 'tahini', 'tamarind concentrate', 'thin sev',
             'thyme', 'toasted bread', 'tomato', 'tomato paste', 'tomato puree', 'tomatoes',
             'turmeric', 'vegetable bullion', 'vegetable oil', 'vinegar', 'water',
             'white onion', 'white pepper', 'white vinegar', 'white wine', 'white wine vinegar',
             'whole-milk yogurt', 'worcestershire sauce', 'yellow bell pepper',
             'yellow mustard', 'yellow onion', 'yoghurt', 'yukon gold potato', 'zucchini'}

_EX1 = {'black pepper', 'breadcrumbs', 'celeriac', 'chickpea flour', 'flour', 'lemon',
        'parsley', 'salt', 'soy sauce', 'sunflower oil', 'water'}

_EX2 = {'black pepper', 'cornstarch', 'garlic', 'ginger', 'lemon juice', 'lemon zest', 'salt',
        'soy sauce', 'sugar', 'tofu', 'vegetable oil', 'vegetable stock', 'water'}

_EX3 = {'black pepper', 'garlic', 'lemon juice', 'mixed herbs', 'nutritional yeast',
        'olive oil', 'salt', 'silken tofu', 'smoked tofu', 'soy sauce', 'spaghetti', 'turmeric'}

_EX4 = {'barley malt', 'bell pepper', 'cashews', 'flour', 'fresh basil', 'garlic',
        'garlic powder', 'honey', 'mushrooms', 'nutritional yeast', 'olive oil', 'oregano',
        'red onion', 'red pepper flakes', 'rosemary', 'salt', 'sugar', 'tomatoes', 'water',
        'yeast'}

_EX5 = {'cardamom powder', 'chickpea flour', 'cilantro', 'cinnamon powder', 'clove powder',
        'coriander powder', 'coriander seeds', 'cumin powder', 'curry leaves', 'fresh ginger',
        'fresh red chili', 'garam masala', 'garlic', 'garlic paste', 'hing', 'mango powder',
        'mangoes', 'mashed potatoes', 'mustard seeds', 'nigella seeds', 'oil', 'onion',
        'red chili powder', 'salt', 'serrano chili', 'sugar', 'turmeric', 'turmeric powder',
        'vinegar', 'water'}

_EXAMPLE_INTERSECTION = {'black pepper', 'cardamom powder', 'chickpea flour', 'cilantro',
                         'cinnamon powder', 'clove powder', 'coriander powder',
                         'coriander seeds', 'cumin powder', 'curry leaves', 'flour',
                         'fresh ginger', 'fresh red chili', 'garam masala', 'garlic',
                         'garlic paste', 'hing', 'lemon juice', 'mango powder', 'mangoes',
                         'mashed potatoes', 'mustard seeds', 'nigella seeds',
                         'nutritional yeast', 'oil', 'olive oil', 'onion', 'red chili powder',
                         'salt', 'serrano chili', 'soy sauce', 'sugar', 'turmeric',
                         'turmeric powder', 'vinegar', 'water'}

_EXAMPLE_SINGLETONS = {'barley malt', 'bell pepper', 'breadcrumbs', 'cashews', 'celeriac',
                       'cornstarch', 'fresh basil', 'garlic powder', 'ginger', 'honey', 'lemon',
                       'lemon zest', 'mixed herbs', 'mushrooms', 'oregano', 'parsley',
                       'red onion', 'red pepper flakes', 'rosemary', 'silken tofu',
                       'smoked tofu', 'spaghetti', 'sunflower oil', 'tofu', 'tomatoes',
                       'vegetable oil', 'vegetable stock', 'yeast'}

_FOUR_OVERLAP = {'black pepper', 'flour', 'garlic', 'lemon juice', 'nutritional yeast',
                 'olive oil', 'salt', 'soy sauce', 'sugar', 'water'}

_FOUR_SINGLETONS = {'barley malt', 'bell pepper', 'breadcrumbs', 'cashews', 'celeriac',
                    'chickpea flour', 'cornstarch', 'fresh basil', 'garlic powder', 'ginger',
                    'honey', 'lemon', 'lemon zest', 'mixed herbs', 'mushrooms', 'oregano',
                    'parsley', 'red onion', 'red pepper flakes', 'rosemary', 'silken tofu',
                    'smoked tofu', 'spaghetti', 'sunflower oil', 'tofu', 'tomatoes', 'turmeric',
                    'vegetable oil', 'vegetable stock', 'yeast'}


def _gen(r):
    categories = tuple((name, set(r.sample(_INGREDIENTS, r.randint(8, 13) + 3 * i)))
                       for i, name in enumerate(_CATEGORY_NAMES))
    members = sorted(categories[r.randrange(len(categories))][1])
    dish_name = r.choice(_DISHES)
    dish_ingredients = set(r.sample(members, r.randint(1, min(6, len(members)))))
    dishes = [set(r.sample(_INGREDIENTS, r.randint(4, 11)))
              for _ in range(r.randint(2, 6))]
    counts = Counter()
    for ingredients in dishes:
        counts.update(ingredients)
    overlapping = {name for name, seen in counts.items() if seen > 1}
    return dish_name, dish_ingredients, categories, dishes, overlapping


def _reference():
    def categorize_dish(dish_name, dish_ingredients, categories):
        for category_name, category_ingredients in categories:
            if set(dish_ingredients) <= category_ingredients:
                return dish_name + ": " + category_name
        return None

    def singleton_ingredients(dishes, overlapping):
        all_ingredients = set()
        for ingredients in dishes:
            all_ingredients = all_ingredients ^ ingredients
        return all_ingredients - overlapping

    return {"categorize_dish": categorize_dish,
            "singleton_ingredients": singleton_ingredients}


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    for _ in range(6):
        dish_name, dish_ingredients, categories, dishes, overlapping = _gen(r)
        assert (got["categorize_dish"](dish_name, set(dish_ingredients), categories)
                == want["categorize_dish"](dish_name, dish_ingredients, categories)), (
            f"categorize_dish({dish_name!r}, {sorted(dish_ingredients)!r}, ...)")
        assert (got["singleton_ingredients"]([set(d) for d in dishes], set(overlapping))
                == want["singleton_ingredients"](dishes, overlapping)), (
            f"singleton_ingredients({dishes!r}, {sorted(overlapping)!r})")

    # canonical cases from exercism's cater-waiter instructions, against its real data
    canonical_categories = (("VEGAN", _VEGAN), ("OMNIVORE", _OMNIVORE))
    assert got["categorize_dish"](
        "Sticky Lemon Tofu",
        {"tofu", "soy sauce", "salt", "black pepper", "cornstarch", "vegetable oil",
         "garlic", "ginger", "water", "vegetable stock", "lemon juice", "lemon zest",
         "sugar"}, canonical_categories) == "Sticky Lemon Tofu: VEGAN"
    assert got["categorize_dish"](
        "Shrimp Bacon and Crispy Chickpea Tacos with Salsa de Guacamole",
        {"shrimp", "bacon", "avocado", "chickpeas", "fresh tortillas", "sea salt",
         "guajillo chile", "slivered almonds", "olive oil", "butter", "black pepper",
         "garlic", "onion"}, canonical_categories) == (
        "Shrimp Bacon and Crispy Chickpea Tacos with Salsa de Guacamole: OMNIVORE")

    assert got["singleton_ingredients"]([_EX1, _EX2, _EX3, _EX4, _EX5, _EX5],
                                        _EXAMPLE_INTERSECTION) == _EXAMPLE_SINGLETONS
    assert got["singleton_ingredients"]([_EX1, _EX2, _EX3, _EX4],
                                        _FOUR_OVERLAP) == _FOUR_SINGLETONS
    assert got["singleton_ingredients"]([_EX1, _EX1], set(_EX1)) == set()
