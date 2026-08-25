"""Whole-task drill: what changed between two configs, at any depth.

Combines topics 30 (nested dicts from JSON), 18 (dict lookups), 25 (copy).
"""

from _lib import rng

META = {"topic": 75, "title": "DRILL: recursive diff of two nested configs",
        "tier": 4, "minutes": 30, "prereqs": [18],
        "practices": [30, 18, 25], "tags": ["whole-task"]}


def solve(old, new):
    """WHY: The staging environment works and production does not. Both were
    deployed from a config file, and someone on the platform team asks "what
    exactly is different between the two?" Reading two long files side by
    side by eye is slow and error-prone; a short list of added, removed and
    changed settings is what they want.

    YOU GET: `old` — a nested dictionary (a dictionary whose values can
    themselves be dictionaries), like {"replicas": 2, "db": {"host": "a"}}.
    This is the config from the first environment.

    `new` — the same kind of dictionary, from the second environment. The
    test builds both and hands them to you; you never build them yourself.

    YOU RETURN: one dictionary with three keys: "added", "removed" and
    "changed". Each holds a dictionary of setting paths (like "db.pool") and
    the values involved. All three keys are always present, even when there
    is nothing to list under one of them.

    ─── exact rules ───
    Two configs came out of two environments. Report the difference.

    `old` and `new` are nested dicts. Return exactly this shape, with
    dotted paths as keys:

        old = {"replicas": 2, "db": {"host": "a", "pool": 5}}
        new = {"replicas": 3, "db": {"host": "a"}, "tls": True}

        ->  {"added":   {"tls": True},
             "removed": {"db.pool": 5},
             "changed": {"replicas": (2, 3)}}

    Rules:
      - Only in new: added, mapped to the new value. Only in old: removed,
        mapped to the old value. In both but different: changed, mapped to
        the tuple (old_value, new_value).
      - When both sides hold a dict, walk into it. Otherwise compare the
        values as they are, so a dict replaced by a string is one changed
        entry, not a subtree of them.
      - Paths join keys with a dot. Top-level keys carry no dot.
      - All three keys are always in the result, empty dict when nothing
        landed there.
      - Do not modify old or new. The test checks that.

    This is config drift, and it is a real on-call question. Narrate the
    walk out loud as you write it.
    """
    raise NotImplementedError


HINTS = [
    ("The input has the same shape at every level, so the code should too: a "
    "function that handles one level and calls itself for the next. The part "
    "people miss is the path — each level has to hand the prefix down, or you "
    "end up with bare key names and no idea where they came from."),
    ("Write a helper walk(a, b, prefix) that appends into three dicts from the "
    "enclosing scope. For each key in a: missing from b means removed; both "
    "values dicts (isinstance(v, dict)) means recurse with prefix + key + '.'; "
    "otherwise compare with != and record the pair. Then a second small loop "
    "over b for the keys a never had. Read values, never assign into old or "
    "new."),
    ("Different data — carrying a prefix down a recursive walk:\n"
    "    def walk(d, prefix=''):\n"
    "        for k, v in d.items():\n"
    "            if isinstance(v, dict):\n"
    "                walk(v, prefix + k + '.')\n"
    "            else:\n"
    "                print(prefix + k, '=', v)\n"
    "    walk({'a': 1, 'b': {'c': 2, 'd': {'e': 3}}})\n"
    "    # a = 1\n"
    "    # b.c = 2\n"
    "    # b.d.e = 3\n"
    "Yours walks two dicts side by side instead of one, and records instead "
    "of printing."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

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
