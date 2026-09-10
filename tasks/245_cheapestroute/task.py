import heapq


def solve(legs, start, target):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_DEPOTS = ["hamburg", "lyon", "porto", "gdansk", "turin", "cork", "malmo", "brno"]


def _gen(r):
    names = _DEPOTS[: r.randint(5, 8)]
    legs = {name: [] for name in names}
    for name in names:
        others = [other for other in names if other != name]
        r.shuffle(others)
        for other in others[: r.randint(1, 3)]:
            legs[name].append((other, r.randint(1, 30)))
    return {name: sorted(legs[name]) for name in names}, r.choice(names), r.choice(names)


def _reference(legs, start, target):
    settled = set()
    heap = [(0, start)]
    while heap:
        cost, here = heapq.heappop(heap)
        if here in settled:
            continue
        if here == target:
            return cost
        settled.add(here)
        for nxt, price in legs[here]:
            if nxt not in settled:
                heapq.heappush(heap, (cost + price, nxt))
    return None


def test_solve():
    r = rng()
    for _ in range(12):
        legs, start, target = _gen(r)
        got, want = solve(legs, start, target), _reference(legs, start, target)
        assert got == want, f"{start} -> {target} costs {want}, got {got!r}, in {legs}"

    # the one-leg route costs 10; two cheap legs get there for 2
    fixed = {
        "hamburg": [("lyon", 10), ("porto", 1)],
        "porto": [("lyon", 1)],
        "lyon": [("turin", 1)],
        "turin": [],
        "cork": [("hamburg", 4)],
    }
    assert solve(fixed, "hamburg", "lyon") == 2, "the cheap pair of legs beats the direct one"
    assert solve(fixed, "hamburg", "turin") == 3
    assert solve(fixed, "hamburg", "hamburg") == 0, "you are already there"
    assert solve(fixed, "turin", "cork") is None, "nothing leaves turin"
