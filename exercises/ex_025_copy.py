"""One shared inner list has silently corrupted many config-cloning scripts."""

from _lib import rng

META = {"topic": 25, "title": "shallow vs deep copy — predict the damage", "tier": 1,
        "minutes": 6, "prereqs": []}


def solve(cfg):
    """Predict, without running it, what this snippet leaves behind:

        import copy
        shallow = cfg.copy()
        deep = copy.deepcopy(cfg)
        shallow["servers"].append("web-9")
        shallow["region"] = "eu"
        deep["ports"].append(9999)

    cfg always has exactly two keys: "servers" (a list of names) and
    "ports" (a list of ints). Return a tuple (cfg, shallow, deep) — the
    three dicts as they look AFTER the snippet runs.

    Build the three results by hand from the cfg you were given. The point
    is deciding which of the three mutations leaks where.
    """
    raise NotImplementedError


HINTS = [
    "cfg.copy() copies only the outer dict — the lists inside are the very "
    "same objects, now reachable from two dicts. deepcopy clones all the way "
    "down. For each of the three mutations, ask: which actual object does "
    "this line touch, and who else can see that object.",
    "shallow['servers'] is the same list object as cfg['servers'], so an "
    "append through one shows through the other. Assigning a brand-new key "
    "on shallow touches only the outer dict, which is NOT shared. deep "
    "shares nothing at all. Now apply that to the three lines.",
    "Different data, same mechanics:\n"
    "    import copy\n"
    "    a = {'x': [1, 2]}\n"
    "    b = a.copy()\n"
    "    c = copy.deepcopy(a)\n"
    "    b['x'].append(3)\n"
    "    print(a)   # {'x': [1, 2, 3]}   b's append leaked into a\n"
    "    print(b)   # {'x': [1, 2, 3]}\n"
    "    print(c)   # {'x': [1, 2]}      the deep copy stayed clean\n"
    "Same reasoning here, just three mutations instead of one.",
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    servers = [f"web-{r.randint(1, 8)}" for _ in range(r.randint(1, 3))]
    servers.append(f"db-{r.randint(1, 4)}")
    ports = r.sample([80, 443, 5432, 6379, 8080, 9090], r.randint(2, 4))
    return {"servers": servers, "ports": ports}


def _reference(cfg):
    import copy
    shallow = cfg.copy()                  # new outer dict, SAME inner lists
    deep = copy.deepcopy(cfg)             # fully independent clone
    shallow["servers"].append("web-9")    # leaks into cfg: the list is shared
    shallow["region"] = "eu"              # does not: top level is separate
    deep["ports"].append(9999)            # touches nothing else
    return cfg, shallow, deep


def test_solve():
    import copy
    r = rng()
    for _ in range(4):
        cfg = _gen(r)
        assert solve(copy.deepcopy(cfg)) == _reference(copy.deepcopy(cfg))
