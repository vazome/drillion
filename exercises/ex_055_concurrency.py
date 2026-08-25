"""Reaching for threads on CPU work is the wrong answer that ends a phone screen."""
# READ FIRST:
#   https://realpython.com/python-concurrency/  — threads vs processes vs asyncio, when each wins
#   https://docs.python.org/3/library/concurrency.html
#   TAKE-HOME: "why async here?"

from _lib import rng

META = {"topic": 55, "title": "threads vs processes vs async — pick one, say why",
        "tier": 3, "minutes": 8, "prereqs": [], "tags": ["concurrency", "rsample"]}


def solve(workloads):
    """WHY: A colleague brings you a list of jobs they want to speed up: resize
    8 images, call 40 APIs, poll 5000 sensors. Python has three ways to do
    several things at once, and picking the wrong one makes a job no faster
    or even slower. The team wants one simple rule written down so everyone
    picks consistently: heavy calculation gets separate processes, a modest
    number of network waits gets threads, a huge number of waits gets async.
    Interviewers ask for this rule and the reasons behind it.

    YOU GET: `workloads` — a list of dicts, each like {"kind": "io",
    "count": 40}, where kind is "io" (waiting on network or disk) or "cpu"
    (calculating) and count is how many things there are to do. The test
    creates it and hands it to you.

    YOU RETURN: a list of strings, one per workload, in the same order; each
    is "threads", "processes" or "async".

    ─── exact rules ───
    Pick the right concurrency tool for each workload.

    Each workload is a dict:

        {"kind": "io", "count": 40}     # 40 things to do, all waiting on I/O
        {"kind": "cpu", "count": 8}     # 8 things to do, all number crunching

    Return a list of labels, one per workload, in input order. Each
    label is "threads", "processes" or "async". The rule:

      - kind == "cpu"                 -> "processes"
      - kind == "io" and count < 100  -> "threads"
      - kind == "io" and count >= 100 -> "async"

        [{"kind": "cpu", "count": 8},
         {"kind": "io", "count": 12},
         {"kind": "io", "count": 5000}]
        ->  ["processes", "threads", "async"]

    The reasoning behind the rule, which is the part you actually get
    asked for:

    CPU work goes to processes because the GIL lets only one thread run
    Python bytecode at a time. Ten threads doing arithmetic finish no
    sooner than one. Separate processes each get their own interpreter
    and their own lock, so they genuinely run at once — you pay for it
    in startup time and in having to pickle whatever you send across.

    I/O work suits threads because a thread blocked on a socket holds
    the GIL for none of that time. Everything you already have works
    unchanged: requests, boto3, psycopg, all of it.

    Past a hundred or so concurrent operations, threads stop being
    cheap — each one is a real OS thread with its own stack, and the
    scheduler starts costing more than the work. An event loop runs
    thousands of waits on one thread. The catch is that every library
    in the path has to be async-aware; one blocking call inside a
    coroutine freezes the whole loop, which is why "just use async" is
    not automatically the right answer.
    """
    raise NotImplementedError


HINTS = [
    ("One fact carries most of this: the GIL means only one thread runs "
    "Python bytecode at a time, so threads buy you nothing while computing "
    "and everything while waiting. That settles the cpu case on its own. The "
    "count only enters the picture on the waiting side, where the question "
    "is how many threads is too many."),
    ("One pass over the list, one label appended per workload. Check the kind "
    "first — cpu has a single answer whatever the count is. Then one "
    ">= 100 test splits the io case in two. Mind the boundary the spec "
    "states: exactly 100 is async, not threads."),
    ("Different data — same two-level decision, sizing disk jobs:\n"
    "    jobs = [{'size': 5}, {'size': 40}, {'size': 40000}]\n"
    "    out = []\n"
    "    for j in jobs:\n"
    "        if j['size'] < 10:\n"
    "            out.append('small')\n"
    "        elif j['size'] < 1000:\n"
    "            out.append('medium')\n"
    "        else:\n"
    "            out.append('large')\n"
    "    print(out)       # ['small', 'medium', 'large']\n"
    "Yours branches on two fields rather than one: kind first, then count "
    "inside the io branch."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    workloads = []
    for _ in range(r.randint(4, 9)):
        kind = r.choice(["io", "io", "cpu"])
        count = r.choice([1, 2, 8, r.randint(3, 98), 99, 100, 101,
                          r.randint(100, 20000), r.randint(1, 5000)])
        workloads.append({"kind": kind, "count": count})
    # the boundary always shows up, so an off-by-one cannot slip through a seed
    for edge in ({"kind": "io", "count": 100}, {"kind": "io", "count": 99},
                 {"kind": "cpu", "count": r.randint(200, 900)}):
        workloads.insert(r.randint(0, len(workloads)), edge)
    return workloads


def _reference(workloads):
    labels = []
    for w in workloads:
        if w["kind"] == "cpu":
            labels.append("processes")
        elif w["count"] >= 100:
            labels.append("async")
        else:
            labels.append("threads")
    return labels


def test_solve():
    r = rng()
    for _ in range(4):
        workloads = _gen(r)
        assert solve(workloads) == _reference(workloads)
