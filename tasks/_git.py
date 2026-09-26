"""The repository a git task's `setup()` builds and its `check()` reads.

Every commit a setup makes is one minute after the last from a fixed epoch, by a fixed
author, so one brief always yields the same SHAs. Every command runs with the switches a
repository's own config could use to run something turned off, since a grader reads the
learner's repository with this too."""

import os
import shutil
import subprocess
from pathlib import Path

# 2026-01-05 09:00 UTC, a Monday
EPOCH = 1767603600
AUTHOR = ("Ada Lovelace", "ada@example.com")
SAFE = (
    "-c",
    "core.fsmonitor=false",
    "-c",
    "core.hooksPath=/dev/null",
    "-c",
    "log.showSignature=false",
)


class Repo:
    def __init__(self, path):
        self.path = Path(path)
        self.clock = 0

    @classmethod
    def init(cls, path, bare=False):
        Path(path).mkdir(parents=True, exist_ok=True)
        repo = cls(path)
        repo.git("init", "-q", "-b", "main", *(["--bare"] if bare else []))
        return repo

    def git(self, *args, check=True):
        """git's stdout, run in this repository at this repository's clock."""
        stamp = f"@{EPOCH + 60 * self.clock} +0000"
        env = {
            **os.environ,
            "GIT_AUTHOR_DATE": stamp,
            "GIT_COMMITTER_DATE": stamp,
            "GIT_AUTHOR_NAME": AUTHOR[0],
            "GIT_AUTHOR_EMAIL": AUTHOR[1],
            "GIT_COMMITTER_NAME": AUTHOR[0],
            "GIT_COMMITTER_EMAIL": AUTHOR[1],
        }
        done = subprocess.run(
            ["git", *SAFE, "-C", str(self.path), *args],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        if check and done.returncode:
            raise RuntimeError(f"git {' '.join(args)}: {done.stderr.strip()}")
        return done.stdout

    def write(self, name, text):
        path = self.path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def commit(self, message, files=None, author=None):
        """Write `files` ({path: text}), stage them and commit, a minute after the last
        commit; returns the new SHA. `author` is `"Name <email>"`."""
        for name, text in (files or {}).items():
            self.write(name, text)
            self.git("add", "--", name)
        self.clock += 1
        self.git(
            "commit", "-q", "-m", message, *([f"--author={author}"] if author else [])
        )
        return self.ref("HEAD")

    def ref(self, name):
        """The commit `name` points at, or None."""
        out = self.git("rev-parse", "-q", "--verify", f"{name}^{{commit}}", check=False)
        return out.strip() or None

    def log(self, ref="HEAD"):
        """The subjects on `ref`'s first-parent line, newest first."""
        return self.git("log", "--first-parent", "--format=%s", ref, "--").splitlines()

    def origin(self):
        """A bare `origin.git` beside this repository, added as its `origin`. Relative, so
        the sitting can be moved into place after it is built."""
        bare = Repo.init(self.path.parent / "origin.git", bare=True)
        self.git("remote", "add", "origin", "../origin.git")
        return bare

    def teammate(self):
        """A second clone of `origin`, for commits that reach the server without the
        learner. `build` deletes it when setup ends."""
        self.git("clone", "-q", "../origin.git", "../teammate")
        mate = Repo(self.path.parent / "teammate")
        mate.clock = self.clock + 100
        return mate


def build(root, setup, brief):
    """Run a task's `setup(repo, brief)` into `root`: the repository at `root/repo`, and
    `origin.git` beside it when the task has a server."""
    root = Path(root)
    setup(Repo.init(root / "repo"), brief)
    shutil.rmtree(root / "teammate", ignore_errors=True)
    return root
