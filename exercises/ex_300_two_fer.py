"""two-fer — one line of dialogue, and the argument the caller often forgets."""
# SOURCE: exercism/python practice/two-fer (MIT, adapted)
# READ FIRST:
#   https://docs.python.org/3/tutorial/controlflow.html#default-argument-values  — a parameter
#       with a default value: what happens when the caller passes nothing
#   https://www.pythonmorsels.com/positional-vs-keyword-arguments/  — the vocabulary an
#       interviewer uses: positional, keyword, default
#   https://realpython.com/defining-your-own-python-function/  — the whole def statement

from _lib import rng

META = {"topic": 300, "title": "two-fer — the bakery's one-for-you line", "minutes": 10,
        "prereqs": [200, 245], "tags": ["exercism", "function-arguments", "core"]}


def solve(name="you"):
    """WHY: A bakery runs a two-for-one offer on cookies, and customers keep
    handing the free one to the next person in the queue. The till prints a
    little line for them to say. Sometimes the till knows who the customer
    is (the loyalty card has a name on it) and sometimes it does not — and
    the line still has to come out right either way. That "sometimes there
    is no value" is the whole exercise: it is the same problem as a config
    option nobody set, or a CLI flag nobody passed.

    YOU GET: `name` — the person's name as a string, e.g. "Alice". The
    caller may leave the argument out completely: `solve()` is a legal call
    and the test makes it.

    YOU RETURN: one string — the line to say.

    ─── exact rules ───
    The line is `One for <name>, one for me.` — capital O, one comma, a full
    stop at the end. When no name is given, the word `you` stands in its
    place. The name is used exactly as handed to you: no capitalising, no
    trimming.

        solve("Alice")   ->  "One for Alice, one for me."
        solve("Bohdan")  ->  "One for Bohdan, one for me."
        solve()          ->  "One for you, one for me."
    """
    raise NotImplementedError


HINTS = [
    ("There is one sentence with one blank in it, so the only real question is "
    "what fills the blank when the caller hands you nothing at all. You do not "
    "need an `if` inside the function to answer that — the `def` line itself can."),
    ("A parameter written `def f(x=<value>)` uses <value> whenever the caller "
    "omits that argument. Pick the stand-in word as the parameter's default, "
    "then build the sentence with a single f-string that drops the parameter in."),
    ("Different data, same shape:\n"
    "    def greet(city='here'):\n"
    "        return f'Welcome to {city}!'\n"
    "    greet('Oslo')  ->  'Welcome to Oslo!'\n"
    "    greet()        ->  'Welcome to here!'\n"
    "One function, two call styles, no branching."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    first = ["Alice", "Bohdan", "Zaphod", "Do-yun", "Mei", "Olamide", "Ingrid", "Rafa"]
    last = ["Ngo", "Ferrer", "O'Neill", "Adeyemi", "Kowalski"]
    name = r.choice(first)
    if r.random() < 0.4:
        name = f"{name} {r.choice(last)}"
    return name


def _reference(name="you"):
    return f"One for {name}, one for me."


def test_solve():
    r = rng()
    for _ in range(5):
        name = _gen(r)
        assert solve(name) == _reference(name), f"name {name!r}"

    # canonical cases (exercism/python practice/two-fer)
    assert solve() == "One for you, one for me."
    assert solve("Alice") == "One for Alice, one for me."
    assert solve("Bob") == "One for Bob, one for me."
