"""A git sitting's repository: where it lives, how it is built, and the environment every
git in it runs with, the learner's shell, its setup and its grader alike."""

import functools
import re
import subprocess

from . import manifest

MIN_VERSION = (2, 40)


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
