import graphlib


def solve(graph, completions):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_JOBS = ["extract", "clean", "enrich", "report", "notify", "archive", "audit"]


def _gen(r):
    names = _JOBS[: r.randint(4, 7)]
    graph = {}
    for i, name in enumerate(names):
        # predecessors only ever point backwards, so the graph is acyclic by construction
        pool = names[:i]
        graph[name] = set(r.sample(pool, min(len(pool), r.randint(0, 3))))
    if r.random() < 0.25:
        graph[names[0]] = {names[-1]}  # close a loop back to the front
        return graph, []
    done, order = set(), []
    while len(order) < len(names):
        ready = [n for n in names if n not in done and graph[n] <= done]
        pick = r.choice(ready)
        done.add(pick)
        order.append(pick)
    return graph, order


def _reference(graph, completions):
    ts = graphlib.TopologicalSorter(graph)
    try:
        ts.prepare()
    except graphlib.CycleError:
        return {"cycle": True, "initial": [], "unlocked": []}
    out = {"cycle": False, "initial": sorted(ts.get_ready()), "unlocked": []}
    for job in completions:
        ts.done(job)
        out["unlocked"].append(sorted(ts.get_ready()))
    return out


def test_solve():
    r = rng()
    seen_cycle = seen_multi = False
    for _ in range(24):
        graph, completions = _gen(r)
        got, want = solve(graph, completions), _reference(graph, completions)
        assert got == want, f"for graph={graph} completions={completions}: got {got}"
        assert set(got) == {"cycle", "initial", "unlocked"}, f"exactly three keys, got {sorted(got)}"
        assert got["cycle"] is want["cycle"], "cycle must be a real bool"
        if want["cycle"]:
            seen_cycle = True
        else:
            assert len(got["unlocked"]) == len(completions), "one entry per completion, even the empty ones"
            if any(len(preds) > 1 for preds in graph.values()):
                seen_multi = True
    assert seen_cycle and seen_multi, "generator should produce a cycle and a job with two dependencies"

    # api waits for two, so it is unlocked by the second of them and not by the first
    canonical = solve({"db": set(), "cache": set(), "api": {"db", "cache"}}, ["db", "cache", "api"])
    assert canonical == {"cycle": False, "initial": ["cache", "db"], "unlocked": [[], ["api"], []]}, canonical

    # the same graph, the other legal completion order: the unlock moves with it
    swapped = solve({"db": set(), "cache": set(), "api": {"db", "cache"}}, ["cache", "db", "api"])
    assert swapped["unlocked"] == [[], ["api"], []], swapped["unlocked"]

    assert solve({"a": {"b"}, "b": {"a"}}, []) == {"cycle": True, "initial": [], "unlocked": []}
