def solve(graph: dict[str, list[object] | list[str]] | dict[str, list[str]]):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


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
