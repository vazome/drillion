"""and / or / not — four arcade-game rules built from booleans alone."""
# SOURCE: exercism/python concept/ghost-gobble-arcade-game (MIT, adapted)
# READ FIRST:
#   https://docs.python.org/3/library/stdtypes.html#boolean-operations-and-or-not  — the three
#       operators, their precedence (not binds tightest, then and, then or)
#   https://docs.python.org/3/library/stdtypes.html#truth  — Truth Value Testing: why you never
#       need to write `if flag == True`
#   CONCEPT: bools — Python's True/False type, a subclass of int, combined with and / or / not.

from _lib import rng

META = {"topic": 203, "title": "bools — the Pac-Man rulebook", "minutes": 12,
        "prereqs": [200], "tags": ["exercism", "bools", "core"]}


def solve():
    """WHY: You have taken over the rules engine of an arcade game. The graphics
    team already worked out where everything is on screen; every frame they hand
    the rules engine a handful of yes/no facts — is a power pellet active, is
    the player touching a ghost, has the player eaten the last dot — and the
    engine has to say what that means for the game: did the player score, did
    they eat the ghost, did they lose, did they win. Nothing here is arithmetic.
    It is four sentences of English turned into and / or / not, which is most of
    what business rules ever are.

    YOU GET: nothing. Every fact arrives as an argument to one of your
    functions, and every fact is already a plain True or False — you never work
    out where anything is.

    YOU RETURN: a dict with these four functions, all returning True or False.

      "eat_ghost" — takes `power_pellet_active`, `touching_ghost`. The player
      eats a ghost only while a power pellet is active AND they are touching
      that ghost.

      "score" — takes `touching_power_pellet`, `touching_dot`. The player scores
      when they touch a power pellet or a dot; either one is enough.

      "lose" — takes `power_pellet_active`, `touching_ghost`. The player loses
      when they touch a ghost with no power pellet active.

      "win" — takes `has_eaten_all_dots`, `power_pellet_active`,
      `touching_ghost`. The player wins when every dot is eaten and they have
      not, at that same moment, lost by the rule above.

    ─── exact rules ───
    The dict keys are exactly the four strings above.

        eat_ghost(False, True)   ->  False  (touching a ghost, but no pellet)
        score(True, False)       ->  True   (a power pellet still counts)
        lose(True, True)         ->  False  (the pellet saves you)
        win(True, True, True)    ->  True   (all dots eaten, and not lost)
        win(True, False, True)   ->  False  (all dots eaten, but lost anyway)
    """
    raise NotImplementedError


HINTS = [
    ("Read each rule out loud and mark the joining word. 'active AND touching' is "
    "`and`; 'a pellet OR a dot' is `or`; 'with NO pellet' is `not`. Each function "
    "is a single return of the arguments combined that way — no if statement is "
    "needed, because comparing two bools with `and` already gives you a bool."),
    ("`win` is the interesting one: it is 'all dots eaten AND not lost'. You already "
    "wrote the losing rule as its own function, so call it rather than restating "
    "'touching a ghost without a pellet' a second time — that way one bug fix fixes "
    "both. Precedence: `not` binds tighter than `and`, so `not a and b` reads as "
    "`(not a) and b`; add parentheses whenever you have to stop and think about it."),
    ("Different data, same shape. A door lock: it opens when the badge is valid and "
    "the building is not in lockdown; it alarms when someone pushes the door while "
    "it is not open.\n"
    "    def opens(badge_valid, lockdown):\n"
    "        return badge_valid and not lockdown\n"
    "    def alarms(pushed, badge_valid, lockdown):\n"
    "        return pushed and not opens(badge_valid, lockdown)\n"
    "`alarms` reuses `opens` instead of repeating its condition — that is exactly "
    "the relationship `win` has with the losing rule."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

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
