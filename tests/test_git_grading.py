"""How two repositories are compared: content ids, the default probes, the messages."""

import importlib.util

import pytest

from drillion import grading
from drillion.settings import settings


@pytest.fixture
def git(monkeypatch):
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", "/dev/null")
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.setenv("GIT_OPTIONAL_LOCKS", "0")
    spec = importlib.util.spec_from_file_location(
        "_git", settings.tasks_dir / "_git.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _two(git, tmp_path, setup):
    return git.build(tmp_path / "mine", setup, {}), git.build(
        tmp_path / "key", setup, {}
    )


def _diff(git, mine, key, start=None, skip=()):
    m, k = grading.git_state(git, mine), grading.git_state(git, key)
    return grading.git_difference(m[""], k[""], (start or k)[""], set(skip))


def _base(repo, _b):
    repo.commit("start", {"a.txt": "a\n"})


def test_the_same_history_on_another_day_is_equal(git, tmp_path):
    mine, key = _two(git, tmp_path, _base)
    for root, clock in ((mine, 5), (key, 50)):
        r = git.Repo(root / "repo")
        r.clock = clock
        r.commit("add b", {"b.txt": "b\n"})
    assert git.Repo(mine / "repo").ref("main") != git.Repo(key / "repo").ref("main")
    assert _diff(git, mine, key) is None


def test_a_different_subject_is_named(git, tmp_path):
    mine, key = _two(git, tmp_path, _base)
    git.Repo(mine / "repo").commit("wip", {"b.txt": "b\n"})
    git.Repo(key / "repo").commit("add b", {"b.txt": "b\n"})
    assert _diff(git, mine, key) == 'main: its 2nd commit is "wip", expected "add b"'


def test_different_files_under_the_same_subject_are_named(git, tmp_path):
    mine, key = _two(git, tmp_path, _base)
    git.Repo(mine / "repo").commit("add b", {"b.txt": "B\n"})
    git.Repo(key / "repo").commit("add b", {"b.txt": "b\n"})
    assert _diff(git, mine, key) == 'main: "add b" does not hold the files it should'


def test_a_missing_commit_and_an_extra_one_are_counted(git, tmp_path):
    mine, key = _two(git, tmp_path, _base)
    git.Repo(key / "repo").commit("add b", {"b.txt": "b\n"})
    assert _diff(git, mine, key) == 'main is missing 1 commit, starting with "add b"'
    assert _diff(git, key, mine) == 'main has 1 commit too many, starting with "add b"'


def test_a_merge_the_other_way_round_differs(git, tmp_path):
    def setup(repo, _b):
        repo.commit("start", {"a.txt": "a\n"})
        repo.git("switch", "-q", "-c", "side")
        repo.commit("side", {"s.txt": "s\n"})
        repo.git("switch", "-q", "main")
        repo.commit("main", {"m.txt": "m\n"})

    mine, key = _two(git, tmp_path, setup)
    # one message for both merges, so only the order of the parents tells them apart
    git.Repo(key / "repo").git("merge", "-q", "-m", "merge", "side")
    r = git.Repo(mine / "repo")
    r.git("switch", "-q", "side")
    r.git("merge", "-q", "-m", "merge", "main")
    r.git("switch", "-q", "main")
    r.git("reset", "-q", "--hard", "side")
    assert _diff(git, mine, key) is not None


def test_a_branch_the_learner_added_is_ignored_and_one_the_key_deleted_is_not(
    git, tmp_path
):
    def setup(repo, _b):
        repo.commit("start", {"a.txt": "a\n"})
        repo.git("branch", "old")

    mine, key = _two(git, tmp_path, setup)
    start = grading.git_state(git, key)
    git.Repo(key / "repo").git("branch", "-q", "-D", "old")
    git.Repo(mine / "repo").git("branch", "backup")
    m, k = grading.git_state(git, mine), grading.git_state(git, key)
    assert (
        grading.git_difference(m[""], k[""], start[""], set()) == "old should be gone"
    )


def test_an_operation_in_progress_comes_first(git, tmp_path):
    def setup(repo, _b):
        repo.commit("start", {"a.txt": "a\n"})
        repo.git("switch", "-q", "-c", "side")
        repo.commit("side", {"a.txt": "side\n"})
        repo.git("switch", "-q", "main")
        repo.commit("main", {"a.txt": "main\n"})

    mine, key = _two(git, tmp_path, setup)
    git.Repo(mine / "repo").git("merge", "side", check=False)
    assert _diff(git, mine, key).startswith("a merge is still in progress")


def test_head_status_and_stash_are_each_named(git, tmp_path):
    mine, key = _two(git, tmp_path, _base)
    r = git.Repo(mine / "repo")
    r.git("switch", "-q", "-c", "other")
    assert _diff(git, mine, key) == "HEAD is on other, expected main"
    r.git("switch", "-q", "main")
    r.write("new.txt", "n\n")
    assert _diff(git, mine, key) == (
        "the working tree or the staging area is not as it should be: "
        "expected nothing to commit, found ?? new.txt"
    )
    r.git("stash", "-u")
    assert _diff(git, mine, key) == "the stash holds 1 entry, expected 0"
    assert _diff(git, mine, key, skip={"stash"}) is None


def test_a_fsmonitor_in_the_learners_config_never_runs(git, tmp_path):
    mine, _key = _two(git, tmp_path, _base)
    marker = tmp_path / "ran"
    git.Repo(mine / "repo").git("config", "core.fsmonitor", f"touch {marker}; false")
    grading.git_state(git, mine)
    assert not marker.exists()


def test_a_held_index_lock_does_not_stop_the_grade(git, tmp_path):
    mine, key = _two(git, tmp_path, _base)
    (mine / "repo" / ".git" / "index.lock").write_text("")
    assert _diff(git, mine, key) is None


def test_origin_is_compared_by_its_refs(git, tmp_path):
    def setup(repo, _b):
        repo.origin()
        repo.commit("start", {"a.txt": "a\n"})
        repo.git("push", "-q", "-u", "origin", "main")

    mine, key = _two(git, tmp_path, setup)
    start = grading.git_state(git, key)
    k = git.Repo(key / "repo")
    k.commit("add b", {"b.txt": "b\n"})
    k.git("push", "-q")
    git.Repo(mine / "repo").commit("add b", {"b.txt": "b\n"})
    m, kk = grading.git_state(git, mine), grading.git_state(git, key)
    assert grading.git_difference(m[""], kk[""], start[""], set()) == (
        'origin/main is missing 1 commit, starting with "add b"'
    )
    assert grading.git_difference(
        m[" on origin"], kk[" on origin"], start[" on origin"], set(), " on origin"
    ) == ('main on origin is missing 1 commit, starting with "add b"')
