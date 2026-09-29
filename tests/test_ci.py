"""Exercise the Linux CI change filter against real Git histories."""

import os
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from drillion.cli import LEARNER_FILES

WORKFLOW = Path(__file__).parents[1] / ".github/workflows/ci.yml"
CHANGE_SCRIPT = WORKFLOW.parent.parent / "scripts/ci-changes.py"
BROWSERS_SCRIPT = WORKFLOW.parent.parent / "scripts/screens-multiengine.sh"
RELEASE_WORKFLOW = Path(__file__).parents[1] / ".github/workflows/release.yml"
ROOT = Path(__file__).parents[1]


def run_change_filter(tmp_path, changes, base_files=None, base_override=None):
    def git(*args):
        return subprocess.check_output(["git", *args], cwd=tmp_path, text=True).strip()

    git("init", "-q")
    git("config", "commit.gpgsign", "false")
    git("config", "user.name", "Test")
    git("config", "user.email", "test@example.invalid")
    script = tmp_path / ".github/scripts/ci-changes.py"
    script.parent.mkdir(parents=True)
    shutil.copyfile(CHANGE_SCRIPT, script)
    for name, content in (base_files or {}).items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    git("add", ".")
    git("commit", "--allow-empty", "-qm", "base")
    base = git("rev-parse", "HEAD")
    for name, content in changes.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    git("add", ".")
    git("commit", "--allow-empty", "-qm", "head")
    step = yaml.safe_load(WORKFLOW.read_text())["jobs"]["changes"]["steps"][-1]
    output = tmp_path / "output"
    subprocess.run(
        [shutil.which("bash"), "-e", "-o", "pipefail", "-c", step["run"]],
        cwd=tmp_path,
        env={
            **os.environ,
            "BASE": base if base_override is None else base_override,
            "HEAD": git("rev-parse", "HEAD"),
            "EVENT_NAME": "pull_request",
            "GITHUB_OUTPUT": str(output),
            "GITHUB_STEP_SUMMARY": str(tmp_path / "summary"),
        },
        check=True,
    )
    return output.read_text().strip().splitlines()


def selected_lines(enabled):
    return [
        f"{name}={'true' if value else 'false'}"
        for name, value in zip(
            ("docs", "check", "web", "screens", "image"), enabled, strict=True
        )
    ]


@pytest.mark.parametrize(
    ("paths", "base_override", "expected"),
    [
        (["docs/guide.md"], None, (1, 0, 0, 0, 0)),
        (["docs/images/screen.png"], None, (0, 0, 0, 0, 0)),
        (["CONTRIBUTING.md"], None, (1, 0, 0, 0, 0)),
        (["web/README.md"], None, (1, 0, 0, 0, 0)),
        ([".design-sync/NOTES.md"], None, (1, 0, 0, 0, 0)),
        (["README.md"], None, (1, 0, 0, 0, 0)),
        (["web/src/README.md"], None, (0, 0, 1, 1, 1)),
        (["web/e2e/races.spec.ts"], None, (0, 0, 1, 1, 0)),
        (["LICENSE"], None, (0, 1, 1, 1, 1)),
        (["tasks/001_example/README.md"], None, (0, 1, 1, 1, 1)),
        (["docs/check.py"], None, (0, 1, 1, 1, 1)),
        (["docs/guide.md", "src/code.py"], None, (1, 1, 1, 1, 1)),
        (["new-folder/file"], None, (0, 1, 1, 1, 1)),
        (["docs/guide.md\nsrc/code.py"], None, (0, 1, 1, 1, 1)),
        (["docs/guide.md"], "missing", (1, 1, 1, 1, 1)),
        (["docs/guide.md"], "0" * 40, (1, 1, 1, 1, 1)),
        (["docs/guide.md"], "", (1, 1, 1, 1, 1)),
        ([], None, (1, 1, 1, 1, 1)),
    ],
)
def test_change_filter(tmp_path, paths, base_override, expected):
    assert run_change_filter(
        tmp_path, {name: "changed\n" for name in paths}, base_override=base_override
    ) == selected_lines(expected)


@pytest.mark.parametrize(
    ("before", "after", "other_paths", "expected"),
    [
        (
            '[project]\nname = "drillion"\ndescription = "old"\ndependencies = ["fastapi"]\n',
            '[project]\nname = "drillion"\ndescription = "new"\ndependencies = ["fastapi"]\n',
            ["README.md", "AGENTS.md"],
            (1, 0, 0, 0, 0),
        ),
        (
            '[project]\nname = "drillion"\ndependencies = ["fastapi"]\n',
            '[project]\nname = "drillion"\ndependencies = ["starlette"]\n',
            [],
            (0, 1, 1, 1, 1),
        ),
        (
            '[project]\nname = "drillion"\n',
            "not valid TOML\n",
            [],
            (0, 1, 1, 1, 1),
        ),
        (
            '[project]\nname = "drillion"\n',
            'project = "not a table"\n',
            [],
            (0, 1, 1, 1, 1),
        ),
    ],
)
def test_change_filter_project_metadata(tmp_path, before, after, other_paths, expected):
    changes = {"pyproject.toml": after, **dict.fromkeys(other_paths, "changed\n")}
    assert run_change_filter(
        tmp_path, changes, base_files={"pyproject.toml": before}
    ) == selected_lines(expected)


def test_scheduled_ci_runs_all_checks(tmp_path):
    output = tmp_path / "output"
    subprocess.run(
        ["python3", str(CHANGE_SCRIPT)],
        env={
            **os.environ,
            "EVENT_NAME": "schedule",
            "BASE": "",
            "HEAD": "",
            "GITHUB_OUTPUT": str(output),
            "GITHUB_STEP_SUMMARY": str(tmp_path / "summary"),
        },
        check=True,
    )
    assert output.read_text().strip().splitlines() == [
        f"{name}=true" for name in ("docs", "check", "web", "screens", "image")
    ]


@pytest.mark.parametrize("failed", ["", "firefox", "webkit"])
def test_parallel_browser_engines_keep_state_separate_and_report_failures(
    tmp_path, failed
):
    pnpm = tmp_path / "pnpm"
    pnpm.write_text(
        "#!/usr/bin/env bash\n"
        'echo "$DRILLION_E2E_ROOT $DRILLION_PORT $*" >> "$CALLS"\n'
        'if [[ "$*" == *"--project=$FAIL_ON"* && -n "$FAIL_ON" ]]; then exit 7; fi\n'
    )
    pnpm.chmod(0o755)
    calls = tmp_path / "calls"
    result = subprocess.run(
        ["bash", str(BROWSERS_SCRIPT)],
        cwd=tmp_path,
        env={
            **os.environ,
            "PATH": f"{tmp_path}:{os.environ['PATH']}",
            "RUNNER_TEMP": str(tmp_path),
            "CALLS": str(calls),
            "FAIL_ON": failed,
        },
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == (1 if failed else 0), result.stderr
    lines = calls.read_text().splitlines()
    assert len(lines) == 2
    assert any(
        "drillion-firefox 8766 screens --project=firefox --output=test-results/firefox"
        in line
        for line in lines
    )
    assert any(
        "drillion-webkit 8767 screens --project=webkit --output=test-results/webkit"
        in line
        for line in lines
    )


@pytest.mark.parametrize("status", [0, 7])
def test_background_smoke_result(tmp_path, status):
    script = tmp_path / ".github/scripts/image-smoke.sh"
    script.parent.mkdir(parents=True)
    script.write_text(f"echo smoke-output\nexit {status}\n")
    steps = yaml.safe_load(WORKFLOW.read_text())["jobs"]["image"]["steps"]
    start = next(step for step in steps if step.get("id") == "smoke")
    collect = next(
        step for step in steps if step.get("name") == "collect image smoke tests"
    )
    output = tmp_path / "output"
    env = {**os.environ, "RUNNER_TEMP": str(tmp_path), "GITHUB_OUTPUT": str(output)}
    subprocess.run(
        ["bash", "-e", "-o", "pipefail", "-c", start["run"]],
        cwd=tmp_path,
        env=env,
        check=True,
    )
    env["SMOKE_PID"] = output.read_text().strip().split("=")[1]
    result = subprocess.run(
        ["bash", "-e", "-o", "pipefail", "-c", collect["run"]],
        cwd=tmp_path,
        env=env,
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == status
    assert "smoke-output" in result.stdout


@pytest.mark.parametrize("failure", ["", "selfcheck", "python"])
def test_smoke_reaches_volume_check_and_propagates_failures(tmp_path, failure):
    docker = tmp_path / "docker"
    docker.write_text(
        "#!/usr/bin/env bash\n"
        'if [[ "$1" == inspect ]]; then echo healthy; fi\n'
        'if [[ "$*" == *"$FAIL_ON"* && -n "$FAIL_ON" ]]; then exit 7; fi\n'
    )
    # the script checks the served count against the checkout, so the fake serves what
    # every kind's learner file adds up to, and a kind the script forgot fails here
    task_dir = WORKFLOW.parents[2] / "tasks"
    served = sum(len(list(task_dir.glob(f"*/{name}"))) for name in LEARNER_FILES)
    curl = tmp_path / "curl"
    curl.write_text(
        f'#!/usr/bin/env bash\necho "$*" >> "$CALLS"\necho \'{{"tasks":{served}}}\'\n'
    )
    for command in (docker, curl):
        command.chmod(0o755)
    calls = tmp_path / "calls"
    result = subprocess.run(
        ["bash", str(WORKFLOW.parent.parent / "scripts/image-smoke.sh")],
        env={
            **os.environ,
            "PATH": f"{tmp_path}:{os.environ['PATH']}",
            "FAIL_ON": failure,
            "CALLS": str(calls),
        },
        cwd=WORKFLOW.parents[2],
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == (7 if failure else 0), result.stdout + result.stderr
    if not failure:
        assert "/api/task/009_fstrings/open" in calls.read_text()


def test_release_publishes_only_the_attested_container_image():
    release = yaml.safe_load(RELEASE_WORKFLOW.read_text())
    jobs = release["jobs"]

    assert set(jobs) == {"gate", "build", "image", "sbom", "image-scan", "notes"}
    assert jobs["notes"]["needs"] == ["image", "sbom"]
    assert jobs["notes"]["permissions"] == {"contents": "write"}

    image = {step.get("id"): step for step in jobs["image"]["steps"]}
    assert image["meta"]["with"]["tags"] == "type=pep440,pattern={{version}}"
    assert image["meta"]["with"]["flavor"] == "latest=auto"
    assert jobs["image"]["outputs"]["digest"] == "${{ steps.digest.outputs.value }}"
    assert "imagetools create" in image["digest"]["run"]

    # a published version is never rebuilt: a retry reuses its digest
    gate = {step.get("id"): step for step in jobs["gate"]["steps"]}
    assert "imagetools inspect" in gate["published"]["run"]
    assert jobs["build"]["if"] == "needs.gate.outputs.published == ''"
    assert image["digest"]["env"]["PUBLISHED"] == "${{ needs.gate.outputs.published }}"
    # a skipped build skips everything below it unless each job says otherwise
    for job in ("image", "sbom", "image-scan", "notes"):
        assert "!cancelled()" in jobs[job]["if"]

    # each platform builds natively, never under QEMU
    legs = jobs["build"]["strategy"]["matrix"]["include"]
    assert {leg["arch"]: leg["runner"] for leg in legs} == {
        "amd64": "ubuntu-latest",
        "arm64": "ubuntu-24.04-arm",
    }
    build = {step.get("id"): step for step in jobs["build"]["steps"]}
    assert build["push"]["with"]["platforms"] == "linux/${{ matrix.arch }}"
    assert "push-by-digest=true" in build["push"]["with"]["outputs"]
    assert not any(
        "setup-qemu" in s.get("uses", "")
        for j in jobs.values()
        for s in j.get("steps", [])
    )

    def attested(steps):
        return [s for s in steps if s.get("uses", "").startswith("actions/attest@")]

    [provenance] = attested(jobs["image"]["steps"])
    assert provenance["with"]["subject-digest"] == "${{ steps.digest.outputs.value }}"
    assert "sbom-path" not in provenance["with"]

    # every platform the image is built for gets an SBOM of its own filesystem
    arches = jobs["sbom"]["strategy"]["matrix"]["arch"]
    assert sorted(arches) == sorted(leg["arch"] for leg in legs)
    platforms = [f"linux/{a}" for a in arches]
    [sbom] = attested(jobs["sbom"]["steps"])
    assert sbom["with"]["subject-digest"] == "${{ steps.platform.outputs.digest }}"
    assert sbom["with"]["sbom-path"] == "sbom.spdx.json"
    assert all(
        s["with"]["push-to-registry"] is True
        for s in attested(jobs["image"]["steps"] + jobs["sbom"]["steps"])
    )

    release_step = jobs["notes"]["steps"][-1]
    assert release_step["env"]["DIGEST"] == "${{ needs.image.outputs.digest }}"
    notes = release_step["run"]
    assert "${image}@${DIGEST}" in notes
    for platform in platforms:
        assert platform in notes
    assert "docker run" in notes and "-v drillion:/data" in notes
    assert "gh attestation verify oci://${image}@${DIGEST}" in notes
    assert 'gh release create "$GITHUB_REF_NAME"' in notes
    assert "dist/" not in notes


def test_user_docs_describe_docker_as_the_only_distribution():
    docs = {
        "README.md": (ROOT / "README.md").read_text(),
        "docs/configuration.md": (ROOT / "docs/configuration.md").read_text(),
        "CONTRIBUTING.md": (ROOT / "CONTRIBUTING.md").read_text(),
        "SECURITY.md": (ROOT / "SECURITY.md").read_text(),
    }

    for text in docs.values():
        assert "uv tool install drillion" not in text
        assert "uv tool upgrade drillion" not in text
        assert "pypi-attestations" not in text

    assert "docker compose up -d" in docs["README.md"]
    assert "docker exec drillion drillion selfcheck" in docs["README.md"]
    assert "docker compose pull && docker compose up -d" in docs["README.md"]
    assert "docker stop drillion && docker rm drillion" in docs["README.md"]
    assert "docker rm -f drillion" not in docs["README.md"]
    assert (
        "gh attestation verify oci://ghcr.io/vazome/drillion:<version>"
        in docs["docs/configuration.md"]
    )
