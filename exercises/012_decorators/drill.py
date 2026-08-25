def solve(calls):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _make(name, k, base):
    """A plain function with a known name, so the log has something to record."""
    def fn(host, replicas=1, dry_run=False):
        return f"{host}:dry" if dry_run else f"{host}:{base + k * replicas}"

    fn.__name__ = name
    return fn


def _gen(r):
    """A few functions, each with the calls to replay against it."""
    plans = []
    for name in r.sample(["scale", "drain", "cordon", "restart", "resize", "tag"],
                         r.randint(2, 4)):
        fn = _make(name, r.randint(2, 9), r.randint(1, 20))
        calls = []
        for _ in range(r.randint(2, 4)):
            host = r.choice(["api", "db", "cache", "edge"]) + str(r.randint(1, 9))
            args = (host,) if r.random() < 0.5 else (host, r.randint(1, 4))
            kwargs = {}
            if len(args) == 1 and r.random() < 0.6:
                kwargs["replicas"] = r.randint(1, 4)
            if r.random() < 0.4:
                kwargs["dry_run"] = r.choice([True, False])
            calls.append((args, kwargs))
        plans.append((fn, calls))
    return plans


def _reference(calls):
    def record(fn):
        def wrapper(*args, **kwargs):
            result = fn(*args, **kwargs)
            calls.append((fn.__name__, args, kwargs, result))
            return result
        return wrapper
    return record


def test_solve():
    r = rng()
    for _ in range(4):
        plans = _gen(r)
        got_log, exp_log = [], []
        record, ref_record = solve(got_log), _reference(exp_log)

        for fn, planned in plans:
            wrapped, ref_wrapped = record(fn), ref_record(fn)
            for args, kwargs in planned:
                expected = fn(*args, **kwargs)
                assert wrapped(*args, **kwargs) == expected, "wrapper must return fn's result"
                assert ref_wrapped(*args, **kwargs) == expected

        assert got_log == exp_log
