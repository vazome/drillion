---
title: sets — spot the alcohol, tag the allergens
difficulty: easy
tier: core
minutes: 14
prereqs: [32]
tags: [sets]
source: exercism/python concept/cater-waiter (MIT, adapted)
---
# sets — spot the alcohol, tag the allergens

*Sets — `isdisjoint` and `&`, checking a menu against two reference lists.*

## Read first
- [Set types — set, frozenset](https://devdocs.io/python~3.14/library/stdtypes#set) — the full method table; note that the *methods* take any iterable while the *operators* need sets on both sides
- [set.isdisjoint()](https://devdocs.io/python~3.14/library/stdtypes#frozenset.isdisjoint) — "do these two share nothing?", `True` when there is no overlap; there is no operator form
- [set.intersection()](https://devdocs.io/python~3.14/library/stdtypes#frozenset.intersection) — the shared items themselves; the operator form is `&`
- [Real Python: Sets in Python](https://realpython.com/python-sets/) — a walk through the operations with pictures of the overlaps
- [Set and logic symbols cheat sheet](http://notes.imt-decal.org/sets/cheat-sheet.html) — the maths notation the method names come from

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
Two questions at a catering event have legal weight rather than culinary weight. Is this drink actually alcohol-free, so it can be handed to the guest who asked for a mocktail? And does this dish contain anything on the allergen list, so it can be labelled before somebody eats it? Both are the same question asked of two collections: does this recipe touch that reference list at all, and if so, which items exactly. Sets answer both in one call each — one for "do these overlap, yes or no", one for "give me the overlap". Same pattern as checking a deployment's IAM actions against a banned-actions list.

## You get
Two reference sets, already written into the file above `solve` and marked `# given — do not edit`:

- `ALCOHOLS` — the 22 spirits, wines and liqueurs that make a drink a cocktail
- `SPECIAL_INGREDIENTS` — the 85 allergens and restricted foods that have to be printed on a dish label

`solve()` itself takes **no arguments**; the drinks and dishes arrive as arguments to the functions you hand back. Exercism imports these two names from `sets_categories_data.py`; here they are simply already in the file.

> [!NOTE]
> Exercism asks for all seven functions in one `sets.py`. Here the task is split in three: **this task covers tasks 2 and 4** — the two that check a recipe against a reference list. Tasks 1, 5 and 6 are task `032_cater_waiter`; tasks 3 and 7 are task `034_cater_waiter`.

## You return
A dict with these two functions.

| key | parameters | returns |
| --- | --- | --- |
| `"check_drinks"` | `drink_name` (a string), `drink_ingredients` (a list) | the drink name plus a single space plus `Cocktail` if any ingredient is in `ALCOHOLS`, otherwise the name plus `Mocktail` |
| `"tag_special_ingredients"` | `dish` — ONE argument, a tuple of `(dish name, ingredients)`, where the ingredients are a `list` (possibly with duplicates) or a `set` | a tuple: the dish name unchanged, then the `set` of that dish's ingredients that appear in `SPECIAL_INGREDIENTS` |

```python
bar = solve()

bar["check_drinks"]("Honeydew Cucumber", ["honeydew", "mint leaves", "lime juice"])
# -> "Honeydew Cucumber Mocktail"

bar["check_drinks"]("Shirley Tonic", ["ginger", "scotch", "club soda"])
# -> "Shirley Tonic Cocktail"

bar["tag_special_ingredients"](("Ginger Glazed Tofu Cutlets",
                               ["tofu", "soy sauce", "ginger", "garlic", "sesame seeds"]))
# -> ("Ginger Glazed Tofu Cutlets", {"tofu", "soy sauce", "garlic"})
```

## Rules
- the dict keys are exactly the two strings above, and each value is the function **itself** — `{"check_drinks": check_drinks}`, no parentheses
- `check_drinks` returns one string, with exactly one space before `Cocktail` / `Mocktail` and no other punctuation
- `tag_special_ingredients` takes the dish as a **single tuple argument**, not as two arguments — reach into it by index
- the second half of that returned tuple is a `set`, and it is empty (`set()`) when nothing on the dish needs a label

> [!WARNING]
> `Cocktail` and `Mocktail` are compared character for character. A drink with no alcohol is a `Mocktail`; only one alcoholic ingredient is needed to make it a `Cocktail`.

## Hints
### Hint 1
Neither function needs a loop over the ingredients. Python already knows how to ask a set "do you and this other collection have nothing in common?" and how to ask it "give me what we do have in common". One of those answers a `bool`, the other answers a `set` — which is exactly the difference between the two tasks here. Careful with the first one: it is worded as *disjoint*, so it says `True` when there is **no** alcohol.
### Hint 2
`check_drinks` — call the disjoint check on `ALCOHOLS` with the ingredient list as the argument (the method takes any iterable, so no conversion needed). It returns `True` when nothing overlaps, i.e. when the drink is a mocktail, so the branch you want first is the negated one, or swap which name you concatenate. Strings join with `+`, and remember the space.

`tag_special_ingredients` — the argument is one tuple. `dish[0]` is the name and `dish[1]` is the ingredients. Intersect `SPECIAL_INGREDIENTS` with `set(dish[1])` (the `&` operator wants sets on both sides; the `.intersection()` method would take the list directly), then return the name and that set separated by a comma.
### Hint 3
Different data, same two moves — auditing an IAM policy against a list of actions security has banned:

```python
BANNED = {"iam:PassRole", "s3:DeleteBucket", "ec2:TerminateInstances"}

def verdict(policy_name, actions):
    if not BANNED.isdisjoint(actions):
        return policy_name + " REJECTED"
    return policy_name + " APPROVED"

def offending(policy):
    return policy[0], BANNED & set(policy[1])

verdict("read-only", ["s3:GetObject"])                 # -> 'read-only APPROVED'
offending(("admin", ["s3:GetObject", "iam:PassRole"])) # -> ('admin', {'iam:PassRole'})
```

`isdisjoint` gives the yes/no, `&` gives the list to put in the report — and `offending` takes the policy as one tuple, so it has to index into it.
