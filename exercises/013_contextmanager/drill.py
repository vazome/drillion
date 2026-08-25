def solve(events, name):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from contextlib import contextmanager

from _lib import rng


def _gen(r):
    name = r.choice(["deploy", "drain", "migrate", "rollout", "backup", "reindex"])
    body = [r.choice(["step", "check", "wait", "push"]) + str(r.randint(1, 9))
            for _ in range(r.randint(1, 3))]
    boom = r.choice([ValueError, KeyError, RuntimeError, TimeoutError])
    msg = f"{r.choice(['pod', 'node', 'disk'])} {r.randint(100, 999)}"
    return name, body, boom, msg


def _run(factory, name, body, boom, msg):
    """Drive one context manager down both paths and report what happened."""
    clean = []
    with factory(clean, name):
        clean.extend(body)

    dirty, caught = [], None
    try:
        with factory(dirty, name):
            dirty.extend(body)
            raise boom(msg)
    except boom as exc:
        caught = str(exc)
    return clean, dirty, caught


@contextmanager
def _reference(events, name):
    events.append(f"enter {name}")
    try:
        yield
    finally:
        events.append(f"exit {name}")


def test_solve():
    r = rng()
    for _ in range(4):
        name, body, boom, msg = _gen(r)
        assert _run(solve, name, body, boom, msg) == _run(_reference, name, body, boom, msg)
