def solve(specs):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


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
