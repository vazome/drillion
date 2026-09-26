"""A git sitting's repository, and the git that builds and grades it."""

import os
import shutil
from datetime import datetime

import pytest

from drillion import gitrepo, kinds, manifest
from drillion.settings import settings
from tests.fixtures import tasks_root
from tests.fixtures_git import fixture_task

SLUG = "900_git_fixture"


def test_the_version_is_the_numbers_git_prints(monkeypatch):
    gitrepo.version.cache_clear()
    monkeypatch.setattr(gitrepo, "_git_says", lambda: "git version 2.47.3\n")
    assert gitrepo.version() == "2.47.3"
    gitrepo.version.cache_clear()


def test_an_old_git_is_refused_with_the_floor(monkeypatch):
    monkeypatch.setattr(gitrepo, "version", lambda: "2.34.1")
    with pytest.raises(manifest.ToolMissing, match="2.40"):
        gitrepo.require()


def test_no_git_is_refused_with_the_install(monkeypatch):
    monkeypatch.setattr(gitrepo, "version", lambda: None)
    with pytest.raises(manifest.ToolMissing, match="git is not installed"):
        gitrepo.require()


@pytest.fixture
def sitting(monkeypatch):
    """A throwaway root holding the fixture task and `_git.py`, and an opened sitting."""
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", "/dev/null")
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    root, keep = tasks_root(**{SLUG: fixture_task()}), settings.root
    shutil.copy(keep / "tasks" / "_git.py", root / "tasks" / "_git.py")
    settings.root = root
    meta = {
        "dir": root / "tasks" / SLUG,
        "path": root / "tasks" / SLUG / "history.sh",
        "kind": "git",
    }
    o = {
        "started": datetime.now().isoformat(),  # noqa: DTZ005
        "seed": 7,
        **kinds.KINDS["git"].opening(meta | {"spec_md": ""}, 7),
    }
    yield meta, o
    settings.root = keep
    shutil.rmtree(root, ignore_errors=True)


def test_a_sitting_is_built_once_and_kept(sitting):
    meta, o = sitting
    where, replaced = gitrepo.ensure(meta, o)
    assert (where / "repo" / ".git").is_dir() and not replaced
    (where / "repo" / "mine.txt").write_text("kept\n")
    assert gitrepo.ensure(meta, o) == (where, False)
    assert (where / "repo" / "mine.txt").exists()


def test_another_sitting_gets_a_fresh_repository(sitting):
    meta, o = sitting
    where, _ = gitrepo.ensure(meta, o)
    (where / "repo" / "mine.txt").write_text("old\n")
    where, replaced = gitrepo.ensure(meta, o | {"started": "2027-01-01T00:00:00"})
    assert not (where / "repo" / "mine.txt").exists() and not replaced


def test_a_read_only_repository_is_still_replaced(sitting):
    meta, o = sitting
    where, _ = gitrepo.ensure(meta, o)
    for base, dirs, _files in os.walk(where / "repo"):
        for d in dirs:
            os.chmod(os.path.join(base, d), 0o500)
    # unreadable, not just unwritable: `os.open`/`os.scandir` can't even enter it
    os.chmod(where / "repo" / ".git" / "objects", 0o000)
    gitrepo.discard(meta["dir"].name)
    assert not where.exists()


def test_a_setup_that_fails_says_so(sitting):
    meta, o = sitting
    (meta["dir"] / "grade.py").write_text(
        (meta["dir"] / "grade.py").read_text()
        + "\n\ndef setup(repo, b):\n    raise ValueError('boom')\n"
    )
    with pytest.raises(manifest.Rejected, match="setup\\(\\) failed.*boom"):
        gitrepo.ensure(meta, o)
    assert not gitrepo.home(SLUG).exists()
