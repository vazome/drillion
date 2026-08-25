"""Running the tests: exercise code only ever executes in a pytest subprocess.

The server never imports a drill, so a runaway loop or a stray `sys.exit` costs a
subprocess, not the session. `summarise` turns pytest's output into the handful of
lines the browser shows, in the editor's own line numbers.
"""

import ast
import os
import re
import subprocess
import sys

from .catalogue import exercises
from .region import _solve, cut, splice, stub
from .settings import settings

_DRILL_LINE = re.compile(r"[\w./\\-]*drill\.py:(\d+)")
# every drill.py is called drill.py, so pytest must name modules by path, not basename
_PYTEST = ["-q", "--no-header", "-p", "no:cacheprovider", "--import-mode=importlib"]


def _env(**extra):
    """`exercises/` on the path, so `from _lib import rng` works from any root."""
    return {**os.environ, "PYTHONPATH": str(settings.exercises_dir), **extra}


def run_tests(path, seed):
    """Exercise code only ever runs here, in its own process."""
    cmd = [sys.executable, "-m", "pytest", str(path), "-x", "--timeout=10", *_PYTEST]
    try:
        r = subprocess.run(cmd, env=_env(STUDY_SEED=str(seed)), cwd=settings.root,
                           capture_output=True, text=True, check=False, timeout=60)
    except subprocess.TimeoutExpired:
        return False, "timed out after 60s — an endless loop, most likely"
    return r.returncode == 0, r.stdout


def summarise(out, marker_line):
    """pytest output for the browser: the assertion lines, in editor coordinates.

    The region starts at line 1 of drill.py, so the map is the identity — a frame
    is either the learner's or the grader's, and only the first gets a bare line."""
    def editor_line(m):
        n = int(m.group(1))
        return f"line {n}" if n < marker_line else m.group(0)

    text = _DRILL_LINE.sub(editor_line, out)
    lines = text.split("\n")
    head = [ln for ln in lines if ln.startswith("E   ")][:6]
    return {"headline": head or [ln for ln in lines if ln.startswith(("FAILED", "ERROR"))][:6],
            "output": text[-8192:]}


def _reference_call(body):
    """solve()'s own signature, wired straight to the reference answer."""
    fn = _solve(ast.parse(body))
    a = fn.args
    args = [p.arg for p in a.posonlyargs + a.args]
    args += [f"*{a.vararg.arg}"] if a.vararg else []
    args += [f"{p.arg}={p.arg}" for p in a.kwonlyargs]
    args += [f"**{a.kwarg.arg}"] if a.kwarg else []
    stubbed = stub(body)
    return stubbed[:stubbed.rindex("raise NotImplementedError")] + f"return _reference({', '.join(args)})"


def selfcheck():
    """Does the whole set still work? Solve every exercise with its own _reference.
    Returns the number of failures."""
    exs = exercises()
    made = []
    try:
        for meta in exs.values():
            src = meta["path"].read_text()
            path = meta["dir"] / "_selfcheck.py"      # an explicit path is always collected
            path.write_text(splice(src, _reference_call(cut(src).body)))
            made.append(path)
        r = subprocess.run([sys.executable, "-m", "pytest", *map(str, made),
                            "--timeout=60", *_PYTEST],
                           cwd=settings.root, env=_env(), capture_output=True, text=True,
                           check=False)
    finally:
        for path in made:
            path.unlink(missing_ok=True)
    failed = sorted({ln.split("_selfcheck.py")[0].rstrip("/\\").split("/")[-1]
                     for ln in r.stdout.split("\n") if ln.startswith(("FAILED", "ERROR"))})
    if r.returncode and not failed:
        print(r.stdout[-2000:].strip() or "pytest did not run")
        return 1
    for slug in failed:
        print("FAILED", slug)
    print(f"{len(exs) - len(failed)}/{len(exs)} ok")
    return len(failed)
