"""The mutable default argument — Python's most-asked trap question."""

from _lib import rng

META = {"topic": 7, "title": "mutable default — predict the leak", "tier": 1,
        "minutes": 8, "prereqs": []}


def solve(tasks):
    """WHY: This is a classic interview question and a real production bug. A
    helper function keeps a "done" list as a default argument so callers can
    skip passing one. In production a task runner calls it once per job, and
    after a while every job report lists every job that ever ran, because the
    default list is shared between calls and never reset. Nothing crashes;
    the reports are just wrong. Interviewers ask you to predict the output
    and explain why it happens.

    YOU GET: `tasks` — a list of job names like ["a", "b", "c"], never empty.
    The test creates it and hands it to you; you never build it yourself.

    YOU RETURN: a pair (buggy, fixed): the list the buggy function returns on
    its last call, and the list the safe version would return on its last
    call. You predict; you do not repair the function.

    ─── exact rules ───
    Predict, do not fix. This function is buggy on purpose:

        def add(task, done=[]):
            done.append(task)
            return done

    It is called once per item in `tasks`, always WITHOUT the second
    argument:

        for t in tasks:
            result = add(t)

    Return a tuple (buggy, fixed):

        buggy — the list the LAST call returns, exactly as written above
        fixed — what the last call would return if the default were done
                the safe way (done=None, make a fresh [] inside)

        ["a", "b", "c"]  ->  (["a", "b", "c"], ["c"])

    tasks is never empty. Work it out on paper first — saying WHY the
    buggy one remembers earlier calls is the interview answer.
    """
    raise NotImplementedError


HINTS = [
    ("Default values are evaluated ONCE, when the def line runs — not on "
    "every call. A mutable default is therefore one shared object that "
    "quietly survives from call to call. That single fact is the whole bug."),
    ("Trace it: call 1 appends to the shared list, call 2 appends to that "
    "SAME list, and so on — so the last call returns everything appended so "
    "far. The fixed version builds a new list per call, so the last call "
    "returns exactly one item. Return those two predictions as a tuple."),
    ("Different data, same leak:\n"
    "    def log(msg, seen=[]):\n"
    "        seen.append(msg)\n"
    "        return seen\n"
    "\n"
    "    print(log('boot'))    # ['boot']\n"
    "    print(log('ready'))   # ['boot', 'ready']  <- remembered\n"
    "The safe idiom is seen=None, then `if seen is None: seen = []` inside — "
    "say that sentence out loud in the interview."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    pool = ["deploy", "migrate", "backup", "rotate", "scale", "purge", "sync"]
    return r.sample(pool, r.randint(2, 5))


def _reference(tasks):
    def add(task, done=[]):  # noqa: B006 — the bug under study
        done.append(task)
        return done

    def add_fixed(task, done=None):
        if done is None:
            done = []
        done.append(task)
        return done

    for t in tasks:
        buggy = add(t)
    for t in tasks:
        fixed = add_fixed(t)
    return (list(buggy), fixed)


def test_solve():
    r = rng()
    for _ in range(4):
        tasks = _gen(r)
        assert solve(list(tasks)) == _reference(tasks)
