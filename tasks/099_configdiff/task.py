def solve(old: dict[str, bool | dict[str, float | int | str] | dict[str, str]] | dict[str, dict[str, bool | dict[str, int] | float] | dict[str, dict[str, bool | int | str] | float] | dict[str, dict[str, float] | float | int | str]] | dict[str, dict[str, dict[str, bool] | dict[str, float] | dict[str, int | str]] | str] | dict[str, float], new: dict[str, dict[str, bool | dict[str, int] | str] | dict[str, dict[str, float] | float | int | str] | float] | dict[str, dict[str, dict[str, bool] | dict[str, float | str] | dict[str, int | str]] | str] | dict[str, dict[str, float | str] | dict[str, str] | float] | dict[str, int]):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    import copy

    def leaf():
        return r.choice([r.randint(1, 99),
                         r.choice(["on", "off", "warn", "1Gi", "30s"]),
                         r.choice([True, False]),
                         round(r.uniform(0.1, 9.9), 2)])

    def tree(depth):
        node = {}
        for name in r.sample(["db", "cache", "tls", "limits", "probe", "log",
                              "queue", "auth"], r.randint(2, 4)):
            node[name] = tree(depth - 1) if depth and r.random() < 0.5 else leaf()
        return node

    old = tree(2)
    new = copy.deepcopy(old)
    nodes = []

    def collect(d):
        nodes.append(d)
        for v in d.values():
            if isinstance(v, dict):
                collect(v)

    collect(new)
    for _ in range(r.randint(2, 5)):
        node = r.choice(nodes)
        action = r.choice(["add", "remove", "change", "change"])
        if action == "add":
            node[f"opt{r.randint(1, 99)}"] = r.choice([leaf(), {"k": leaf()}])
        elif node:
            key = r.choice(sorted(node))
            if action == "remove":
                del node[key]
            else:
                node[key] = leaf()
    return old, new


def _reference(old, new):
    added, removed, changed = {}, {}, {}

    def walk(a, b, prefix):
        for k, av in a.items():
            path = prefix + k
            if k not in b:
                removed[path] = av
            elif isinstance(av, dict) and isinstance(b[k], dict):
                walk(av, b[k], path + ".")
            elif av != b[k]:
                changed[path] = (av, b[k])
        for k, bv in b.items():
            if k not in a:
                added[prefix + k] = bv

    walk(old, new, "")
    return {"added": added, "removed": removed, "changed": changed}


def test_solve():
    import copy
    r = rng()
    for _ in range(4):
        old, new = _gen(r)
        before = copy.deepcopy((old, new))
        got = solve(old, new)
        assert (old, new) == before, "solve modified its inputs"
        assert got == _reference(old, new)
