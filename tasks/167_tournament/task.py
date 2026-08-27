def solve(results: list[object] | list[str]):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

HEADER = "Team                           | MP |  W |  D |  L |  P"
TEAMS = ["Allegoric Alaskans", "Blithering Badgers", "Courageous Californians",
         "Devastating Donkeys", "Erratic Emus", "Flustered Flamingos",
         "Grumbling Gnus", "Hapless Hedgehogs", "Idle Iguanas", "Jubilant Jackals"]


def _gen(r):
    teams = r.sample(TEAMS, r.randint(2, 5))
    lines = []
    for _ in range(r.randint(0, 10)):
        home, away = r.sample(teams, 2)
        lines.append(f"{home};{away};{r.choice(['win', 'loss', 'draw'])}")
    return lines


def _reference(results):
    tally = {}
    for line in results:
        home, away, outcome = line.split(";")
        for team in (home, away):
            tally.setdefault(team, [0, 0, 0])   # wins, draws, losses
        if outcome == "draw":
            tally[home][1] += 1
            tally[away][1] += 1
        else:
            winner, loser = (home, away) if outcome == "win" else (away, home)
            tally[winner][0] += 1
            tally[loser][2] += 1

    def points(record):
        return record[0] * 3 + record[1]

    table = [HEADER]
    for team, record in sorted(tally.items(), key=lambda kv: (-points(kv[1]), kv[0])):
        wins, draws, losses = record
        table.append(f"{team:30} | {sum(record):2} | {wins:2} | {draws:2} |"
                     f" {losses:2} | {points(record):2}")
    return table


def test_solve():
    r = rng()
    for _ in range(5):
        results = _gen(r)
        assert solve(results) == _reference(results), f"results {results!r}"

    # canonical cases (exercism/python practice/tournament)
    assert solve([]) == ["Team                           | MP |  W |  D |  L |  P"], \
        "just the header if no input"
    assert solve(["Allegoric Alaskans;Blithering Badgers;win"]) == [
        "Team                           | MP |  W |  D |  L |  P",
        "Allegoric Alaskans             |  1 |  1 |  0 |  0 |  3",
        "Blithering Badgers             |  1 |  0 |  0 |  1 |  0",
    ], "a win is three points, a loss is zero points"
    assert solve(["Allegoric Alaskans;Blithering Badgers;draw"]) == [
        "Team                           | MP |  W |  D |  L |  P",
        "Allegoric Alaskans             |  1 |  0 |  1 |  0 |  1",
        "Blithering Badgers             |  1 |  0 |  1 |  0 |  1",
    ], "a draw is one point each"
    assert solve([
        "Allegoric Alaskans;Blithering Badgers;win",
        "Devastating Donkeys;Courageous Californians;draw",
        "Devastating Donkeys;Allegoric Alaskans;win",
        "Courageous Californians;Blithering Badgers;loss",
        "Blithering Badgers;Devastating Donkeys;loss",
        "Allegoric Alaskans;Courageous Californians;win",
    ]) == [
        "Team                           | MP |  W |  D |  L |  P",
        "Devastating Donkeys            |  3 |  2 |  1 |  0 |  7",
        "Allegoric Alaskans             |  3 |  2 |  0 |  1 |  6",
        "Blithering Badgers             |  3 |  1 |  0 |  2 |  3",
        "Courageous Californians        |  3 |  0 |  1 |  2 |  1",
    ], "typical input"
    assert solve([
        "Courageous Californians;Devastating Donkeys;win",
        "Allegoric Alaskans;Blithering Badgers;win",
        "Devastating Donkeys;Allegoric Alaskans;loss",
        "Courageous Californians;Blithering Badgers;win",
        "Blithering Badgers;Devastating Donkeys;draw",
        "Allegoric Alaskans;Courageous Californians;draw",
    ]) == [
        "Team                           | MP |  W |  D |  L |  P",
        "Allegoric Alaskans             |  3 |  2 |  1 |  0 |  7",
        "Courageous Californians        |  3 |  2 |  1 |  0 |  7",
        "Blithering Badgers             |  3 |  0 |  1 |  2 |  1",
        "Devastating Donkeys            |  3 |  0 |  1 |  2 |  1",
    ], "ties broken alphabetically"
    assert solve([
        "Devastating Donkeys;Blithering Badgers;win",
        "Devastating Donkeys;Blithering Badgers;win",
        "Devastating Donkeys;Blithering Badgers;win",
        "Devastating Donkeys;Blithering Badgers;win",
        "Blithering Badgers;Devastating Donkeys;win",
    ]) == [
        "Team                           | MP |  W |  D |  L |  P",
        "Devastating Donkeys            |  5 |  4 |  0 |  1 | 12",
        "Blithering Badgers             |  5 |  1 |  0 |  4 |  3",
    ], "points sorted numerically, not as text"
