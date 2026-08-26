def solve(argv):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import subprocess
import sys

from _lib import rng


def _gen(r):
    word = r.choice(["deploy", "sync", "drain", "evict", "rollout"])
    word += f"-{r.randint(10, 99)}"
    kind = r.choice(["echo", "true", "false", "py", "py"])
    if kind == "echo":
        return ["echo", word]
    if kind == "true":
        return ["true"]
    if kind == "false":
        return ["false"]
    code = r.choice([0, 1, 2, 5])
    prog = (f"import sys; print({word!r}); "
            f"sys.stderr.write('warn: slow disk\\n'); sys.exit({code})")
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
