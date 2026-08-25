def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_TREASURES = ["Amethyst Octopus", "Angry Monkey Figurine",
              "Antique Glass Fishnet Float", "Brass Spyglass",
              "Carved Wooden Elephant", "Crystal Crab", "Glass Starfish",
              "Model Ship in Large Bottle", "Pirate Flag", "Robot Parrot",
              "Scrimshawed Whale Tooth", "Silver Seahorse", "Vintage Pirate Hat"]
_LOCATIONS = ["Seaside Cottages", "Aqua Lagoon (Island of Mystery)",
              "Deserted Docks", "Spiky Rocks", "Abandoned Lighthouse",
              "Hidden Spring (Island of Mystery)", "Stormy Breakwater",
              "Old Schooner", "Tangled Seaweed Patch",
              "Quiet Inlet (Island of Mystery)", "Harbor Managers Office",
              "Foggy Seacave"]
_QUADRANTS = ["Blue", "Yellow", "Purple", "Orange"]


def _coordinate(r):
    return f"{r.randint(1, 8)}{r.choice('ABCDEF')}"


def _gen(r):
    azara_record = (r.choice(_TREASURES), _coordinate(r))
    if r.random() < 0.5:
        coordinate = tuple(azara_record[1])
    else:
        coordinate = tuple(_coordinate(r))
    rui_record = (r.choice(_LOCATIONS), coordinate, r.choice(_QUADRANTS))
    group = tuple(
        (r.choice(_TREASURES), coord, r.choice(_LOCATIONS), tuple(coord),
         r.choice(_QUADRANTS))
        for coord in [_coordinate(r) for _ in range(r.randint(1, 5))])
    return azara_record, rui_record, group


def _reference():
    def compare_records(azara_record, rui_record):
        return tuple(azara_record[1]) in rui_record

    def create_record(azara_record, rui_record):
        if compare_records(azara_record, rui_record):
            return azara_record + rui_record
        return "not a match"

    def clean_up(combined_record_group):
        report = ""
        for item in combined_record_group:
            report += f"{(item[0], item[2], item[3], item[4])}\n"
        return report

    return {"compare_records": compare_records, "create_record": create_record,
            "clean_up": clean_up}


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    for _ in range(6):
        azara_record, rui_record, group = _gen(r)
        assert (got["compare_records"](azara_record, rui_record)
                == want["compare_records"](azara_record, rui_record)), \
            f"compare_records({azara_record!r}, {rui_record!r})"
        assert (got["create_record"](azara_record, rui_record)
                == want["create_record"](azara_record, rui_record)), \
            f"create_record({azara_record!r}, {rui_record!r})"
        assert got["clean_up"](group) == want["clean_up"](group), \
            f"clean_up({group!r})"

    # canonical cases from exercism's tuples_test.py
    assert got["compare_records"](("Scrimshawed Whale Tooth", "2A"),
                                  ("Deserted Docks", ("2", "A"), "Blue")) is True
    assert got["compare_records"](("Vintage Pirate Hat", "7E"),
                                  ("Quiet Inlet (Island of Mystery)",
                                   ("7", "E"), "Orange")) is True
    assert got["compare_records"](("Angry Monkey Figurine", "5B"),
                                  ("Aqua Lagoon (Island of Mystery)",
                                   ("1", "F"), "Yellow")) is False
    assert got["create_record"](
        ("Angry Monkey Figurine", "5B"),
        ("Stormy Breakwater", ("5", "B"), "Purple")) == (
            "Angry Monkey Figurine", "5B", "Stormy Breakwater",
            ("5", "B"), "Purple")
    assert got["create_record"](
        ("Brass Spyglass", "4B"),
        ("Spiky Rocks", ("3", "D"), "Yellow")) == "not a match"
    assert got["clean_up"]((
        ("Scrimshawed Whale Tooth", "2A", "Deserted Docks", ("2", "A"), "Blue"),
        ("Brass Spyglass", "4B", "Abandoned Lighthouse", ("4", "B"), "Blue"),
        ("Crystal Crab", "6A", "Old Schooner", ("6", "A"), "Purple"),
    )) == ("('Scrimshawed Whale Tooth', 'Deserted Docks', ('2', 'A'), 'Blue')\n"
           "('Brass Spyglass', 'Abandoned Lighthouse', ('4', 'B'), 'Blue')\n"
           "('Crystal Crab', 'Old Schooner', ('6', 'A'), 'Purple')\n")
