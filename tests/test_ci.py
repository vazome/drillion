"""Exercise the Linux CI change filter against real Git histories."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.skipif(
    sys.platform == "win32", reason="CI filter runs on Linux"
)
WORKFLOW = Path(__file__).parents[1] / ".github/workflows/ci.yml"
RELEASE_WORKFLOW = Path(__file__).parents[1] / ".github/workflows/release.yml"
ROOT = Path(__file__).parents[1]


@pytest.mark.parametrize(
    ("paths", "base_override", "expected"),
    [
        (["docs/guide.md"], None, "false"),
        (["docs/images/screen.png"], None, "false"),
        (["CONTRIBUTING.md"], None, "false"),
        (["README.md"], None, "true"),
        (["LICENSE"], None, "true"),
        (["tasks/001_example/README.md"], None, "true"),
        (["docs/check.py"], None, "true"),
        (["docs/guide.md", "src/code.py"], None, "true"),
        (["new-folder/file"], None, "true"),
        (["docs/guide.md\nsrc/code.py"], None, "true"),
        (["docs/guide.md"], "missing", "true"),
        (["docs/guide.md"], "0" * 40, "true"),
        (["docs/guide.md"], "", "true"),
        ([], None, "true"),
    ],
)
def test_change_filter(tmp_path, paths, base_override, expected):
    def git(*args):
        return subprocess.check_output(["git", *args], cwd=tmp_path, text=True).strip()

    git("init", "-q")
    git("config", "commit.gpgsign", "false")
    git("config", "user.name", "Test")
    git("config", "user.email", "test@example.invalid")
    git("commit", "--allow-empty", "-qm", "base")
    base = git("rev-parse", "HEAD")
    for name in paths:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("changed\n")
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
            "GITHUB_OUTPUT": str(output),
            "GITHUB_STEP_SUMMARY": str(tmp_path / "summary"),
            "RUNNER_TEMP": str(tmp_path),
        },
        check=True,
    )
    assert output.read_text().strip() == f"code={expected}"


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
    # the script checks the served count against the checkout, so the fake has to agree
    task_dir = WORKFLOW.parents[2] / "tasks"
    served = sum(
        len(list(task_dir.glob(pattern))) for pattern in ("*/task.py", "*/task.yaml")
    )
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

    assert set(jobs) == {"gate", "image", "sbom", "image-scan", "notes"}
    assert jobs["notes"]["needs"] == ["image", "sbom"]
    assert jobs["notes"]["permissions"] == {"contents": "write"}

    image = {step.get("id"): step for step in jobs["image"]["steps"]}
    assert image["meta"]["with"]["tags"] == "type=pep440,pattern={{version}}"
    assert image["meta"]["with"]["flavor"] == "latest=auto"
    assert jobs["image"]["outputs"]["digest"] == "${{ steps.digest.outputs.value }}"

    # a published version is never rebuilt: a retry reuses its digest
    assert image["push"]["if"] == "steps.existing.outputs.digest == ''"
    assert "imagetools inspect" in image["existing"]["run"]

    def attested(steps):
        return [s for s in steps if s.get("uses", "").startswith("actions/attest@")]

    [provenance] = attested(jobs["image"]["steps"])
    assert provenance["with"]["subject-digest"] == "${{ steps.digest.outputs.value }}"
    assert "sbom-path" not in provenance["with"]

    # every platform the image is built for gets an SBOM of its own filesystem
    platforms = image["push"]["with"]["platforms"].split(",")
    arches = jobs["sbom"]["strategy"]["matrix"]["arch"]
    assert [f"linux/{a}" for a in arches] == platforms
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
    assert "docker stop drillion" in docs["README.md"]
    assert "docker rm -f drillion" not in docs["README.md"]
    assert (
        "gh attestation verify oci://ghcr.io/vazome/drillion:<version>"
        in docs["docs/configuration.md"]
    )
