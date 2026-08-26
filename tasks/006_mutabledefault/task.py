def solve(tasks):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    pool = ["deploy", "migrate", "backup", "rotate", "scale", "purge", "sync"]
    return r.sample(pool, r.randint(2, 5))


def _reference(tasks):
    def add(task, done=[]):  # noqa: B006 — the bug under study
        done.append(task)
        return done

    def add_fixed(task, done=None):
        if done is None:
            done = []
        done.append(task)
        return done

    for t in tasks:
        buggy = add(t)
    for t in tasks:
        fixed = add_fixed(t)
    return (list(buggy), fixed)


def test_solve():
    r = rng()
    for _ in range(4):
        tasks = _gen(r)
        assert solve(list(tasks)) == _reference(tasks)
