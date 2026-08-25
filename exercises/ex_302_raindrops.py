"""raindrops — build a string from the factors a number has, with a fallback."""
# SOURCE: exercism/python practice/raindrops (MIT, adapted)
# READ FIRST:
#   https://docs.python.org/3/tutorial/controlflow.html#if-statements  — if / elif / else, and
#       why three separate ifs are not the same thing as one if/elif chain
#   https://docs.python.org/3/library/stdtypes.html#truth-value-testing  — an empty string is
#       falsy: that is how you ask "did I add anything?"
#   https://docs.python.org/3/library/functions.html#divmod  — `%` and divmod, the two ways to
#       ask for a remainder

from _lib import rng

META = {"topic": 302, "title": "raindrops — sounds for the factors 3, 5 and 7", "minutes": 10,
        "prereqs": [200, 203, 206, 209], "tags": ["exercism", "conditionals", "core"]}


def solve(number):
    """WHY: This is FizzBuzz in a raincoat, and interviewers still hand it
    out because most candidates trip on the same two things: that several
    rules can fire for the same number (so it is three questions, not one
    choice of three), and that the fallback only applies when none of them
    fired. Picture a rain gauge whose display plays a chime per factor and
    only prints the raw reading when there is nothing to chime about.

    YOU GET: `number` — a positive whole number, e.g. 28.

    YOU RETURN: a string. Either the chimes glued together, or the number
    written out as text.

    ─── exact rules ───
    Start with nothing. If the number divides evenly by 3, add "Pling"; by
    5, add "Plang"; by 7, add "Plong" — always in that order, and a number
    can add two or all three. If it divides by none of 3, 5 and 7, the
    answer is the number itself as a string.

        solve(28)   ->  "Plong"            (7 only)
        solve(30)   ->  "PlingPlang"       (3 and 5)
        solve(105)  ->  "PlingPlangPlong"  (3, 5 and 7)
        solve(34)   ->  "34"               (none of them)
    """
    raise NotImplementedError


HINTS = [
    ("Three independent yes/no questions, not one choice between three answers "
    "— 15 has to produce two words. So build the answer up as you go, and only "
    "at the very end decide whether anything was added to it."),
    ("Start with an empty string. Ask about 3, then 5, then 7, each with its own "
    "`if`, appending a word when the remainder is zero — that ordering of the "
    "ifs is what puts the words in the right order. Afterwards, if the string is "
    "still empty, return the number converted to text instead."),
    ("Different data, same shape — Unix permission strings:\n"
    "    out = ''\n"
    "    if readable:   out += 'r'\n"
    "    if writable:   out += 'w'\n"
    "    if executable: out += 'x'\n"
    "    return out or '-'\n"
    "Three separate ifs, one accumulator, and a fallback for 'nothing applied'."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    base = r.choice([1, 2, 3, 5, 7, 15, 21, 35, 105])
    return base * r.randrange(1, 40)


def _reference(number):
    sounds = "".join(word for factor, word in ((3, "Pling"), (5, "Plang"), (7, "Plong"))
                     if number % factor == 0)
    return sounds or str(number)


def test_solve():
    r = rng()
    for _ in range(6):
        number = _gen(r)
        assert solve(number) == _reference(number), f"number {number}"

    # canonical cases (exercism/python practice/raindrops)
    assert solve(1) == "1"
    assert solve(3) == "Pling"
    assert solve(15) == "PlingPlang"
    assert solve(21) == "PlingPlong"
    assert solve(52) == "52"
    assert solve(105) == "PlingPlangPlong"
