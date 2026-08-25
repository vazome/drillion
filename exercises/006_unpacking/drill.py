def solve(xs, pairs):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    xs = [r.randint(0, 99) for _ in range(r.randint(3, 8))]
    keys = r.sample(["env", "region", "tier", "owner", "app"], r.randint(2, 4))
    vals = ["prod", "dev", "eu", "us", "web", "ops"]
    pairs = [(k, r.choice(vals)) for k in keys]
    return xs, pairs


def _reference(xs, pairs):
    first, *rest = xs
    *body, last = xs
    swapped = list(xs)
    swapped[0], swapped[-1] = swapped[-1], swapped[0]
    lines = [f"{k}={v}" for k, v in pairs]
    return {"first": first, "rest": rest, "body": body, "last": last,
            "swapped": swapped, "lines": lines}


def test_solve():
    r = rng()
    for _ in range(4):
        xs, pairs = _gen(r)
        assert solve(list(xs), [tuple(p) for p in pairs]) == _reference(xs, pairs)
