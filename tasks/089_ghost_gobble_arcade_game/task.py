def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    return tuple(r.choice([True, False]) for _ in range(5))


def _reference():
    def eat_ghost(power_pellet_active, touching_ghost):
        return power_pellet_active and touching_ghost

    def score(touching_power_pellet, touching_dot):
        return touching_power_pellet or touching_dot

    def lose(power_pellet_active, touching_ghost):
        return not power_pellet_active and touching_ghost

    def win(has_eaten_all_dots, power_pellet_active, touching_ghost):
        return has_eaten_all_dots and not lose(power_pellet_active, touching_ghost)

    return {"eat_ghost": eat_ghost, "score": score, "lose": lose, "win": win}


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    for _ in range(6):
        pellet, ghost, on_pellet, on_dot, all_dots = _gen(r)
        assert got["eat_ghost"](pellet, ghost) == want["eat_ghost"](pellet, ghost)
        assert got["score"](on_pellet, on_dot) == want["score"](on_pellet, on_dot)
        assert got["lose"](pellet, ghost) == want["lose"](pellet, ghost)
        assert (got["win"](all_dots, pellet, ghost)
                == want["win"](all_dots, pellet, ghost))

    # canonical cases from exercism's arcade_game_test.py
    for pellet, ghost, expected in [(True, True, True), (False, True, False),
                                    (True, False, False)]:
        assert got["eat_ghost"](pellet, ghost) == expected
    for on_pellet, on_dot, expected in [(False, True, True), (True, False, True),
                                        (False, False, False)]:
        assert got["score"](on_pellet, on_dot) == expected
    for pellet, ghost, expected in [(False, True, True), (True, True, False),
                                    (True, False, False)]:
        assert got["lose"](pellet, ghost) == expected
    for all_dots, pellet, ghost, expected in [(True, False, False, True),
                                              (True, False, True, False),
                                              (True, True, True, True),
                                              (False, True, True, False)]:
        assert got["win"](all_dots, pellet, ghost) == expected
