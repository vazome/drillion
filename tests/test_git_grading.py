"""How two repositories are compared: content ids, the default probes, the messages."""

import asyncio
import importlib.util
import os
import shutil
import subprocess
import threading
from datetime import datetime

import httpx
import pytest

from drillion import gitrepo, grading, kinds, manifest
from drillion.api import app
from drillion.settings import settings
from tests.fixtures import tasks_root
from tests.fixtures_git import fixture_task

SLUG = "900_git_fixture"


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


def test_an_unstaged_change_that_holds_the_wrong_text_is_named(git, tmp_path):
    def setup(repo, _b):
        repo.commit("start", {"notes.md": "- one\n"})

    mine, key = _two(git, tmp_path, setup)
    git.Repo(key / "repo").write("notes.md", "- one\n- the note\n")
    git.Repo(mine / "repo").write("notes.md", "the note was lost\n")
    assert _diff(git, mine, key) == "notes.md does not hold what it should (not staged)"
    git.Repo(mine / "repo").write("notes.md", "- one\n- the note\n")
    assert _diff(git, mine, key) is None


def test_a_staged_change_that_holds_the_wrong_text_is_named(git, tmp_path):
    def setup(repo, _b):
        repo.commit("start", {"a.txt": "a\n"})

    mine, key = _two(git, tmp_path, setup)
    for root, text in ((mine, "wrong\n"), (key, "right\n")):
        r = git.Repo(root / "repo")
        r.write("a.txt", text)
        r.git("add", "a.txt")
    assert _diff(git, mine, key) == "a.txt does not hold what it should (staged)"


def test_an_untracked_file_that_holds_the_wrong_text_is_named(git, tmp_path):
    mine, key = _two(git, tmp_path, _base)
    git.Repo(mine / "repo").write("new.txt", "mine\n")
    git.Repo(key / "repo").write("new.txt", "key\n")
    assert _diff(git, mine, key) == "new.txt does not hold what it should (not staged)"


def test_a_stash_that_holds_another_edit_is_named(git, tmp_path):
    def setup(repo, _b):
        repo.commit("start", {"a.txt": "a\n"})
        repo.write("a.txt", "half done\n")
        repo.git("stash", "-q")

    mine, key = _two(git, tmp_path, setup)
    assert _diff(git, mine, key) is None
    r = git.Repo(mine / "repo")
    r.git("stash", "drop", "-q")
    r.write("a.txt", "something else\n")
    r.git("stash", "-q")
    assert _diff(git, mine, key) == "the stash's 1st entry does not hold what it should"


def test_a_fifo_in_the_working_tree_is_never_opened(git, tmp_path):
    def setup(repo, _b):
        repo.commit("start", {"a.txt": "a\n"})

    mine, key = _two(git, tmp_path, setup)
    git.Repo(key / "repo").write("a.txt", "b\n")
    git.Repo(key / "repo").write("p.txt", "p\n")
    (mine / "repo" / "a.txt").unlink()
    os.mkfifo(mine / "repo" / "a.txt")
    os.mkfifo(mine / "repo" / "p.txt")
    found = []
    t = threading.Thread(
        target=lambda: found.append(_diff(git, mine, key)), daemon=True
    )
    t.start()
    t.join(10)
    assert found and found[0] is not None
    (mine / "repo" / "p.txt").unlink()
    (mine / "repo" / "p.txt").write_text("p\n")
    assert _diff(git, mine, key) == "a.txt does not hold what it should (not staged)"


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


def _git_root():
    """A throwaway tasks/ root holding the fixture git task and the real `_git.py`
    helper, with `settings.root` pointed at it. The caller restores `settings.root`."""
    root, keep = tasks_root(**{SLUG: fixture_task()}), settings.root
    shutil.copy(keep / "tasks" / "_git.py", root / "tasks" / "_git.py")
    settings.root = root
    return root, keep


@pytest.fixture
def task(monkeypatch):
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", "/dev/null")
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    root, keep = _git_root()
    meta = {
        "dir": root / "tasks" / SLUG,
        "path": root / "tasks" / SLUG / "history.sh",
        "kind": "git",
        "spec_md": "",
    }
    o = {
        "started": datetime.now().isoformat(),  # noqa: DTZ005
        "seed": 7,
        **kinds.KINDS["git"].opening(meta, 7),
    }
    yield meta, o
    settings.root = keep
    shutil.rmtree(root, ignore_errors=True)


def test_the_untouched_sitting_fails_and_the_answer_passes(task):
    meta, o = task
    kind = kinds.KINDS["git"]
    passed, detail = kind.grade(meta, o, "")
    name = o["brief"]["name"]
    assert not passed
    assert detail["headline"] == [
        f'main is missing 1 commit, starting with "add {name}"'
    ]
    repo = gitrepo.home(SLUG) / "repo"
    env = {**os.environ, **gitrepo.environ(gitrepo.home(SLUG))}
    subprocess.run(["git", "add", f"{name}.md"], cwd=repo, env=env, check=True)
    subprocess.run(
        ["git", "commit", "-qm", f"add {name}"], cwd=repo, env=env, check=True
    )
    assert kind.grade(meta, o, "")[0]


def _commit_the_answer(meta, o):
    """Make the fixture's answer in the sitting, as a learner would type it."""
    where = gitrepo.ensure(meta, o)[0]
    env = {**os.environ, **gitrepo.environ(where)}
    name = o["brief"]["name"]
    for argv in (["add", f"{name}.md"], ["commit", "-qm", f"add {name}"]):
        subprocess.run(["git", *argv], cwd=where / "repo", env=env, check=True)


def test_the_fixture_self_checks(task):
    meta, _ = task
    files, judge = kinds.KINDS["git"].selfcheck(meta)
    assert files == {} and judge() == (True, "")


def test_a_task_whose_untouched_repository_passes_fails_its_self_check(task):
    meta, _ = task
    (meta["dir"] / "solution.sh").write_text("true\n")
    passed, why = kinds.KINDS["git"].selfcheck(meta)[1]()
    assert not passed and "untouched" in why


def test_a_task_changed_under_a_sitting_is_refused_and_rebuilt(task):
    meta, o = task
    gitrepo.ensure(meta, o)
    grader = meta["dir"] / "grade.py"
    grader.write_text(grader.read_text() + "\n# changed\n")
    with pytest.raises(manifest.Rejected, match="changed since you started"):
        kinds.KINDS["git"].grade(meta, o, "")
    assert (
        gitrepo.ensure(meta, o)[1] is False
    )  # already rebuilt: the next grade is fair


def test_a_check_that_crashes_names_a_broken_task(task):
    meta, o = task
    grader = meta["dir"] / "grade.py"
    grader.write_text(
        grader.read_text() + "\n\ndef check(repo, b):\n    raise RuntimeError('boom')\n"
    )
    _commit_the_answer(meta, o)
    with pytest.raises(manifest.Rejected, match="grader could not read") as caught:
        kinds.KINDS["git"].grade(meta, o, "")
    assert "RuntimeError: boom" in str(caught.value)


def test_an_origin_only_the_answer_key_makes_is_named(task):
    meta, o = task
    solution = meta["dir"] / "solution.sh"
    solution.write_text(solution.read_text() + "git init -q --bare ../origin.git\n")
    _commit_the_answer(meta, o)
    assert kinds.KINDS["git"].grade(meta, o, "")[1]["headline"] == [
        "there is no origin repository"
    ]


def test_a_verdict_is_fingerprinted_by_git_and_moves_with_the_helper(task):
    meta, _ = task
    before = kinds.KINDS["git"].revision(meta, "")
    assert before.startswith("g1:")
    helper = settings.tasks_dir / "_git.py"
    helper.write_text(helper.read_text() + "\n# changed\n")
    assert kinds.KINDS["git"].revision(meta, "") != before


@pytest.fixture
def api_root(monkeypatch):
    """The fixture git task, reachable through the real HTTP routes rather than by
    calling a kind directly: what `save_task` and `run_task` do to `history.sh`."""
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", "/dev/null")
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    root, keep = _git_root()
    yield root
    settings.root = keep
    shutil.rmtree(root, ignore_errors=True)


def _run(flow):
    async def drive():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://127.0.0.1"
        ) as api:
            await flow(api)

    asyncio.run(drive())


def test_a_save_leaves_historys_content_and_inode_unchanged_and_returns_the_etag(
    api_root,
):
    path = settings.tasks_dir / SLUG / "history.sh"
    path.write_text("git status\n", encoding="utf-8")
    before = os.stat(path).st_ino

    async def flow(api):
        opened = (await api.post(f"/api/task/{SLUG}/open")).json()
        saved = await api.put(
            f"/api/task/{SLUG}",
            json={"code": "echo mine\n", "etag": opened["etag"]},
        )
        assert saved.status_code == 200, saved.text
        assert saved.json() == {"etag": opened["etag"]}

    _run(flow)
    assert path.read_text(encoding="utf-8") == "git status\n"
    assert os.stat(path).st_ino == before


def test_a_run_leaves_historys_content_and_inode_unchanged(api_root):
    path = settings.tasks_dir / SLUG / "history.sh"
    path.write_text("git status\n", encoding="utf-8")
    before = os.stat(path).st_ino

    async def flow(api):
        opened = (await api.post(f"/api/task/{SLUG}/open")).json()
        run = await api.post(
            f"/api/task/{SLUG}/run",
            json={"code": "echo mine\n", "etag": opened["etag"], "submit": False},
        )
        assert run.status_code == 200, run.text

    _run(flow)
    assert path.read_text(encoding="utf-8") == "git status\n"
    assert os.stat(path).st_ino == before
