"""@dataclass writes the boilerplate; frozen=True makes a record you cannot corrupt."""

from _lib import rng

META = {"topic": 15, "title": "dataclasses — defaults, frozen=True, sort by a field", "tier": 3,
        "minutes": 12, "prereqs": []}


def solve(specs):
    """WHY: An inventory script reads server records from a short-hand list
    where people leave out the fields that have sensible defaults: most
    servers get 100 CPU and live in the main zone unless said otherwise. The
    records get passed around many scripts, so nobody should be able to
    change one by accident after it is made. Capacity planning then wants
    the list ordered smallest-CPU first.

    YOU GET: `specs` — a list of tuples of 1, 2 or 3 items like [("db",
    400), ("api",), ("edge", 200, "eu-west-1b")]: name, then optional cpu,
    then optional zone. The test creates it and hands it to you; you never
    build it yourself.

    YOU RETURN: a list of Node records (one per spec, defaults filled in,
    locked against later edits), sorted by cpu from smallest to largest.

    ─── exact rules ───
    Build frozen Node records from short specs and sort them by cpu.

    Define a dataclass called Node with exactly these three fields, in this
    order, with these defaults:

        name: str
        cpu: int = 100
        zone: str = "us-east-1a"

    It must be frozen, so no attribute can be reassigned after construction.

    specs is a list of tuples of length 1, 2 or 3 — the leading fields only,
    with whatever is missing left to the defaults. Return the list of Node
    instances sorted by cpu, ascending.

        [("db", 400), ("api",), ("edge", 200, "eu-west-1b")]
        ->  [Node(name='api',  cpu=100, zone='us-east-1a'),
             Node(name='edge', cpu=200, zone='eu-west-1b'),
             Node(name='db',   cpu=400, zone='us-east-1a')]

    Node(*spec) spreads a short tuple straight into the constructor, which is
    where the defaults do their work — no need to pad the tuples yourself.
    Sort with sorted and a key.
    """
    raise NotImplementedError


HINTS = [
    ("Two halves. First, describe the record: a class body that is nothing but "
    "field names with their types, plus one decorator that turns that into a "
    "real class with a constructor, a repr and equality. Second, the frozen "
    "part — the decorator takes an argument that makes assignment raise instead "
    "of silently rewriting a record someone else is holding. Then it is just a "
    "sort."),
    ("from dataclasses import dataclass, then @dataclass(frozen=True) above "
    "class Node. Inside the class write the three annotated fields, giving the "
    "last two their default values; fields with defaults must come after ones "
    "without. Build with Node(*spec) for each spec, and return "
    "sorted(nodes, key=lambda n: n.cpu)."),
    ("Different data — release records:\n"
    "    from dataclasses import dataclass\n"
    "\n"
    "    @dataclass(frozen=True)\n"
    "    class Release:\n"
    "        tag: str\n"
    "        build: int = 0\n"
    "\n"
    "    rs = [Release(*s) for s in [('v2', 7), ('v1',)]]\n"
    "    print(rs)                                  # [Release(tag='v2', build=7), \n"
    "                                               #  Release(tag='v1', build=0)]\n"
    "    print(sorted(rs, key=lambda x: x.build))   # v1 first\n"
    "    rs[0].build = 9                            # dataclasses.FrozenInstanceError\n"
    "The repr and the __init__ came free — that is the whole point of the "
    "decorator."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    """Specs of mixed length. Exactly one leans on both defaults, and no two
    nodes share a cpu, so the sorted order is never ambiguous."""
    zones = ["us-east-1a", "us-east-1b", "eu-west-1b", "ap-south-1a"]
    names = r.sample(["api", "auth", "billing", "cron", "db", "edge", "ingest", "web"],
                     r.randint(3, 5))
    cpus = r.sample([200, 300, 400, 500, 600, 700, 800, 900], len(names))

    specs = []
    for name, cpu in zip(names, cpus):
        specs.append((name, cpu) if r.random() < 0.5 else (name, cpu, r.choice(zones)))
    bare = r.randrange(len(specs))
    specs[bare] = (specs[bare][0],)
    r.shuffle(specs)
    return specs


def _reference(specs):
    from dataclasses import dataclass

    @dataclass(frozen=True)
    class Node:
        name: str
        cpu: int = 100
        zone: str = "us-east-1a"

    return sorted((Node(*spec) for spec in specs), key=lambda n: n.cpu)


def test_solve():
    import dataclasses

    r = rng()
    for _ in range(4):
        specs = _gen(r)
        got, exp = solve(list(specs)), _reference(specs)

        assert [(n.name, n.cpu, n.zone) for n in got] == [(n.name, n.cpu, n.zone) for n in exp]
        assert dataclasses.is_dataclass(got[0]), "Node must be a dataclass"
        assert type(got[0]).__name__ == "Node"

        try:
            got[0].cpu = 1
        except dataclasses.FrozenInstanceError:
            pass
        else:
            raise AssertionError("Node must be declared frozen=True")
