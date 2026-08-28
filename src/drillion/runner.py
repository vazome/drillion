"""Running the tests: task code only ever executes in a pytest subprocess."""

import ast
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

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


def _run_pytest(args, timeout=None, **env):
    """pytest in a subprocess, cwd a scratch dir so stray files never land in tasks/, and
    `tasks/` on PYTHONPATH so `from _lib import rng` works from any root."""
    with tempfile.TemporaryDirectory(
        dir=settings.root, ignore_cleanup_errors=True
    ) as scratch:
        # an empty config, pinned: from a checkout pytest would otherwise walk up, adopt
        # the repo's pyproject.toml and grade a learner against our own settings — its
        # `filterwarnings = error` above all. `-c` moves rootdir too, so pin that back to
        # `root` or pytest reports failures with no filename in them.
        ini = Path(scratch, "pytest.ini")
        ini.write_text("[pytest]\n", encoding="utf-8")
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-c",
                str(ini),
                f"--rootdir={settings.root}",
                *args,
                *_PYTEST,
            ],
            # task files are UTF-8; a Windows pipe would otherwise be cp1252 at both ends
            env={
                **os.environ,
                "PYTHONPATH": str(settings.tasks_dir),
                "PYTHONIOENCODING": "utf-8",
                **env,
            },
            cwd=scratch,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
            timeout=timeout,
        )


def run_tests(path, seed):
    """Task code only ever runs here, in its own process."""
    try:
        r = _run_pytest(
            [str(path), "-x", "--timeout=10"], timeout=60, DRILLION_SEED=str(seed)
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
            src = meta["path"].read_text(encoding="utf-8")
            path = meta["dir"] / "_selfcheck.py"  # an explicit path is always collected
            path.write_text(
                splice(src, _reference_call(cut(src).body)), encoding="utf-8"
            )
            made.append(path)
        r = _run_pytest([*map(str, made), "--timeout=60"])
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
