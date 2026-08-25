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

_FILE_LINE = re.compile(r"[\w./\\-]*\.py:(\d+)")


def run_tests(path, seed):
    """Exercise code only ever runs here, in its own process."""
    cmd = [sys.executable, "-m", "pytest", str(path), "-x", "-q", "--no-header",
           "--timeout=10", "-p", "no:cacheprovider"]
    try:
        r = subprocess.run(cmd, env={**os.environ, "STUDY_SEED": str(seed)}, cwd=settings.root,
                           capture_output=True, text=True, check=False, timeout=60)
    except subprocess.TimeoutExpired:
        return False, "timed out after 60s — an endless loop, most likely"
    return r.returncode == 0, r.stdout


def summarise(out, region_start, doc_offset, hints_line):
    """pytest output for the browser: the assertion lines, in editor coordinates."""
    # ponytail: the last docstring line, under-counted when code sits above solve() — but
    # only by lines inside the docstring itself, which never appear in a traceback
    doc_end = region_start + doc_offset

    def editor_line(m):
        n = int(m.group(1))
        if not region_start <= n < hints_line:
            return m.group(0)             # a frame in the test or the machinery: leave it alone
        return f"line {n - region_start + 1 - (doc_offset if n > doc_end else 0)}"

    text = _FILE_LINE.sub(editor_line, out)
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
        for slug, meta in exs.items():
            src = meta["path"].read_text()
            path = settings.exercises_dir / f"_selfcheck_{slug}.py"
            path.write_text(splice(src, _reference_call(cut(src).body)))
            made.append(path)
        r = subprocess.run([sys.executable, "-m", "pytest", *map(str, made), "-q", "--no-header",
                            "--timeout=60", "-p", "no:cacheprovider"],
                           cwd=settings.root, capture_output=True, text=True, check=False)
    finally:
        for path in made:
            path.unlink(missing_ok=True)
    failed = sorted({ln.split("_selfcheck_", 1)[-1].split(".py")[0]
                     for ln in r.stdout.split("\n") if ln.startswith(("FAILED", "ERROR"))})
    if r.returncode and not failed:
        print(r.stdout[-2000:].strip() or "pytest did not run")
        return 1
    for slug in failed:
        print("FAILED", slug)
    print(f"{len(exs) - len(failed)}/{len(exs)} ok")
    return len(failed)
