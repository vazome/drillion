"""Grading a manifest: the brief a sitting is graded against, and how it is produced.

`grade.py` is task-authored Python. It is loaded and run only inside the sandboxed child
that `sandbox.run_script` starts, and it talks back in JSON. The server never imports it."""

import hashlib
import json
import math
import os
import stat
import subprocess
import tempfile
from pathlib import Path

from . import sandbox
from .settings import settings

MAX_BRIEF_BYTES = 8192
MAX_SPEC_CHARS = 65536
SCALARS = (str, int, float, bool)
BRIEF_SECONDS = 30

# Runs inside the sandbox, with the grader path, seed, output path and module name as argv.
# `drillion.guard` first because on the guard tier its audit hook is the only confinement
# there is, and it installs on import. A kernel tier denies the read instead, which is the
# same answer by a stronger route, so failing to find it is not an error here.
_BRIEF_SOURCE = """
try:
    import drillion.guard
except ImportError, OSError:
    pass

import importlib.util, json, random, sys

path, seed, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
spec = importlib.util.spec_from_file_location(sys.argv[4], path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
text = json.dumps(module.brief(random.Random(seed)))
with open(out, "w", encoding="utf-8") as stream:
    stream.write(text)
"""


class Rejected(Exception):
    """A grader that did not produce a usable brief. Nothing was graded."""


def _validated(raw):
    """A brief is a flat mapping of string keys to finite scalars. Anything else is a
    task-authoring bug, and one that would otherwise reach a template or an assert."""
    if not isinstance(raw, dict):
        raise Rejected("brief() must return a mapping")
    for key, value in raw.items():
        if not isinstance(key, str) or not key.isidentifier():
            raise Rejected(f"brief key {key!r} is not a plain name")
        if not isinstance(value, SCALARS):
            raise Rejected(f"brief value for {key!r} is not a scalar")
        if isinstance(value, float) and not math.isfinite(value):
            raise Rejected(f"brief value for {key!r} is not a finite number")
    return raw


def grader_revision(meta):
    """Which generator produced a stored brief, so a later run can say whether an upgrade
    has moved the question underneath it. Both files it takes to make one are hashed, each
    by its own digest so nothing shifts between them."""
    digest = hashlib.sha256()
    for name in ("grade.py", "solution.yaml"):
        digest.update(hashlib.sha256((meta["dir"] / name).read_bytes()).digest())
    return digest.hexdigest()[:12]


def module_name(slug):
    """A unique module name per task, so two graders cannot share state in selfcheck."""
    return f"drillion_grade_{slug}"


def generate_brief(meta, seed):
    """The requirements for one sitting, produced by the task's own code, in the sandbox.

    The child shares its `sys.argv`, so the grader can write the output file itself instead
    of returning from `brief()`. What comes back is validated either way."""
    grader = meta["dir"] / "grade.py"
    with tempfile.TemporaryDirectory(
        dir=settings.root, ignore_cleanup_errors=True
    ) as scratch:
        scratch = Path(scratch)
        script = scratch / "_brief.py"
        script.write_text(_BRIEF_SOURCE, encoding="utf-8")
        out = scratch / "brief.json"
        try:
            result = sandbox.run_script(
                [
                    str(script),
                    str(grader),
                    str(seed),
                    str(out),
                    module_name(meta["dir"].name),
                ],
                scratch,
                BRIEF_SECONDS,
            )
        except subprocess.TimeoutExpired:
            raise Rejected("brief() did not finish") from None
        if result.returncode != 0:
            raise Rejected(f"brief() failed: {result.stderr.strip()[-500:]}")
        return _read_brief(out)


def _read_brief(out):
    """Read back what the child wrote, as the one file object the size check looked at.

    The child owns the scratch directory, so it can unlink `out` and leave a symlink or a
    fifo in its place. `O_NOFOLLOW` keeps the parent from becoming a confused deputy for a
    file the sandbox denies the child, `O_NONBLOCK` keeps a fifo from wedging this thread,
    and `fstat` measures the fd rather than the name, so nothing can be swapped in between."""
    try:
        fd = os.open(out, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except OSError:
        raise Rejected("brief() wrote nothing") from None
    with open(fd, encoding="utf-8") as stream:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise Rejected("brief() wrote something that is not a plain file")
        if info.st_size > MAX_BRIEF_BYTES:
            raise Rejected("brief() wrote too much")
        try:
            return _validated(json.loads(stream.read()))
        except ValueError as exc:
            raise Rejected(f"brief() is not valid JSON: {exc}") from None


def render(template, brief):
    """Plain-text substitution for a README. Doubled braces stay literal, as in str.format.

    Every way a placeholder can go wrong is a task-authoring bug, so they all come back as
    `Rejected`: a missing name, a malformed spec, and the attribute and index traversal that
    `{name.title}` and `{replicas[0]}` ask for. The length bound is here because a width like
    `{name:>1000000000}` allocates in the one process that has no `RLIMIT_AS`."""
    try:
        filled = template.format(**brief)
    except (LookupError, ValueError, AttributeError, TypeError, MemoryError) as exc:
        raise Rejected(f"the spec template does not match the brief: {exc}") from None
    if len(filled) > MAX_SPEC_CHARS:
        raise Rejected("the filled spec is too long")
    return filled
