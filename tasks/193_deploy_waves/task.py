def solve(graph: dict[str, list[str]]):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _reference(graph):
    from collections import defaultdict, deque

    waiting = {service: len(deps) for service, deps in graph.items()}
    unlocks = defaultdict(list)
    for service, deps in graph.items():
        for dependency in deps:
            unlocks[dependency].append(service)

    ready = deque(sorted(service for service, count in waiting.items() if count == 0))
    waves = []
    while ready:
        wave = list(ready)
        ready.clear()
        waves.append(wave)
        next_wave = []
        for service in wave:
            for unlocked in unlocks[service]:
                waiting[unlocked] -= 1
                if waiting[unlocked] == 0:
                    next_wave.append(unlocked)
        ready.extend(sorted(next_wave))
    return waves if sum(map(len, waves)) == len(graph) else []


def _gen(r):
    names = r.sample(["db", "cache", "api", "web", "jobs", "mail", "metrics"], r.randint(4, 7))
    graph = {name: r.sample(names[:index], min(index, r.randint(0, 2)))
             for index, name in enumerate(names)}
    if r.random() < 0.35 and len(names) > 1:
        graph[names[0]] = [names[-1]]
    items = list(graph.items())
    r.shuffle(items)
    return dict(items)


def test_solve():
    assert solve({"db": [], "api": ["db"], "web": ["api"], "jobs": ["db"]}) == [
        ["db"], ["api", "jobs"], ["web"]]
    assert solve({"a": ["b"], "b": ["a"]}) == []
    r = rng()
    for _ in range(6):
        graph = _gen(r)
        assert solve({key: list(value) for key, value in graph.items()}) == _reference(graph)
