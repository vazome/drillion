from collections import Counter


def solve(dice: list[int], category: str) -> int:
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_CATEGORIES = (
    "YACHT",
    "ONES",
    "TWOS",
    "THREES",
    "FOURS",
    "FIVES",
    "SIXES",
    "FULL_HOUSE",
    "FOUR_OF_A_KIND",
    "LITTLE_STRAIGHT",
    "BIG_STRAIGHT",
    "CHOICE",
)
# the interesting throws are rare under uniform dice, so they are drawn on purpose
_SHAPES = ("uniform", "yacht", "full_house", "four", "little", "big")


def _gen(r):
    match r.choice(_SHAPES):
        case "yacht":
            dice = [r.randint(1, 6)] * 5
        case "full_house":
            a, b = r.sample(range(1, 7), 2)
            dice = [a] * 3 + [b] * 2
        case "four":
            a, b = r.sample(range(1, 7), 2)
            dice = [a] * 4 + [b]
        case "little":
            dice = [1, 2, 3, 4, 5]
        case "big":
            dice = [2, 3, 4, 5, 6]
        case _:
            dice = [r.randint(1, 6) for _ in range(5)]
    r.shuffle(dice)
    return dice, r.choice(_CATEGORIES)


def _reference(dice, category):
    counts = Counter(dice)
    top, how_many = counts.most_common(1)[0]
    match category:
        case "YACHT":
            return 50 if how_many == 5 else 0
        case "ONES" | "TWOS" | "THREES" | "FOURS" | "FIVES" | "SIXES":
            face = _CATEGORIES.index(category)
            return face * counts[face]
        case "FULL_HOUSE":
            return sum(dice) if sorted(counts.values()) == [2, 3] else 0
        case "FOUR_OF_A_KIND":
            return top * 4 if how_many >= 4 else 0
        case "LITTLE_STRAIGHT":
            return 30 if sorted(dice) == [1, 2, 3, 4, 5] else 0
        case "BIG_STRAIGHT":
            return 30 if sorted(dice) == [2, 3, 4, 5, 6] else 0
        case _:
            return sum(dice)


def test_solve():
    r = rng()
    cases = [
        ([5, 5, 5, 5, 5], "YACHT"),
        ([1, 3, 3, 2, 5], "YACHT"),
        ([1, 1, 1, 3, 5], "ONES"),
        ([4, 3, 6, 5, 5], "FIVES"),
        ([2, 2, 4, 4, 4], "FULL_HOUSE"),
        ([2, 2, 2, 2, 2], "FULL_HOUSE"),  # five of a kind is not a full house
        ([6, 6, 6, 6, 3], "FOUR_OF_A_KIND"),
        ([3, 3, 3, 3, 3], "FOUR_OF_A_KIND"),  # but five of a kind is four of a kind
        ([3, 5, 4, 1, 2], "LITTLE_STRAIGHT"),
        ([1, 2, 3, 4, 5], "BIG_STRAIGHT"),
        ([3, 3, 5, 6, 6], "CHOICE"),
    ]
    cases += [_gen(r) for _ in range(60)]
    for dice, category in cases:
        want = _reference(list(dice), category)
        assert solve(list(dice), category) == want, f"{category} on {dice} scores {want}"
