"""Running the tests: task code only ever executes in a pytest subprocess."""

import ast
import re
import subprocess
import tempfile
from pathlib import Path

from . import sandbox
from .catalogue import tasks
from .region import _solve, cut, splice, stub
from .settings import settings

_TASK_LINE = re.compile(r"[\w./-]*task\.py:(\d+)")
# pytest renders paths with the platform separator, so on Windows every path it prints
# arrives with backslashes. Normalising the .py paths once, on the way in, keeps both the
# panel and the slug parsing platform-blind — and leaves a learner's own backslashes
# (a regex, an escape in a failed assertion) alone, which a blanket replace would not
_PY_PATH = re.compile(r"[\w.\\/-]*\.py")
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
    """pytest in a subprocess, sandboxed: cwd a scratch dir that is also the child's `HOME`
    and the only place it may write, and `tasks/` on PYTHONPATH so `from _lib import rng`
    works from any root. `sandbox.run` decides everything else about the child."""
    with tempfile.TemporaryDirectory(
        dir=settings.root, ignore_cleanup_errors=True
    ) as scratch:
        # an empty config, pinned: from a checkout pytest would otherwise walk up, adopt
        # the repo's pyproject.toml and grade a learner against our own settings — its
        # `filterwarnings = error` above all. `-c` moves rootdir too, so pin that back to
        # `root` or pytest reports failures with no filename in them.
        ini = Path(scratch, "pytest.ini")
        ini.write_text("[pytest]\n", encoding="utf-8")
        return sandbox.run(
            ["-c", str(ini), f"--rootdir={settings.root}", *args, *_PYTEST],
            scratch,
            timeout,
            PYTHONPATH=str(settings.tasks_dir),
            **env,
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


def _posix(out):
    """Every .py path in pytest's output with "/" separators, whatever printed it."""
    return _PY_PATH.sub(lambda m: m.group(0).replace("\\", "/"), out)


def summarise(out, marker_line):
    """pytest output for the browser: the assertion lines, in editor coordinates."""
    out = _posix(out)

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


def _failed_slugs(out):
    """The task folders named by pytest's `FAILED`/`ERROR` summary lines.

    Splitting on whitespace drops the `FAILED ` prefix, which the old `/`-only split
    used to eat by accident and kept on Windows."""
    return sorted(
        {
            Path(ln.split(maxsplit=1)[1].split("::")[0]).parent.name
            for ln in _posix(out).split("\n")
            if ln.startswith(("FAILED", "ERROR")) and "_selfcheck.py" in ln
        }
    )


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
    failed = _failed_slugs(r.stdout)
    if r.returncode and not failed:
        print(r.stdout[-2000:].strip() or "pytest did not run")
        return 1
    for slug in failed:
        print("FAILED", slug)
    print(f"{len(all_tasks) - len(failed)}/{len(all_tasks)} ok")
    return len(failed)
