"""Every git task's answer key passes, and every broken version of it fails, through the
real pipeline: setup in the sandbox, the commands typed, the repositories compared."""

import pytest

from drillion import catalogue, gitrepo, kinds, manifest, runner

pytestmark = pytest.mark.skipif(gitrepo.version() is None, reason="needs git")

# (what in solution.sh, what to put instead); `{name}` and the like are the brief's
BREAKS = {
    "339_git_first_commit": [
        ("'{secret}'", "'*.log'"),
        ("add the {app}", "add {app}"),
        ("git add .gitignore {app}.py test_{app}.py", "git add .gitignore {app}.py"),
    ],
    "340_git_stage_part_of_a_file": [
        ("printf 'y\\nn\\n'", "printf 'y\\ny\\n'"),
        ("read settings as UTF-8", "fix encoding"),
    ],
    "341_git_fix_the_last_commit": [
        ("--amend ", ""),
        ("git add test_{app}.py\n", ""),
    ],
    "342_git_undo_changes": [
        ("git restore --staged notes.md", "git restore --staged --worktree notes.md"),
        ("git restore app.py\n", ""),
    ],
    "343_git_stash_and_switch": [
        ("git stash pop", "true"),
        ("git switch main\n", ""),
    ],
    "344_git_find_the_commit": [
        ("tail -n 1", "head -n 1"),
        (" -- docs/", ""),
    ],
    "345_git_merge_a_branch": [
        ("git merge --ff-only feature/{a}", "git merge --no-ff --no-edit feature/{a}"),
        ("git branch -d feature/{a} feature/{b}", "git branch -d feature/{a}"),
    ],
    "346_git_resolve_a_conflict": [
        ("git commit --no-edit", "true"),
        ("'port = {port}'", "'port = {theirs}'"),
    ],
    "347_git_backport_a_fix": [
        (
            "git cherry-pick \"$(git log main --format=%H --grep='^fix {bug}$')\"",
            "git merge --no-edit main",
        ),
        ("git switch main", "true"),
    ],
    "348_git_tidy_a_branch": [
        (" -e '5s/^pick/drop/'", ""),
        (" -e '4s/^pick/reword/'", ""),
    ],
    "349_git_fixup_commits": [
        (" --autosquash", ""),
    ],
    "350_git_rebase_onto_main": [
        ("git rebase main || true", "git merge --no-edit main || true"),
        ("git branch -d feature/{feature}", "true"),
    ],
}


def _git_tasks():
    return {s: m for s, m in catalogue.tasks().items() if m.get("kind") == "git"}


def _filled(part, brief):
    for key, value in brief.items():
        part = part.replace(f"{{{key}}}", str(value))
    return part


def _grade(meta, brief, script):
    passed, diagnostics, *_ = runner.run_manifest(
        meta, brief, git=gitrepo.job(meta, brief, script=script)
    )
    return passed, diagnostics


@pytest.fixture(autouse=True)
def _isolated(monkeypatch):
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", "/dev/null")
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")


def test_every_git_task_has_its_rules_listed():
    assert set(_git_tasks()) == set(BREAKS)


@pytest.mark.parametrize("slug", sorted(BREAKS))
@pytest.mark.parametrize("seed", [0, 1, 2])
def test_the_answer_key_passes_and_nothing_done_fails(slug, seed):
    meta = _git_tasks()[slug]
    brief = manifest.generate_brief(meta, seed)
    assert _grade(meta, brief, kinds.of(meta).answer_key(meta, brief)) == (True, [])
    assert not _grade(meta, brief, None)[0]


@pytest.mark.parametrize(
    ("slug", "row"),
    [
        pytest.param(s, row, id=f"{s[:3]}-{i}")
        for s, rows in sorted(BREAKS.items())
        for i, row in enumerate(rows)
    ],
)
def test_every_broken_rule_fails(slug, row):
    meta = _git_tasks()[slug]
    brief = manifest.generate_brief(meta, 0)
    key = kinds.of(meta).answer_key(meta, brief)
    old, new = (_filled(part, brief) for part in row)
    assert old in key, (slug, old)
    passed, diagnostics = _grade(meta, brief, key.replace(old, new))
    assert not passed and diagnostics, (slug, old)
