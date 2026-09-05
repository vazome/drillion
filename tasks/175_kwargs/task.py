def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    cmds = ["deploy", "status", "rollback", "scale"]
    words = ["api", "worker", "--force", "web", "--now"]
    names = ["region", "dry_run", "max_retries", "log_level"]
    vals = ["eu", True, 3, "debug"]
    args = tuple(r.sample(words, r.randint(0, 3)))
    flags = {n: v for n, v in zip(r.sample(names, r.randint(0, 3)), vals)}
    kwargs = dict(flags)
    if r.random() < 0.5:
        kwargs["timeout"] = r.choice([5, 60, 120])
    return r.choice(cmds), args, kwargs


def _reference():
    def describe(cmd, *args, timeout=30, **flags):
        parts = [cmd, *args]
        parts += [f"--{k.replace('_', '-')}={v}" for k, v in sorted(flags.items())]
        return " ".join(str(p) for p in parts) + f" (timeout={timeout})"

    return describe


def test_solve():
    r = rng()
    mine, theirs = solve(), _reference()
    for _ in range(8):
        cmd, args, kwargs = _gen(r)
        assert mine(cmd, *args, **kwargs) == theirs(cmd, *args, **kwargs), (cmd, args, kwargs)
    assert mine("deploy", "api", 5) == theirs("deploy", "api", 5), "timeout must be keyword-only"
    assert mine("status") == "status (timeout=30)"
