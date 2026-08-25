"""Constants and small functions — the shape every Python module has."""
# SOURCE: exercism/python concept/guidos-gorgeous-lasagna (MIT, adapted)
# READ FIRST:
#   https://lerner.co.il/2019/06/18/understanding-python-assignment/  — what `name = value`
#       actually binds, and why SCREAMING_SNAKE_CASE is a promise to yourself, not a lock
#   https://docs.python.org/3/tutorial/controlflow.html#defining-functions  — def, parameters,
#       return, and what a function hands back when you forget to return anything
#   CONCEPT: basics — naming values, defining functions, comments and docstrings; internally
#       everything in Python is an object, functions included.

from _lib import rng

META = {"topic": 200, "title": "basics — Guido's lasagna kitchen timer", "minutes": 12,
        "prereqs": [], "tags": ["exercism", "basics", "core"]}


def solve():
    """WHY: You are writing the kitchen timer for a recipe app. The cook opens
    the lasagna recipe, tells the app how many layers they are building and how
    long the dish has already been in the oven, and the app has to answer two
    questions: "how much longer does it bake?" and "how long have I been at
    this?". The cookbook numbers never change — 40 minutes in the oven, 2
    minutes of work per layer — so they belong in named constants at the top of
    the file, not copy-pasted into every calculation. That is the whole habit
    this drill is about.

    YOU GET: nothing. You define the numbers and the functions yourself.

    YOU RETURN: a dict with these four entries, wired to your own code.

      "EXPECTED_BAKE_TIME" — the plain number 40: how many minutes the cookbook
      says the lasagna spends in the oven, start to finish.

      "bake_time_remaining" — a function taking `elapsed_bake_time` (minutes
      already spent in the oven, e.g. 30) and returning how many minutes of
      baking are still to go.

      "preparation_time_in_minutes" — a function taking `number_of_layers`
      (e.g. 2) and returning the minutes of layering work, at 2 minutes a layer.

      "elapsed_time_in_minutes" — a function taking `number_of_layers` and
      `elapsed_bake_time` and returning the total minutes spent in the kitchen:
      the layering work plus the baking done so far.

    ─── exact rules ───
    Every input is a whole number of minutes or layers; every function returns
    a number. The dict keys are exactly the four strings above.

        bake_time_remaining(30)          ->  10   (40 - 30)
        preparation_time_in_minutes(2)   ->   4   (2 layers x 2 minutes)
        elapsed_time_in_minutes(3, 20)   ->  26   (3 x 2 of prep, plus 20 baked)

    Nobody bakes past the cookbook time, so `bake_time_remaining` never has to
    deal with a negative answer.
    """
    raise NotImplementedError


HINTS = [
    ("Two numbers in this recipe never change: 40 and 2. Bind each to a name once, "
    "above the functions, and let the functions read those names. The third function "
    "does not need to redo the per-layer arithmetic — one of your other functions "
    "already knows how to do it."),
    ("Shape of the work: define the two constants, then define the three functions, "
    "then build the dict that maps each key string to the matching function. Put the "
    "function name in the dict WITHOUT parentheses — `{'bake_time_remaining': "
    "bake_time_remaining}` hands over the function itself so the caller can run it "
    "later; adding `()` would run it now, with no arguments, and store the result."),
    ("Different data, same shape. A car wash charges a fixed 15-minute wash plus 3 "
    "minutes per extra service:\n"
    "    WASH_TIME = 15\n"
    "    PER_EXTRA = 3\n"
    "    def extras_time(extras):\n"
    "        return extras * PER_EXTRA\n"
    "    def total_time(extras):\n"
    "        return WASH_TIME + extras_time(extras)\n"
    "    def handles():\n"
    "        return {'WASH_TIME': WASH_TIME, 'total_time': total_time}\n"
    "`handles()['total_time'](2)` is 21. Note `total_time` reusing `extras_time` "
    "instead of writing `extras * 3` a second time."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    return r.randint(0, 40), r.randint(1, 25)


def _reference():
    EXPECTED_BAKE_TIME = 40
    PREPARATION_TIME = 2

    def bake_time_remaining(elapsed_bake_time):
        return EXPECTED_BAKE_TIME - elapsed_bake_time

    def preparation_time_in_minutes(number_of_layers):
        return number_of_layers * PREPARATION_TIME

    def elapsed_time_in_minutes(number_of_layers, elapsed_bake_time):
        return preparation_time_in_minutes(number_of_layers) + elapsed_bake_time

    return {"EXPECTED_BAKE_TIME": EXPECTED_BAKE_TIME,
            "bake_time_remaining": bake_time_remaining,
            "preparation_time_in_minutes": preparation_time_in_minutes,
            "elapsed_time_in_minutes": elapsed_time_in_minutes}


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    assert got["EXPECTED_BAKE_TIME"] == want["EXPECTED_BAKE_TIME"]
    for _ in range(5):
        elapsed, layers = _gen(r)
        assert got["bake_time_remaining"](elapsed) == want["bake_time_remaining"](elapsed)
        assert (got["preparation_time_in_minutes"](layers)
                == want["preparation_time_in_minutes"](layers))
        assert (got["elapsed_time_in_minutes"](layers, elapsed)
                == want["elapsed_time_in_minutes"](layers, elapsed))

    # canonical cases from exercism's lasagna_test.py + instructions.md
    assert got["EXPECTED_BAKE_TIME"] == 40
    for elapsed, expected in [(1, 39), (23, 17), (33, 7)]:
        assert got["bake_time_remaining"](elapsed) == expected
    for layers, expected in [(2, 4), (11, 22), (15, 30)]:
        assert got["preparation_time_in_minutes"](layers) == expected
    for layers, elapsed, expected in [(1, 3, 5), (3, 20, 26), (11, 15, 37)]:
        assert got["elapsed_time_in_minutes"](layers, elapsed) == expected
