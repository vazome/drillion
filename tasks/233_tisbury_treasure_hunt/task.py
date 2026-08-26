def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_TREASURES = ["Amethyst Octopus", "Angry Monkey Figurine",
              "Antique Glass Fishnet Float", "Brass Spyglass",
              "Carved Wooden Elephant", "Crystal Crab", "Glass Starfish",
              "Model Ship in Large Bottle", "Pirate Flag", "Robot Parrot",
              "Scrimshawed Whale Tooth", "Silver Seahorse", "Vintage Pirate Hat"]


def _gen(r):
    coordinate = f"{r.randint(1, 8)}{r.choice('ABCDEF')}"
    return r.choice(_TREASURES), coordinate


def _reference():
    def get_coordinate(record):
        return record[1]

    def convert_coordinate(coordinate):
        return tuple(coordinate)

    return {"get_coordinate": get_coordinate,
            "convert_coordinate": convert_coordinate}


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    for _ in range(6):
        record = _gen(r)
        assert (got["get_coordinate"](record)
                == want["get_coordinate"](record)), f"get_coordinate({record!r})"
        coordinate = record[1]
        assert (got["convert_coordinate"](coordinate)
                == want["convert_coordinate"](coordinate)), \
            f"convert_coordinate({coordinate!r})"

    # canonical cases from exercism's tuples_test.py
    for record, expected in [(("Scrimshawed Whale Tooth", "2A"), "2A"),
                             (("Brass Spyglass", "4B"), "4B"),
                             (("Robot Parrot", "1C"), "1C"),
                             (("Model Ship in Large Bottle", "8A"), "8A")]:
        assert got["get_coordinate"](record) == expected
    for coordinate, expected in [("2A", ("2", "A")), ("6D", ("6", "D")),
                                 ("7F", ("7", "F")), ("8C", ("8", "C"))]:
        assert got["convert_coordinate"](coordinate) == expected
