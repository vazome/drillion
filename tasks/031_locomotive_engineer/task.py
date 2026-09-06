def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from copy import deepcopy

from _lib import rng

_CITIES = ["Berlin", "Hamburg", "Paris", "London", "Gothenburg", "Copenhagen",
           "New York", "Miami", "Lille", "Lund", "Malmo", "Atlanta", "Orlando"]
_DETAILS = [("timeOfArrival", "12:00"), ("precipitation", "10"),
            ("temperature", "5"), ("caboose", "yes"), ("length", "15"),
            ("speed", "50"), ("cargo", "grain")]
_COLORS = ["red", "blue", "orange", "green", "yellow", "pink", "purple",
           "black", "white"]


def _gen(r):
    origin, destination = r.sample(_CITIES, 2)
    route = {"from": origin, "to": destination}
    stops = {f"stop_{number}": city
             for number, city in enumerate(r.sample(_CITIES, r.randint(0, 5)),
                                           start=1)}
    more_information = dict(r.sample(_DETAILS, r.randint(1, 4)))
    colors = r.sample(_COLORS, 3)
    ids = r.sample(range(2, 40), 9)
    depot = [[(ids[row * 3 + column], colors[row]) for column in range(3)]
             for row in range(3)]
    return route, stops, more_information, depot


def _reference():
    def add_missing_stops(route, **kwargs):
        return {**route, "stops": list(kwargs.values())}

    def extend_route_information(route, more_route_information):
        return {**route, **more_route_information}

    def fix_wagon_depot(wagons_rows):
        [*row_one], [*row_two], [*row_three] = zip(*wagons_rows)
        return [row_one, row_two, row_three]

    return {"add_missing_stops": add_missing_stops,
            "extend_route_information": extend_route_information,
            "fix_wagon_depot": fix_wagon_depot}


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    for _ in range(6):
        route, stops, more_information, depot = _gen(r)
        assert (got["add_missing_stops"](dict(route), **stops)
                == want["add_missing_stops"](dict(route), **stops)), \
            f"add_missing_stops({route!r}, {stops!r})"
        assert (got["extend_route_information"](dict(route),
                                                dict(more_information))
                == want["extend_route_information"](dict(route),
                                                    dict(more_information))), \
            f"extend_route_information({route!r}, {more_information!r})"
        assert (got["fix_wagon_depot"](deepcopy(depot))
                == want["fix_wagon_depot"](deepcopy(depot))), \
            f"fix_wagon_depot({depot!r})"

    # canonical cases from exercism's locomotive_engineer_test.py
    assert got["add_missing_stops"](
        {"from": "Berlin", "to": "Hamburg"},
        stop_1="Lepzig", stop_2="Hannover", stop_3="Frankfurt") == {
            "from": "Berlin", "to": "Hamburg",
            "stops": ["Lepzig", "Hannover", "Frankfurt"]}
    assert got["add_missing_stops"]({"from": "New York",
                                     "to": "Philadelphia"}) == {
        "from": "New York", "to": "Philadelphia", "stops": []}
    assert got["extend_route_information"](
        {"from": "Berlin", "to": "Hamburg"},
        {"timeOfArrival": "12:00", "precipitation": "10", "temperature": "5",
         "caboose": "yes"}) == {
            "from": "Berlin", "to": "Hamburg", "timeOfArrival": "12:00",
            "precipitation": "10", "temperature": "5", "caboose": "yes"}
    assert got["extend_route_information"](
        {"from": "Paris", "to": "London"},
        {"timeOfArrival": "10:30", "temperature": "20", "length": "15"}) == {
            "from": "Paris", "to": "London", "timeOfArrival": "10:30",
            "temperature": "20", "length": "15"}
    assert got["fix_wagon_depot"](
        [[(2, "red"), (4, "red"), (8, "red")],
         [(5, "blue"), (9, "blue"), (13, "blue")],
         [(3, "orange"), (7, "orange"), (11, "orange")]]) == [
            [(2, "red"), (5, "blue"), (3, "orange")],
            [(4, "red"), (9, "blue"), (7, "orange")],
            [(8, "red"), (13, "blue"), (11, "orange")]]
    assert got["fix_wagon_depot"](
        [[(7, "pink"), (4, "pink"), (2, "pink")],
         [(10, "green"), (6, "green"), (14, "green")],
         [(9, "yellow"), (5, "yellow"), (13, "yellow")]]) == [
            [(7, "pink"), (10, "green"), (9, "yellow")],
            [(4, "pink"), (6, "green"), (5, "yellow")],
            [(2, "pink"), (14, "green"), (13, "yellow")]]
