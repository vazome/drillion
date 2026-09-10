def solve(imports):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_MODULES = ["app", "api", "auth", "core", "db", "models", "report", "utils", "views"]


def _gen(r):
    names = _MODULES[: r.randint(6, 9)]
    order = list(names)
    r.shuffle(order)
    imports = {name: [] for name in names}
    for i, name in enumerate(order):
        later = order[i + 1 :]
        r.shuffle(later)
        imports[name] = later[: r.randint(0, 3)]
    if r.random() < 0.5:
        # one edge pointing back up the order is all it takes to close a loop
        cut = r.randrange(1, len(order))
        imports[order[cut]].append(order[r.randrange(cut)])
    return {name: sorted(imports[name]) for name in sorted(names)}


def _reference(imports):
    seen, stack, live = set(), [], set()

    def walk(node):
        seen.add(node)
        stack.append(node)
        live.add(node)
        for nxt in imports[node]:
            if nxt in live:
                return [*stack[stack.index(nxt) :], nxt]
            if nxt not in seen:
                found = walk(nxt)
                if found:
                    return found
        stack.pop()
        live.discard(node)
        return []

    for node in sorted(imports):
        if node not in seen:
            found = walk(node)
            if found:
                return found
    return []


def test_solve():
    r = rng()
    for _ in range(12):
        imports = _gen(r)
        got, want = solve(imports), _reference(imports)
        assert got == want, f"expected {want}, got {got!r}, for {imports}"

    # core is reached twice, down two different branches, and nothing loops
    diamond = {"app": ["db", "cache"], "cache": ["core"], "db": ["core"], "core": []}
    assert solve(diamond) == [], "two ways to reach one module is not a loop"

    loop = {"api": ["auth"], "auth": ["models"], "models": ["api"], "utils": []}
    assert solve(loop) == ["api", "auth", "models", "api"], "report the loop, first name repeated"
    assert solve({"api": ["api"]}) == ["api", "api"], "a module that imports itself is a loop"
    assert solve({}) == []
