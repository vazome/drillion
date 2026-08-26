"""Running the tests: task code only ever executes in a pytest subprocess."""

import ast
import os
import re
import subprocess
import sys

from .catalogue import tasks
from .region import _solve, cut, splice, stub
from .settings import settings

_TASK_LINE = re.compile(r"[\w./\\-]*task\.py:(\d+)")
# every task.py is called task.py, so pytest must name modules by path, not basename
# `--color=no` because FORCE_COLOR or PY_COLORS in the environment turns colour on
# regardless of the tty, and the escapes land in the learner's output panel
_PYTEST = [
    "-q",
    "--no-header",
    "--color=no",
    "-p",
    "no:cacheprovider",
    "--import-mode=importlib",
]


def _env(**extra):
    """`tasks/` on the path, so `from _lib import rng` works from any root."""
    return {**os.environ, "PYTHONPATH": str(settings.tasks_dir), **extra}


def run_tests(path, seed):
    """Task code only ever runs here, in its own process."""
    cmd = [sys.executable, "-m", "pytest", str(path), "-x", "--timeout=10", *_PYTEST]
    try:
        r = subprocess.run(
            cmd,
            env=_env(DRILLION_SEED=str(seed)),
            cwd=settings.root,
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        return False, "timed out after 60s — an endless loop, most likely"
    return r.returncode == 0, r.stdout


def summarise(out, marker_line):
    """pytest output for the browser: the assertion lines, in editor coordinates."""

    def editor_line(m):
        n = int(m.group(1))
        return f"line {n}" if n < marker_line else m.group(0)

    text = _TASK_LINE.sub(editor_line, out)
    lines = text.split("\n")
    head = [ln for ln in lines if ln.startswith("E   ")][:6]
    return {
        "headline": head
        or [ln for ln in lines if ln.startswith(("FAILED", "ERROR"))][:6],
        "output": text[-8192:],
    }


def _reference_call(body):
    """solve()'s own signature, wired straight to the reference answer."""
    fn = _solve(ast.parse(body))
    a = fn.args
    args = [p.arg for p in a.posonlyargs + a.args]
    args += [f"*{a.vararg.arg}"] if a.vararg else []
    args += [f"{p.arg}={p.arg}" for p in a.kwonlyargs]
    args += [f"**{a.kwarg.arg}"] if a.kwarg else []
    stubbed = stub(body)
    return (
        stubbed[: stubbed.rindex("raise NotImplementedError")]
        + f"return _reference({', '.join(args)})"
    )


def selfcheck():
    """Does the whole set still work? Solve every task with its own _reference.
    Returns the number of failures."""
    all_tasks = tasks()
    made = []
    try:
        for meta in all_tasks.values():
            src = meta["path"].read_text()
            path = meta["dir"] / "_selfcheck.py"  # an explicit path is always collected
            path.write_text(splice(src, _reference_call(cut(src).body)))
            made.append(path)
        r = subprocess.run(
            [sys.executable, "-m", "pytest", *map(str, made), "--timeout=60", *_PYTEST],
            cwd=settings.root,
            env=_env(),
            capture_output=True,
            text=True,
            check=False,
        )
    finally:
        for path in made:
            path.unlink(missing_ok=True)
    failed = sorted(
        {
            ln.split("_selfcheck.py")[0].rstrip("/\\").split("/")[-1]
            for ln in r.stdout.split("\n")
            if ln.startswith(("FAILED", "ERROR"))
        }
    )
    if r.returncode and not failed:
        print(r.stdout[-2000:].strip() or "pytest did not run")
        return 1
    for slug in failed:
        print("FAILED", slug)
    print(f"{len(all_tasks) - len(failed)}/{len(all_tasks)} ok")
    return len(failed)
