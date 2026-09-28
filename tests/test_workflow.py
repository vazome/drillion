"""Workflow tasks: every rule a README states is one its grader enforces, and the real
pipeline, actionlint in the sandbox, judges the answer key and the mistakes it exists for.

The rows below break exactly one displayed rule each and must fail. A rule with no row
here is a rule a wrong workflow can pass."""

import copy
import random
import uuid

import pytest
import yaml

from drillion import catalogue, kinds, manifest, runner, tools
from drillion.grading import WorkflowLoader
from tests.test_graders import BIG, DOUBLE, DROP, WRONG, _broken, _grader

_J = lambda name: ("jobs", name)
_S = lambda name, i: ("jobs", name, "steps", i)
_M = ("jobs", "test", "strategy", "matrix")
_WC = ("on", "workflow_call")
SECRET = "${{ secrets.AZURE_CREDENTIALS }}"
EXTRA = {"runs-on": "ubuntu-latest", "steps": [{"run": "true"}]}

BREAKS = {
    "371_gha_first_workflow": [
        (("name",), WRONG),
        (("on", "push"), DROP),
        (("on", "push", "branches"), ["develop"]),
        (("on", "pull_request"), {"branches": ["main"]}),
        (("on", "workflow_dispatch"), None),
        (("jobs", "lint"), EXTRA),
        ((*_J("test"), "runs-on"), "windows-latest"),
        ((*_J("test"), "steps"), DOUBLE),
        ((*_S("test", 0), "uses"), "actions/cache@v6"),
        ((*_S("test", 1), "uses"), "actions/setup-node@v6"),
        ((*_S("test", 1), "with", "python-version"), 3.1),
        ((*_S("test", 1), "with", "cache"), "pip"),
        ((*_S("test", 2), "run"), "pip install ."),
        ((*_S("test", 3), "run"), "pytest -x"),
    ],
    "372_gha_path_filters": [
        (("name",), WRONG),
        (("on", "push", "branches"), ["develop"]),
        (("on", "push", "paths"), DOUBLE),
        (("on", "push", "paths", 0), "services/**"),
        (("on", "push", "paths", 1), "docs/**"),
        (("on", "pull_request", "branches"), ["main"]),
        (("on", "pull_request", "paths"), DOUBLE),
        (("on", "pull_request", "paths", 1), WRONG),
        (("on", "workflow_dispatch"), DROP),
        (("on", "workflow_dispatch", "inputs", "environment", "type"), "string"),
        (("on", "workflow_dispatch", "inputs", "environment", "options"), ["staging"]),
        (("on", "workflow_dispatch", "inputs", "environment", "default"), "production"),
        (("on", "workflow_dispatch", "inputs", "dry-run"), {"type": "boolean"}),
        (("on", "schedule"), [{"cron": "0 3 * * *"}]),
        (("jobs", "other"), EXTRA),
        ((*_J("build"), "runs-on"), WRONG),
        ((*_J("build"), "steps"), DOUBLE),
        ((*_S("build", 0), "uses"), "actions/cache@v6"),
        ((*_S("build", 1), "run"), WRONG),
        ((*_S("build", 1), "env"), {"TARGET": "staging"}),
        ((*_S("build", 2), "run"), WRONG),
        ((*_S("build", 2), "env", "TARGET"), "${{ inputs.environment }}"),
        ((*_S("build", 2), "env", "DEBUG"), "1"),
    ],
    "373_gha_needs_and_if": [
        (("name",), WRONG),
        (("on", "push", "branches"), ["develop"]),
        (("on", "pull_request"), {"branches": ["main"]}),
        (("on", "workflow_dispatch"), None),
        (("jobs", "lint"), DROP),
        (("jobs", "release"), EXTRA),
        ((*_J("lint"), "runs-on"), "macos-latest"),
        ((*_J("lint"), "needs"), "test"),
        ((*_J("lint"), "if"), "always()"),
        ((*_J("lint"), "steps"), DOUBLE),
        (_S("lint", 0), {"run": "git clone ."}),
        ((*_S("lint", 1), "run"), "flake8"),
        ((*_J("test"), "needs"), DROP),
        ((*_J("test"), "if"), "success()"),
        ((*_S("test", 1), "run"), WRONG),
        ((*_J("deploy"), "needs"), "test"),
        ((*_J("deploy"), "if"), DROP),
        ((*_J("deploy"), "if"), "github.ref == 'refs/heads/main'"),
        ((*_S("deploy", 1), "run"), WRONG),
    ],
    "374_gha_matrix": [
        (("name",), WRONG),
        (("on",), "pull_request"),
        (("jobs", "lint"), EXTRA),
        ((*_J("test"), "runs-on"), "ubuntu-latest"),
        ((*_J("test"), "strategy", "fail-fast"), True),
        ((*_J("test"), "strategy", "fail-fast"), DROP),
        ((*_M, "os"), ["ubuntu-latest"]),
        ((*_M, "python"), DOUBLE),
        ((*_M, "python"), [3.12, 3.13, 3.14]),
        ((*_M, "exclude"), DROP),
        ((*_M, "exclude", 0, "python"), WRONG),
        ((*_M, "include"), DROP),
        ((*_M, "include", 0, "os"), "ubuntu-latest"),
        ((*_M, "node"), ["22"]),
        ((*_J("test"), "steps"), DOUBLE),
        ((*_S("test", 0), "uses"), "actions/cache@v6"),
        ((*_S("test", 1), "with", "python-version"), "3.14"),
        ((*_S("test", 2), "run"), WRONG),
    ],
    "375_gha_caching": [
        (("name",), WRONG),
        (("on",), "pull_request"),
        ((*_J("test"), "runs-on"), WRONG),
        ((*_M, "python"), ["3.14"]),
        ((*_M, "os"), ["ubuntu-latest"]),
        ((*_J("test"), "steps"), DOUBLE),
        ((*_S("test", 0), "uses"), "actions/cache@v6"),
        ((*_S("test", 1), "with", "python-version"), "3.14"),
        ((*_S("test", 2), "uses"), "actions/setup-node@v6"),
        ((*_S("test", 2), "with", "path"), "~/.npm"),
        ((*_S("test", 2), "with", "key"), "${{ runner.os }}-pip"),
        (
            (*_S("test", 2), "with", "key"),
            "${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}",
        ),
        ((*_S("test", 2), "with", "restore-keys"), DROP),
        ((*_S("test", 2), "with", "restore-keys"), "${{ runner.os }}-"),
        ((*_S("test", 2), "with", "enableCrossOsArchive"), True),
        ((*_S("test", 3), "run"), WRONG),
        ((*_S("test", 4), "run"), WRONG),
    ],
    "376_gha_artifacts": [
        (("name",), WRONG),
        (("on",), "pull_request"),
        (("jobs", "publish"), EXTRA),
        ((*_J("build"), "runs-on"), WRONG),
        ((*_J("build"), "needs"), "check"),
        ((*_J("build"), "steps"), DOUBLE),
        ((*_S("build", 0), "uses"), "actions/cache@v6"),
        ((*_S("build", 1), "run"), WRONG),
        ((*_S("build", 2), "run"), WRONG),
        ((*_S("build", 3), "uses"), "actions/cache@v6"),
        ((*_S("build", 3), "with", "name"), WRONG),
        ((*_S("build", 3), "with", "path"), "dist"),
        ((*_S("build", 3), "with", "retention-days"), BIG),
        ((*_S("build", 3), "with", "retention-days"), DROP),
        ((*_S("build", 3), "with", "overwrite"), True),
        ((*_J("check"), "runs-on"), WRONG),
        ((*_J("check"), "needs"), DROP),
        ((*_J("check"), "steps"), DOUBLE),
        (_S("check", 0), {"uses": "actions/checkout@v7"}),
        ((*_S("check", 0), "with", "name"), WRONG),
        ((*_S("check", 0), "with", "path"), WRONG),
        ((*_S("check", 1), "run"), WRONG),
    ],
    "377_gha_permissions": [
        (("name",), WRONG),
        (("on", "pull_request", "types"), ["opened", "synchronize"]),
        (("on", "push"), None),
        (("permissions",), DROP),
        (("permissions", "contents"), "write"),
        (("permissions", "issues"), "write"),
        (("jobs", "other"), EXTRA),
        ((*_J("label"), "runs-on"), WRONG),
        ((*_J("label"), "permissions", "contents"), DROP),
        ((*_J("label"), "permissions", "pull-requests"), "read"),
        ((*_J("label"), "permissions", "issues"), "write"),
        ((*_J("label"), "steps"), DOUBLE),
        ((*_S("label", 0), "run"), WRONG),
        ((*_S("label", 0), "env", "GH_TOKEN"), "${{ secrets.GITHUB_TOKEN }}"),
        ((*_S("label", 0), "env", "GH_REPO"), DROP),
        ((*_S("label", 0), "env", "NUMBER"), "${{ github.event.number }}"),
        ((*_S("label", 0), "env", "EXTRA"), "1"),
    ],
    "378_gha_azure_oidc": [
        (("name",), WRONG),
        (("on", "push", "branches"), ["develop"]),
        (("on", "pull_request"), None),
        (("jobs", "other"), EXTRA),
        ((*_J("deploy"), "runs-on"), WRONG),
        ((*_J("deploy"), "environment"), "staging"),
        ((*_J("deploy"), "environment"), DROP),
        ((*_J("deploy"), "permissions", "id-token"), DROP),
        ((*_J("deploy"), "permissions", "contents"), DROP),
        ((*_J("deploy"), "permissions", "actions"), "read"),
        ((*_J("deploy"), "env"), {"TOKEN": "${{ secrets.DEPLOY_TOKEN }}"}),
        ((*_J("deploy"), "steps"), DOUBLE),
        ((*_S("deploy", 0), "uses"), "actions/cache@v6"),
        ((*_S("deploy", 1), "uses"), "azure/cli@v2"),
        ((*_S("deploy", 1), "with", "creds"), SECRET),
        ((*_S("deploy", 1), "with", "client-id"), "${{ vars.CLIENT_ID }}"),
        ((*_S("deploy", 1), "with", "tenant-id"), DROP),
        ((*_S("deploy", 2), "run"), WRONG),
        ((*_S("deploy", 3), "run"), WRONG),
    ],
    "379_gha_environments": [
        (("name",), WRONG),
        (("on", "push", "branches"), ["develop"]),
        (("jobs", "deploy-dev"), DROP),
        (("jobs", "deploy-qa"), EXTRA),
        ((*_J("deploy-dev"), "runs-on"), WRONG),
        ((*_J("deploy-dev"), "needs"), "deploy-staging"),
        ((*_J("deploy-staging"), "needs"), DROP),
        ((*_J("deploy-production"), "needs"), "deploy-dev"),
        ((*_J("deploy-dev"), "environment", "name"), "development"),
        ((*_J("deploy-staging"), "environment", "url"), WRONG),
        ((*_J("deploy-production"), "environment"), "production"),
        ((*_J("deploy-production"), "environment"), DROP),
        ((*_J("deploy-production"), "concurrency", "group"), "deploy"),
        ((*_J("deploy-production"), "concurrency", "cancel-in-progress"), True),
        ((*_J("deploy-staging"), "concurrency"), DROP),
        ((*_J("deploy-dev"), "steps"), DOUBLE),
        ((*_S("deploy-dev", 0), "uses"), "actions/cache@v6"),
        ((*_S("deploy-dev", 1), "run"), "./deploy.sh staging"),
    ],
    "380_gha_concurrency": [
        (("name",), WRONG),
        (("on", "push", "branches"), ["develop"]),
        (("on", "pull_request"), {"types": ["opened"]}),
        (("concurrency",), DROP),
        (("concurrency",), "ci"),
        (("concurrency", "group"), "${{ github.ref }}"),
        (("concurrency", "group"), "${{ github.workflow }}"),
        (("concurrency", "cancel-in-progress"), True),
        (("concurrency", "cancel-in-progress"), False),
        (("concurrency", "cancel-in-progress"), DROP),
        (("jobs", "lint"), EXTRA),
        ((*_J("test"), "runs-on"), WRONG),
        ((*_J("test"), "concurrency"), {"group": "test"}),
        ((*_J("test"), "steps"), DOUBLE),
        ((*_S("test", 0), "uses"), "actions/cache@v6"),
        ((*_S("test", 1), "run"), WRONG),
    ],
    "381_gha_reusable_workflow": [
        (("name",), WRONG),
        (("on", "push"), None),
        ((*_WC, "inputs", "image", "required"), False),
        ((*_WC, "inputs", "context", "type"), "number"),
        ((*_WC, "inputs", "context"), DROP),
        ((*_WC, "inputs", "password"), {"type": "string", "required": True}),
        ((*_WC, "secrets"), DROP),
        ((*_WC, "secrets", "REGISTRY_PASSWORD", "required"), False),
        ((*_WC, "outputs"), DROP),
        ((*_WC, "outputs", "digest", "value"), "${{ steps.push.outputs.digest }}"),
        (("jobs", "test"), EXTRA),
        ((*_J("build"), "runs-on"), WRONG),
        ((*_J("build"), "outputs"), DROP),
        ((*_J("build"), "outputs", "digest"), "${{ steps.build.outputs.digest }}"),
        ((*_J("build"), "steps"), DOUBLE),
        ((*_S("build", 0), "uses"), "actions/cache@v6"),
        ((*_S("build", 1), "uses"), "azure/login@v3"),
        ((*_S("build", 1), "with", "registry"), WRONG),
        ((*_S("build", 1), "with", "username"), DROP),
        ((*_S("build", 1), "with", "password"), "${{ inputs.password }}"),
        ((*_S("build", 2), "id"), "build"),
        ((*_S("build", 2), "uses"), "docker/setup-buildx-action@v4"),
        ((*_S("build", 2), "with", "context"), "."),
        ((*_S("build", 2), "with", "push"), False),
        ((*_S("build", 2), "with", "tags"), "acmeshop.azurecr.io/web:latest"),
    ],
    "382_gha_call_reusable_workflow": [
        (("name",), WRONG),
        (("on", "push", "tags"), ["*"]),
        (("on", "push", "branches"), ["main"]),
        (("permissions",), DROP),
        (("permissions", "id-token"), DROP),
        (("permissions", "contents"), "write"),
        (("jobs", "staging"), DROP),
        (("jobs", "dev"), {"uses": "./.github/workflows/deploy.yml"}),
        ((*_J("staging"), "uses"), "./.github/workflows/build.yml"),
        ((*_J("staging"), "runs-on"), "ubuntu-latest"),
        ((*_J("staging"), "with"), DROP),
        ((*_J("staging"), "with", "environment"), "dev"),
        ((*_J("staging"), "with", "image-tag"), "latest"),
        ((*_J("staging"), "needs"), "production"),
        ((*_J("production"), "needs"), DROP),
        ((*_J("production"), "with", "environment"), "staging"),
        ((*_J("production"), "with", "image-tag"), "${{ github.sha }}"),
    ],
    "383_gha_acr_build_push": [
        (("name",), WRONG),
        (("on", "push", "tags"), ["*"]),
        (("on", "push", "branches"), ["main"]),
        (("jobs", "other"), EXTRA),
        ((*_J("image"), "runs-on"), WRONG),
        ((*_J("image"), "permissions", "id-token"), DROP),
        ((*_J("image"), "permissions", "contents"), "write"),
        ((*_J("image"), "steps"), DOUBLE),
        ((*_S("image", 0), "uses"), "actions/cache@v6"),
        ((*_S("image", 1), "uses"), "azure/cli@v2"),
        ((*_S("image", 1), "with", "client-id"), "${{ secrets.AZURE_CLIENT_ID }}"),
        ((*_S("image", 2), "run"), WRONG),
        ((*_S("image", 3), "uses"), "docker/setup-qemu-action@v4"),
        ((*_S("image", 3), "with"), {"driver": "docker"}),
        ((*_S("image", 4), "uses"), "docker/setup-buildx-action@v4"),
        ((*_S("image", 4), "with", "context"), "services/web"),
        ((*_S("image", 4), "with", "push"), False),
        ((*_S("image", 4), "with", "tags"), "acmeshop.azurecr.io/web:latest"),
        ((*_S("image", 4), "with", "cache-from"), DROP),
        ((*_S("image", 4), "with", "cache-to"), "type=gha"),
        ((*_S("image", 4), "with", "platforms"), "linux/amd64,linux/arm64"),
    ],
    "384_gha_release_on_tag": [
        (("name",), WRONG),
        (("on", "push", "tags"), ["v*"]),
        (("permissions",), DROP),
        (("permissions", "contents"), "write"),
        (("jobs", "publish"), EXTRA),
        ((*_J("build"), "runs-on"), WRONG),
        ((*_J("build"), "permissions"), {"contents": "write"}),
        ((*_J("build"), "steps"), DOUBLE),
        ((*_S("build", 0), "uses"), "actions/cache@v6"),
        ((*_S("build", 1), "run"), WRONG),
        ((*_S("build", 2), "run"), WRONG),
        ((*_S("build", 3), "uses"), "actions/cache@v6"),
        ((*_S("build", 3), "with", "name"), WRONG),
        ((*_S("build", 3), "with", "path"), "dist"),
        ((*_S("build", 3), "with", "retention-days"), 5),
        ((*_J("release"), "runs-on"), WRONG),
        ((*_J("release"), "needs"), DROP),
        ((*_J("release"), "permissions"), DROP),
        ((*_J("release"), "permissions", "contents"), "read"),
        ((*_J("release"), "permissions", "packages"), "write"),
        ((*_J("release"), "steps"), DOUBLE),
        ((*_S("release", 0), "uses"), "actions/checkout@v7"),
        ((*_S("release", 0), "with", "name"), WRONG),
        ((*_S("release", 1), "run"), WRONG),
        ((*_S("release", 1), "env", "TAG"), "${{ github.ref }}"),
        ((*_S("release", 1), "env", "GH_REPO"), DROP),
        ((*_S("release", 1), "env", "GH_TOKEN"), "${{ secrets.GITHUB_TOKEN }}"),
    ],
    "385_gha_script_injection": [
        (("name",), WRONG),
        (("on", "issues", "types"), ["opened", "edited"]),
        (("on", "issue_comment"), None),
        (("permissions",), DROP),
        (("permissions", "contents"), "write"),
        (("jobs", "other"), EXTRA),
        ((*_J("triage"), "runs-on"), WRONG),
        ((*_J("triage"), "steps"), DOUBLE),
        (
            (*_S("triage", 0), "run"),
            (
                'echo "New issue: ${{ github.event.issue.title }}"\n'
                'gh issue edit "$NUMBER" --add-label triage\n'
            ),
        ),
        (
            (*_S("triage", 0), "run"),
            'echo "New issue: $TITLE"\ngh issue edit $NUMBER --add-label triage\n',
        ),
        (
            (*_S("triage", 0), "run"),
            'echo New issue: $TITLE\ngh issue edit "$NUMBER" --add-label triage\n',
        ),
        ((*_S("triage", 0), "env", "TITLE"), DROP),
        ((*_S("triage", 0), "env", "NUMBER"), DROP),
        ((*_S("triage", 0), "env", "GH_TOKEN"), DROP),
        ((*_S("triage", 0), "env", "EXTRA"), "1"),
    ],
}
SEEDS = range(8)


def _workflows():
    return {
        slug: meta
        for slug, meta in catalogue.tasks().items()
        if meta.get("kind") == catalogue.WORKFLOW
    }


def _key(meta, seed):
    """The answer key for one brief, parsed the way the grader parses the learner's."""
    brief = _grader(meta).brief(random.Random(seed))
    return brief, yaml.load(
        manifest.render_solution(meta, brief), Loader=WorkflowLoader
    )


@pytest.mark.parametrize(
    "text, on",
    [
        ("on: push\n", "on"),
        ('"on": push\n', "on"),
        ("'on': push\n", "on"),
    ],
)
def test_the_workflow_loader_keeps_on_a_string(text, on):
    """PyYAML alone reads `on:` as the key True, and GitHub reads it as `on`."""
    assert list(yaml.load(text, Loader=WorkflowLoader)) == [on]


def test_the_workflow_loader_keeps_only_true_and_false_as_booleans():
    doc = yaml.load(
        "a: yes\nb: off\nc: true\nd: False\ne: 'true'\n", Loader=WorkflowLoader
    )
    assert doc == {"a": "yes", "b": "off", "c": True, "d": False, "e": "true"}


def test_every_workflow_task_has_its_rules_listed():
    assert set(_workflows()) == set(BREAKS)


@pytest.mark.parametrize("slug", sorted(BREAKS))
def test_the_answer_key_passes_and_every_broken_rule_fails(slug):
    meta = _workflows()[slug]
    grade = _grader(meta)
    for seed in SEEDS:
        brief, workflow = _key(meta, seed)
        grade.check(copy.deepcopy(workflow), brief)
        for path, value in BREAKS[slug]:
            with pytest.raises(AssertionError):
                grade.check(_broken([workflow], 0, path, value)[0], brief)


real = pytest.mark.skipif(
    tools.installed(tools.ACTIONLINT) is None,
    reason="actionlint is not installed: run `drillion doctor --fetch`",
)


def _grade(meta, brief, text):
    """The real child, grading `text` as the learner's file. It has to sit under tasks/,
    the one tree the sandbox reads, and a unique name keeps parallel workers apart."""
    path = meta["dir"] / f"_test_{uuid.uuid4().hex}.yml"
    path.write_text(text, encoding="utf-8")
    try:
        passed, diagnostics, *_ = runner.run_manifest(
            meta, brief, learner=path, **kinds.of(meta).extra(meta, brief, 0)
        )
    finally:
        path.unlink()
    return passed, diagnostics


@real
@pytest.mark.parametrize("slug", sorted(BREAKS))
def test_the_answer_key_passes_actionlint(slug):
    meta = _workflows()[slug]
    brief = manifest.generate_brief(meta, 0)
    assert _grade(meta, brief, kinds.of(meta).answer_key(meta, brief)) == (True, [])


@real
def test_an_actionlint_finding_points_at_the_learners_line():
    meta = _workflows()["371_gha_first_workflow"]
    brief = manifest.generate_brief(meta, 0)
    key = kinds.of(meta).answer_key(meta, brief)
    passed, diagnostics = _grade(
        meta, brief, key.replace("ubuntu-latest", "ubuntu-latst")
    )
    assert not passed
    first = diagnostics[0]
    assert first["file"] == meta["edits"] and first["line"] == 8
    assert "ubuntu-latst" in first["message"]


@real
def test_a_callee_that_drops_an_input_is_refused_where_the_caller_passes_it():
    """The caller ships read-only beside the learner's reusable workflow, and actionlint
    reads the two together: the input the caller passes and the callee no longer declares
    is reported on the caller's line."""
    meta = _workflows()["381_gha_reusable_workflow"]
    brief = manifest.generate_brief(meta, 0)
    key = kinds.of(meta).answer_key(meta, brief)
    dropped = key.replace(
        "      context:\n        type: string\n        required: true\n", ""
    )
    assert dropped != key
    passed, diagnostics = _grade(meta, brief, dropped)
    assert not passed
    assert any(
        d.get("file") == ".github/workflows/ci.yml" and "context" in d["message"]
        for d in diagnostics
    ), diagnostics


@real
def test_an_empty_workflow_says_so_before_actionlint_runs():
    meta = _workflows()["371_gha_first_workflow"]
    brief = manifest.generate_brief(meta, 0)
    passed, diagnostics = _grade(meta, brief, "\n")
    assert not passed and "is empty" in diagnostics[0]["message"]
