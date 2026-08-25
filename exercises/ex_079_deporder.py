"""Whole-task drill: what order do these services start in, and is it even possible.

Combines topics 18 (dict lookups), 20 (defaultdict grouping), 22 (sets).
"""

from _lib import rng

META = {"topic": 79, "title": "DRILL: start-up order, or the cycle that blocks it",
        "tier": 4, "minutes": 35, "prereqs": [20],
        "practices": [18, 20, 22]}


def solve(graph):
    """WHY: A platform has many services, and some cannot start until others
    are already running: the API needs the database, the cache needs the
    database, and so on. After a full outage someone has to bring everything
    back up in an order that works. If two services each wait for the other,
    nothing can start at all, and the team needs to know that before they
    try.

    YOU GET: `graph` — a dictionary where each key is a service name and its
    value is a list of the services it needs running first, like {"api":
    ["db", "cache"], "cache": ["db"], "db": []}. The test builds it and
    hands it to you.

    YOU RETURN: a dictionary with two keys: "cycle" (True when services wait
    on each other in a loop, otherwise False) and "order" (a list of service
    names in a start-up order that works, or an empty list when there is a
    cycle).

    ─── exact rules ───
    `graph` maps a service to the services it depends on:

        {"api": ["db", "cache"], "cache": ["db"], "db": []}

    Everything a service depends on has to be running before it starts.
    Return an order that respects that:

        {"cycle": False, "order": ["db", "cache", "api"]}

    Any order that satisfies the dependencies is accepted — the test
    checks the constraints, not one fixed list.

    If the dependencies loop, nothing can start at all:

        {"a": ["b"], "b": ["a"]}  ->  {"cycle": True, "order": []}

    Guarantees: every name used as a dependency is also a key, no
    duplicates in a dependency list, and a service with nothing to wait
    for has [].

    This is a topological sort, but do not lead with the term. Describe
    what you are doing — repeatedly start whatever is unblocked — and say
    where the cycle shows up. Out loud.
    """
    raise NotImplementedError


HINTS = [
    ("One algorithm answers both questions. Repeatedly take any service whose "
    "dependencies are all started already, mark it started, and see what that "
    "unblocks. If you run out of unblocked services with some still left "
    "over, the leftovers are waiting on each other — that is the cycle, and "
    "you get it for free. No separate cycle hunt."),
    ("Kahn's algorithm. Two structures: unmet[svc] = how many dependencies it "
    "is still waiting on, and a reverse map unblocks = defaultdict(list) "
    "where unblocks[dep] lists the services that were waiting on dep. Seed a "
    "queue with every service at zero, pop one, append it to the order, "
    "decrement each of its dependents, push the ones that hit zero. At the "
    "end, len(order) != len(graph) means a cycle."),
    ("Different data, whole shape:\n"
    "    from collections import defaultdict, deque\n"
    "    needs = {'cake': ['eggs', 'flour'], 'eggs': [], 'flour': []}\n"
    "    unmet = {k: len(v) for k, v in needs.items()}\n"
    "    unblocks = defaultdict(list)\n"
    "    for item, parts in needs.items():\n"
    "        for p in parts:\n"
    "            unblocks[p].append(item)\n"
    "    ready = deque(k for k, n in unmet.items() if n == 0)\n"
    "    order = []\n"
    "    while ready:\n"
    "        item = ready.popleft()\n"
    "        order.append(item)\n"
    "        for nxt in unblocks[item]:\n"
    "            unmet[nxt] -= 1\n"
    "            if unmet[nxt] == 0:\n"
    "                ready.append(nxt)\n"
    "    print(order)      # ['eggs', 'flour', 'cake']\n"
    "Add the leftover check and the two return shapes and you are done."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    names = r.sample(["api", "auth", "db", "cache", "queue", "web", "worker",
                      "search", "mail"], r.randint(4, 7))
    graph = {}
    for i, svc in enumerate(names):
        # a service may only depend on names earlier in the list: no cycles yet
        graph[svc] = r.sample(names[:i], min(i, r.randint(0, 2)))
    if r.random() < 0.4:
        # close a loop: pick a service, walk down its deps, point the last
        # one back at it
        starts = [s for s, deps in graph.items() if deps]
        if starts:
            head = r.choice(starts)
            tail = r.choice(graph[head])
            if graph[tail] and r.random() < 0.5:
                tail = r.choice(graph[tail])     # longer loop when possible
            graph[tail] = sorted(set(graph[tail] + [head]))
    items = list(graph.items())
    r.shuffle(items)
    return dict(items)


def _reference(graph):
    from collections import defaultdict, deque
    unmet = {svc: len(deps) for svc, deps in graph.items()}
    unblocks = defaultdict(list)
    for svc, deps in graph.items():
        for dep in deps:
            unblocks[dep].append(svc)
    ready = deque(sorted(svc for svc, n in unmet.items() if n == 0))
    order = []
    while ready:
        svc = ready.popleft()
        order.append(svc)
        for nxt in unblocks[svc]:
            unmet[nxt] -= 1
            if unmet[nxt] == 0:
                ready.append(nxt)
    if len(order) != len(graph):
        return {"cycle": True, "order": []}
    return {"cycle": False, "order": order}


def _valid(graph, out):
    """Any order is fine as long as it starts everything, once, in a legal order."""
    if out["cycle"]:
        return list(out["order"]) == []
    order = list(out["order"])
    if sorted(order) != sorted(graph):
        return False
    at = {svc: i for i, svc in enumerate(order)}
    return all(at[dep] < at[svc] for svc, deps in graph.items() for dep in deps)


def test_solve():
    r = rng()
    for _ in range(5):
        graph = _gen(r)
        got = solve({k: list(v) for k, v in graph.items()})
        assert got["cycle"] == _reference(graph)["cycle"]
        assert _valid(graph, got)
