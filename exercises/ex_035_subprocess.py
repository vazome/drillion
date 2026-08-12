"""Every deploy script shells out; subprocess.run is how Python does it safely."""

import subprocess
import sys

from _lib import rng

META = {"topic": 35, "title": "subprocess.run — run a command, read the result",
        "tier": 3, "minutes": 15, "prereqs": []}


def solve(argv):
    """Run the command `argv` (a list like ["echo", "hi"]) and report on it.

    Return a dict with exactly these keys:

        {"ok": True,          # returncode == 0
         "code": 0,           # the returncode itself
         "out": "hi",         # stdout, stripped of surrounding whitespace
         "err": ""}           # stderr, stripped the same way

    Rules:
    - Pass argv straight to subprocess.run as a LIST. Never join it into a
      string with shell=True — that is how injection bugs happen, and the
      list form does not need it.
    - Capture both streams as text, not bytes.
    - A non-zero exit must NOT raise. Either skip check=True, or use it and
      catch subprocess.CalledProcessError. Both give the same dict here.

        ["false"]  ->  {"ok": False, "code": 1, "out": "", "err": ""}
    """
    raise NotImplementedError


HINTS = [
    "subprocess.run returns a CompletedProcess object. Everything you need — "
    "return code, stdout, stderr — is an attribute on it. By default though, "
    "output goes to the terminal instead of being captured, and it arrives as "
    "bytes. Two keyword arguments fix that.",
    "The keywords are capture_output=True and text=True. Then read "
    ".returncode, .stdout and .stderr off the result. check=True would raise "
    "CalledProcessError on non-zero exit — here you want the code either way, "
    "so plain run without check is the shorter route.",
    "Different command, same moves:\n"
    "    import subprocess, sys\n"
    "    res = subprocess.run([sys.executable, '--version'],\n"
    "                         capture_output=True, text=True)\n"
    "    print(res.returncode)        # 0\n"
    "    print(res.stdout.strip())    # Python 3.12.x\n"
    "Build your dict from those three attributes.",
]


# ─────────────────────────────  below here is the machinery  ──────────────

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
    res = subprocess.run(argv, capture_output=True, text=True)
    return {"ok": res.returncode == 0,
            "code": res.returncode,
            "out": res.stdout.strip(),
            "err": res.stderr.strip()}


def test_solve():
    r = rng()
    for _ in range(3):
        argv = _gen(r)
        assert solve(list(argv)) == _reference(argv)
