def solve(argv: list[str]):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import subprocess
import sys

from _lib import rng


def _gen(r):
    """Always a python child: `echo`/`true`/`false` are cmd builtins on Windows."""
    word = r.choice(["deploy", "sync", "drain", "evict", "rollout"])
    word += f"-{r.randint(10, 99)}"
    out = r.choice([f"print({word!r}); ", ""])
    err = r.choice(["sys.stderr.write('warn: slow disk\\n'); ", ""])
    code = r.choice([0, 0, 1, 2, 5])
    prog = f"import sys; {out}{err}sys.exit({code})"
    return [sys.executable, "-c", prog]


def _reference(argv):
    res = subprocess.run(argv, capture_output=True, text=True, check=False)
    return {"ok": res.returncode == 0,
            "code": res.returncode,
            "out": res.stdout.strip(),
            "err": res.stderr.strip()}


def test_solve():
    r = rng()
    for _ in range(3):
        argv = _gen(r)
        assert solve(list(argv)) == _reference(argv)
