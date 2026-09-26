"""A git sitting's repository: where it lives, how it is built, and the environment every
git in it runs with, the learner's shell, its setup and its grader alike."""

import collections
import functools
import json
import os
import re
import shutil
import stat
import subprocess
import threading
from pathlib import Path

from . import manifest, sandbox
from .settings import settings

MIN_VERSION = (2, 40)
SITTINGS = ".sittings"
STAMP = ".started"
SETUP_SECONDS = 30
GITCONFIG = """\
[user]
\tname = You
\temail = you@drillion.invalid
[init]
\tdefaultBranch = main
"""
# ponytail: one lock per slug ever opened, never pruned; a few hundred at most
_locks = collections.defaultdict(threading.Lock)

# Runs inside the sandbox with the job's path as argv[1]; the sitting being built is its
# scratch and its working directory.
_SETUP_SOURCE = """
try:
    import drillion.guard
except ImportError, OSError:
    pass

import importlib.util, json, sys
from pathlib import Path

job = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
sys.path.insert(0, job["tasks"])
import _git

spec = importlib.util.spec_from_file_location(job["module"], job["grader"])
grade = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grade)
try:
    _git.build(Path("."), grade.setup, job["brief"])
except Exception as exc:
    print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
    sys.exit(1)
"""


def _git_says():
    return subprocess.run(
        ["git", "--version"], capture_output=True, text=True, check=True, timeout=10
    ).stdout


@functools.cache
def version():
    """git's version as `2.47.3`, or None when there is no git on PATH."""
    try:
        said = _git_says()
    except OSError, subprocess.SubprocessError:
        return None
    found = re.search(r"\d+\.\d+(?:\.\d+)?", said)
    return found.group(0) if found else None


def require():
    """The version, or `ToolMissing` naming what to install. Never the learner's mistake."""
    found = version()
    if found is None:
        raise manifest.ToolMissing("git is not installed: install git 2.40 or newer")
    if tuple(int(p) for p in found.split(".")[:2]) < MIN_VERSION:
        raise manifest.ToolMissing(f"git {found} is older than 2.40: upgrade it")
    return found


def home(slug):
    return settings.root / SITTINGS / slug


def environ(sitting):
    """What every git in a sitting runs with: it never walks up out of `.sittings`, never
    reads the machine's config, and reaches no remote but a local path."""
    sitting = Path(sitting)
    return {
        "GIT_CEILING_DIRECTORIES": str(sitting.parent),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": str(sitting / "home" / ".gitconfig"),
        "GIT_ALLOW_PROTOCOL": "file",
        "GIT_TERMINAL_PROMPT": "0",
    }


def stamp(meta, o):
    """Which sitting, and which version of the task, a repository was built for."""
    return f"{o['started']} {manifest.grader_revision(meta)}"


def ensure(meta, o):
    """(the sitting's directory, whether a repository was replaced because the task
    changed). Built from the sitting's stored brief unless the one on disk is already this
    sitting's, into a fresh directory that is renamed into place, so a crash mid-build
    never leaves half a repository behind."""
    require()
    slug = meta["dir"].name
    want = stamp(meta, o)
    with _locks[slug]:
        where = home(slug)
        try:
            had = (where / STAMP).read_text(encoding="utf-8")
        except OSError:
            had = None
        if had == want:
            return where, False
        fresh = where.with_name(f".{slug}.new")
        _remove(fresh)
        (fresh / "home").mkdir(parents=True)
        (fresh / "home" / ".gitconfig").write_text(GITCONFIG, encoding="utf-8")
        try:
            _setup(meta, o["brief"], fresh)
        except BaseException:
            _remove(fresh)
            raise
        (fresh / STAMP).write_text(want, encoding="utf-8")
        _remove(where)
        fresh.rename(where)
        # the same sitting, a different task: what the learner did there is gone
        return where, bool(had) and had.split()[0] == o["started"]


def discard(slug):
    with _locks[slug]:
        _remove(home(slug))


def _remove(path):
    """rmtree that gives a directory its write bit back and tries again, so a learner's
    `chmod -R a-w` never pins a sitting in place."""

    def retry(func, name, _exc):
        parent = os.path.dirname(name)
        os.chmod(parent, os.stat(parent).st_mode | stat.S_IWUSR | stat.S_IXUSR)
        func(name)

    if path.exists():
        shutil.rmtree(path, onexc=retry)


def _setup(meta, brief, where):
    """The task's `setup()` in the sandbox, with `where` as its scratch."""
    script, job = where / "_setup.py", where / "_setup.json"
    script.write_text(_SETUP_SOURCE, encoding="utf-8")
    job.write_text(
        json.dumps(
            {
                "tasks": str(settings.tasks_dir),
                "grader": str(meta["dir"] / "grade.py"),
                "module": manifest.module_name(meta["dir"].name),
                "brief": brief,
            }
        ),
        encoding="utf-8",
    )
    try:
        done = sandbox.run_script(
            [str(script), str(job)], where, SETUP_SECONDS, **environ(where)
        )
    except subprocess.TimeoutExpired:
        raise manifest.Rejected("setup() did not finish") from None
    finally:
        script.unlink(missing_ok=True)
        job.unlink(missing_ok=True)
    if done.returncode != 0:
        raise manifest.Rejected(f"setup() failed: {done.stderr.strip()[-500:]}")
