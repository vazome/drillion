def solve(links, start):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from itertools import pairwise

from _lib import rng


def _gen(r):
    tail = [f"/app/t{i}" for i in range(r.randint(0, 4))]
    ring = [f"/app/r{i}" for i in range(r.randint(1, 5))]
    loops = r.random() < 0.7
    chain = tail + ring if loops else tail + ring + ["/app/file"]
    links = {}
    for here, there in pairwise(chain):
        links[here] = there
    if loops:
        links[chain[-1]] = ring[0]
    for i in range(r.randint(0, 3)):  # unrelated links, to punish anything that scans the dict
        links[f"/other/x{i}"] = f"/other/y{i}"
    start = chain[0]
    return links, start


def _reference(links, start):
    slow = fast = start
    while True:
        slow = links.get(slow)
        if slow is None:
            return None
        fast = links.get(fast)
        if fast is None:
            return None
        fast = links.get(fast)
        if fast is None:
            return None
        if slow == fast:
            break
    entry = start
    while entry != slow:  # both one step at a time from here, and they meet at the entry
        entry, slow = links[entry], links[slow]
    length, node = 1, links[entry]
    while node != entry:
        node, length = links[node], length + 1
    return entry, length


def _by_bookkeeping(links, start):
    seen, at = [], start
    while at in links:
        if at in seen:
            return at, len(seen) - seen.index(at)
        seen.append(at)
        at = links[at]
    return None


def test_solve():
    r = rng()
    for _ in range(40):
        links, start = _gen(r)
        original = dict(links)
        want = _by_bookkeeping(links, start)
        assert _reference(links, start) == want, "grader bug"
        assert solve(links, start) == want, f"start={start} links={original}"
        assert links == original, f"solve must not disturb its input: {original}"

    assert solve({}, "/anything") is None, "start is not a key: the chain ends there"
    assert solve({"/a": "/b", "/b": "/real"}, "/a") is None
    assert solve({"/t": "/t"}, "/t") == ("/t", 1), "a link to itself is a loop of one"
    assert solve({"/a": "/b", "/b": "/a"}, "/a") == ("/a", 2), "no tail: the entry is the start"
    assert solve({"/a": "/b", "/b": "/c", "/c": "/b"}, "/a") == ("/b", 2)

    # the two walkers meet at /d; the loop begins at /c, and only one of those is the link to fix
    ring = {"/a": "/b", "/b": "/c", "/c": "/d", "/d": "/e", "/e": "/c"}
    assert solve(ring, "/a") == ("/c", 3), "report where the loop begins, not where you met"
    assert solve(ring, "/c") == ("/c", 3), "starting inside the loop gives the same entry"
    assert solve(ring, "/d") == ("/d", 3), "from /d the loop begins at /d, not at /c"
