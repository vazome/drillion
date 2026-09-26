"""`tasks/_git.py`: the same setup always makes the same repository."""

import importlib.util

import pytest

from drillion.settings import settings


def _load():
    spec = importlib.util.spec_from_file_location(
        "_git", settings.tasks_dir / "_git.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def git(monkeypatch):
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", "/dev/null")
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    return _load()


def _setup(repo, b):
    repo.commit("start", {"README.md": "# x\n"})
    repo.git("switch", "-q", "-c", "feature")
    repo.commit(f"add {b['name']}", {f"{b['name']}.py": "x = 1\n"})


def test_the_same_setup_makes_the_same_shas(git, tmp_path):
    one = git.build(tmp_path / "one", _setup, {"name": "a"})
    two = git.build(tmp_path / "two", _setup, {"name": "a"})
    assert git.Repo(one / "repo").ref("feature") == git.Repo(two / "repo").ref(
        "feature"
    )


def test_every_commit_is_a_minute_after_the_last(git, tmp_path):
    root = git.build(tmp_path / "r", _setup, {"name": "a"})
    stamps = git.Repo(root / "repo").git("log", "--format=%ct", "feature").split()
    assert [int(s) for s in stamps] == [git.EPOCH + 120, git.EPOCH + 60]


def test_a_teammate_pushes_to_origin_and_leaves_no_clone(git, tmp_path):
    def setup(repo, b):
        repo.origin()
        repo.commit("start", {"README.md": "# x\n"})
        repo.git("push", "-q", "-u", "origin", "main")
        mate = repo.teammate()
        mate.commit("teammate change", {"ci.yml": "steps: []\n"})
        mate.git("push", "-q", "origin", "main")

    root = git.build(tmp_path / "r", setup, {})
    assert git.Repo(root / "origin.git").log("main") == ["teammate change", "start"]
    assert not (root / "teammate").exists()


def test_log_is_the_first_parent_subjects_newest_first(git, tmp_path):
    root = git.build(tmp_path / "r", _setup, {"name": "a"})
    assert git.Repo(root / "repo").log("feature") == ["add a", "start"]
    assert git.Repo(root / "repo").ref("nope") is None
