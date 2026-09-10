from collections import deque


def solve(calls, start, target):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from itertools import pairwise

from _lib import rng

_SERVICES = [
    "gateway",
    "auth",
    "billing",
    "ledger",
    "search",
    "profile",
    "notify",
    "audit",
    "archive",
]


def _gen(r):
    names = _SERVICES[: r.randint(6, 9)]
    calls = {name: [] for name in names}
    for name in names:
        others = [other for other in names if other != name]
        r.shuffle(others)
        calls[name] = sorted(others[: r.randint(0, 3)])
    return calls, r.choice(names), r.choice(names)


def _reference(calls, start, target):
    if start == target:
        return [start]
    seen = {start}
    queue = deque([[start]])
    while queue:
        path = queue.popleft()
        for nxt in calls[path[-1]]:
            if nxt == target:
                return [*path, nxt]
            if nxt not in seen:
                seen.add(nxt)
                queue.append([*path, nxt])
    return []


def _check(calls, start, target, got, want):
    where = f"{start} -> {target} in {calls}"
    assert isinstance(got, list), f"return a list of service names, got {got!r} for {where}"
    assert len(got) == len(want), f"expected {len(want)} names, got {got!r} for {where}"
    if not want:
        return
    assert got[0] == start, f"the chain has to start at {start}, got {got!r}"
    assert got[-1] == target, f"the chain has to end at {target}, got {got!r}"
    for here, nxt in pairwise(got):
        assert nxt in calls[here], f"{here} does not call {nxt}, in {got!r} for {where}"


def test_solve():
    r = rng()
    for _ in range(10):
        calls, start, target = _gen(r)
        _check(calls, start, target, solve(calls, start, target), _reference(calls, start, target))

    # the first route depth-first finds is four hops long; the shortest is one
    fixed = {
        "gateway": ["auth", "billing"],
        "auth": ["ledger"],
        "ledger": ["billing"],
        "billing": [],
    }
    assert solve(fixed, "gateway", "billing") == ["gateway", "billing"]
    assert solve(fixed, "gateway", "ledger") == ["gateway", "auth", "ledger"]
    assert solve(fixed, "billing", "gateway") == [], "billing calls nothing, so there is no chain"
    assert solve(fixed, "ledger", "ledger") == ["ledger"], "no hops needed to reach yourself"
