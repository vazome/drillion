def solve(peers):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_MACHINES = [
    "app-01",
    "app-02",
    "cache-01",
    "cache-02",
    "db-01",
    "db-02",
    "edge-01",
    "edge-02",
    "job-01",
]


def _gen(r):
    names = _MACHINES[: r.randint(6, 9)]
    r.shuffle(names)
    islands, rest = [], list(names)
    while rest:
        islands.append([rest.pop() for _ in range(min(r.randint(1, 4), len(rest)))])
    peers = {name: [] for name in names}
    for island in islands:
        for i, name in enumerate(island[1:], start=1):
            other = island[r.randrange(i)]
            # the link is recorded once, from whichever side happened to register it
            side, target = (name, other) if r.random() < 0.5 else (other, name)
            peers[side].append(target)
    return {name: sorted(peers[name]) for name in sorted(names)}, sorted(
        sorted(island) for island in islands
    )


def _reference(peers):
    both = {name: set(links) for name, links in peers.items()}
    for name, links in peers.items():
        for other in links:
            both[other].add(name)
    seen, groups = set(), []
    for name in peers:
        if name in seen:
            continue
        seen.add(name)
        stack, group = [name], []
        while stack:
            node = stack.pop()
            group.append(node)
            for nxt in both[node]:
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        groups.append(sorted(group))
    return sorted(groups)


def test_solve():
    r = rng()
    for _ in range(10):
        peers, planted = _gen(r)
        got = solve(peers)
        assert got == _reference(peers), f"islands of {peers}"
        assert got == planted, f"islands of {peers}"

    # cache-b is listed first and its own list is empty: a one-way walk splits the pair
    fixed = {"cache-b": [], "cache-a": ["cache-b"], "edge-1": []}
    assert solve(fixed) == [["cache-a", "cache-b"], ["edge-1"]], "a link works both ways"
    assert solve({"solo": []}) == [["solo"]], "a machine with no links is its own island"
    assert solve({}) == [], "no machines, no islands"
