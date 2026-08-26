def solve(name, replicas, cpu):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    name = f"{r.choice(['api', 'auth', 'billing', 'cron', 'ingest', 'web'])}-" \
           f"{r.choice(['blue', 'green', 'canary'])}"
    return name, r.randint(1, 12), r.choice([100, 250, 500, 750, 1000])


def _reference(name, replicas, cpu):
    class Service:
        def __init__(self, name, replicas, cpu):
            self.name = name
            self.replicas = replicas
            self.cpu = cpu

        def __repr__(self):
            return f"Service(name={self.name!r}, replicas={self.replicas}, cpu={self.cpu})"

        @property
        def total_cpu(self):
            return self.replicas * self.cpu

    return Service(name, replicas, cpu)


def test_solve():
    r = rng()
    for _ in range(4):
        name, replicas, cpu = _gen(r)
        got, exp = solve(name, replicas, cpu), _reference(name, replicas, cpu)

        assert (got.name, got.replicas, got.cpu) == (exp.name, exp.replicas, exp.cpu)
        assert repr(got) == repr(exp)
        assert got.total_cpu == exp.total_cpu

        bumped = replicas + r.randint(1, 8)
        got.replicas = bumped
        exp.replicas = bumped
        assert got.total_cpu == exp.total_cpu, "total_cpu must be derived, not stored"
        assert repr(got) == repr(exp)

        try:
            got.total_cpu = 0
        except AttributeError:
            pass
        else:
            raise AssertionError("total_cpu must be a read-only property")
