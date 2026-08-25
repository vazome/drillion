"""Closures capture variables, not values — the late-binding loop surprise."""

from _lib import rng

META = {"topic": 8, "title": "closures — late binding in a loop", "tier": 1,
        "minutes": 8, "prereqs": [], "tags": ["core"]}


def solve(n, x):
    """WHY: This is a classic interview question and a real production bug. You
    build a list of small callback functions in a loop, one per server, each
    meant to remember "its" server number, and hand them to a scheduler to
    run later. When they finally run, every one of them acts on the last
    server. Nothing crashes; the wrong machines get restarted. Interviewers
    ask you to predict the output and explain why the two ways of writing it
    give different answers.

    YOU GET: `n` — how many callbacks get built, a small number like 3.
    `x` — a number each callback multiplies by, like 10. The test creates
    them and hands them to you; you never build them yourself.

    YOU RETURN: a pair (late, frozen): the list of results from the naive
    callbacks, and the list of results from the callbacks built the safe way.
    You predict the numbers; you do not fix the snippet.

    ─── exact rules ───
    Predict what this produces — that is the whole exercise.

        gs = [lambda: x * i for i in range(n)]
        late = [g() for g in gs]

        def make(i):
            return lambda: x * i

        fs = [make(i) for i in range(n)]
        frozen = [f() for f in fs]

    Return the tuple (late, frozen).

        n=3, x=10  ->  ([20, 20, 20], [0, 10, 20])

    n varies, so you must generalise, not memorise the example. Paste the
    snippet into a REPL if the result surprises you — then make sure you
    can say out loud WHY the two lists differ. That sentence is what the
    interviewer is after.
    """
    raise NotImplementedError


HINTS = [
    ("A closure keeps a reference to the variable itself, not a snapshot of "
    "its value. So ask two questions: when each lambda finally runs, which "
    "`i` is it looking at — and what does that `i` hold by then?"),
    ("The naive lambdas all share the single loop variable and only read it "
    "when called — after the loop it holds its final value, so every call "
    "sees the same i. Each make(i) call opens a fresh scope, so each "
    "returned lambda owns its own i. Build late from the final i, frozen "
    "from each i in turn."),
    ("Different data, same surprise:\n"
    "    fs = [lambda: c for c in 'abc']\n"
    "    print([f() for f in fs])      # ['c', 'c', 'c']\n"
    "\n"
    "    def hold(c):\n"
    "        return lambda: c\n"
    "\n"
    "    gs = [hold(c) for c in 'abc']\n"
    "    print([g() for g in gs])      # ['a', 'b', 'c']\n"
    "The no-factory fix is a default arg, lambda c=c: c — defaults are "
    "evaluated at definition time, the topic-7 trap used for good."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    return r.randint(3, 7), r.randint(2, 12)


def _reference(n, x):
    gs = [lambda: x * i for i in range(n)]  # noqa: B023 — late binding is the point
    late = [g() for g in gs]

    def make(i):
        return lambda: x * i

    fs = [make(i) for i in range(n)]
    frozen = [f() for f in fs]
    return (late, frozen)


def test_solve():
    r = rng()
    for _ in range(4):
        n, x = _gen(r)
        assert solve(n, x) == _reference(n, x)
