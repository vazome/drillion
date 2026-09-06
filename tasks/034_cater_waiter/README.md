---
title: sets — sort dishes into diets, find the singleton ingredients
difficulty: hard
tier: core
minutes: 15
prereqs: [33]
tags: [sets]
source: exercism/python concept/cater-waiter (MIT, adapted)
---
# sets — sort dishes into diets, find the singleton ingredients

*Sets — subset (`<=`) and symmetric difference (`^`), sorting a menu by diet.*

## Read first
- [Set types — set, frozenset](https://devdocs.io/python~3.14/library/stdtypes#set) — the full method table; the *methods* take any iterable, the *operators* need sets on both sides
- [set.issubset()](https://devdocs.io/python~3.14/library/stdtypes#frozenset.issubset) — "is every one of mine also in yours?"; the operator form is `<=`
- [set.symmetric_difference()](https://devdocs.io/python~3.14/library/stdtypes#frozenset.symmetric_difference) — in one or the other but not both; the operator form is `^`
- [Symmetric difference (Wikipedia)](https://en.wikipedia.org/wiki/Symmetric_difference) — why chaining it over three or more sets is not "appears exactly once"
- [Real Python: Sets in Python](https://realpython.com/python-sets/) — a walk through the operations with pictures of the overlaps
- [Set and logic symbols cheat sheet](http://notes.imt-decal.org/sets/cheat-sheet.html) — the maths notation the method names come from

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
The guest list for the catering event comes with dietary needs, so every dish has to be filed under vegan, vegetarian, keto, paleo or omnivore before the staff can plate anything. "This dish is vegan" is not a judgement call: it means every one of its ingredients is on the vegan list, which is precisely the subset test. The second chore is the shopper's problem — inside one diet, find the ingredients that only one dish uses, because those are the ones nobody notices are missing until service starts. That is symmetric difference. Between them you have the two set questions that are easy to write badly with loops and trivial with an operator.

## You get
Nothing. `solve()` takes **no arguments**; the dishes and the reference data arrive as arguments to the functions you hand back.

> [!NOTE]
> Exercism asks for all seven functions in one `sets.py`. Here the task is split in three: **this task covers tasks 3 and 7** — the two comparison-shaped ones. Tasks 1, 5 and 6 are task `032_cater_waiter`; tasks 2 and 4 are task `033_cater_waiter`.
>
> One change to Exercism's signature: `categorize_dish` takes the categories as a **third argument** instead of importing five constants from `sets_categories_data.py`. Everything else about the task is the same, and the grader passes Exercism's real `VEGAN` and `OMNIVORE` ingredient sets for its canonical checks.

## You return
A dict with these two functions.

| key | parameters | returns |
| --- | --- | --- |
| `"categorize_dish"` | `dish_name` (a string), `dish_ingredients` (a `set`), `categories` (a tuple of `(category_name, ingredient_set)` pairs, already in the order to try them) | the string `"<dish name>: <CATEGORY>"` for the first category whose ingredient set contains every one of the dish's ingredients |
| `"singleton_ingredients"` | `dishes` — a list where each dish is a `set` of ingredients; `overlapping` — the set of ingredients that appear in more than one of those dishes | the `set` of ingredients that appear in exactly one dish |

```python
kitchen = solve()

categories = (("VEGAN", {"tofu", "soy sauce", "rice"}),
              ("OMNIVORE", {"tofu", "soy sauce", "rice", "bacon"}))

kitchen["categorize_dish"]("Sticky Lemon Tofu", {"tofu", "soy sauce"}, categories)
# -> "Sticky Lemon Tofu: VEGAN"

kitchen["categorize_dish"]("Bacon Fried Rice", {"rice", "bacon"}, categories)
# -> "Bacon Fried Rice: OMNIVORE"

kitchen["singleton_ingredients"]([{"salt", "tofu"}, {"salt", "pears"}], {"salt"})
# -> {"tofu", "pears"}
```

## Rules
- the dict keys are exactly the two strings above, and each value is the function **itself** — `{"categorize_dish": categorize_dish}`, no parentheses
- `categorize_dish` returns one string: the dish name, then a colon, then a space, then the category name in capitals — `"Sticky Lemon Tofu: VEGAN"`
- **the first category that fits wins.** The `categories` tuple is already in the order Exercism uses (vegan, vegetarian, keto, paleo, omnivore), so walk it front to back and return on the first match; a vegan dish also fits omnivore, and the answer is still `VEGAN`
- a dish belongs to a category only if **every** one of its ingredients is in that category's set — one stray ingredient is enough to rule it out
- `singleton_ingredients` returns a `set`, empty when every ingredient is shared

> [!WARNING]
> `singleton_ingredients` means *exactly one dish*, not *an odd number of dishes*. Chaining `^` across more than two sets keeps an ingredient that appears in three of them — which is why the second argument exists: subtract it at the end. (Exercism's introduction spells this out in the note under "Set Symmetric Difference".)

## Hints
### Hint 1
`categorize_dish` is a loop with a `return` inside it — walk the categories in the order you were handed and return as soon as one fits, because returning early is what makes "first match wins" true. The fits-or-not test is one operator: if all of the dish's ingredients are also in the category's set, the dish's ingredients are a *subset* of it.

`singleton_ingredients` is not a loop over ingredients; it is one fold over the dishes plus one subtraction at the end.
### Hint 2
`categorize_dish` — each entry in `categories` is a `(name, ingredient_set)` pair, so unpack it into two names as you loop. The test you want is "is every ingredient of this dish inside that category" — a subset test, which sets spell with a comparison operator (there is also a method form, which has the advantage of accepting a list). On a match, build the answer with an f-string or with `+`, and return it right there. If nothing matches, falling off the end returns `None`, which is fine — the task promises every dish fits something.

`singleton_ingredients` — start from an empty `set()`, then combine each dish into it with `^`. After that fold, an ingredient survives when it appeared in an odd number of dishes, so it is still holding the ones that showed up three or five times. Subtract `overlapping` (`-`) and only the true singletons are left.
### Hint 3
Different data, same two moves. Which environment does a service's config belong to, and which settings does only one service use?

```python
envs = (("STAGING", {"db_url", "log_level"}),
        ("PROD",    {"db_url", "log_level", "pager_key"}))

def where(service, keys, envs):
    for name, allowed in envs:
        if set(keys) <= allowed:
            return f"{service}: {name}"
    return None

where("api", {"db_url"}, envs)              # -> 'api: STAGING'
where("api", {"db_url", "pager_key"}, envs) # -> 'api: PROD'

services = [{"db_url", "retries"}, {"db_url", "timeout"},
            {"db_url", "timeout"}, {"timeout"}]
shared = {"db_url", "timeout"}
only_one = set()
for keys in services:
    only_one ^= keys
only_one -= shared                          # -> {'retries'}
```

Drop the last line and `db_url` and `timeout` sneak back in: each is in three services, an odd number, so the `^` fold kept both.
