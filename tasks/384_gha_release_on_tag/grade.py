"""What one sitting of 384 asks for, and what counts as having answered it."""

PACKAGES = ["ledger", "pricing", "retry-kit"]
COMMAND = 'gh release create "$TAG" dist/* --generate-notes'
ENV = {
    "GH_TOKEN": "${{ github.token }}",
    "GH_REPO": "${{ github.repository }}",
    "TAG": "${{ github.ref_name }}",
}


def brief(r):
    return {"artifact": f"{r.choice(PACKAGES)}-dist"}


def _expr(value):
    return " ".join(value.split()) if isinstance(value, str) else value


def _uses(step, action):
    return isinstance(step, dict) and str(step.get("uses", "")).startswith(action + "@")


def _needs(job):
    needs = job.get("needs") or []
    return {needs} if isinstance(needs, str) else set(needs)


def check(workflow, b):
    assert workflow.get("name") == "release", (
        f"the workflow's name is {workflow.get('name')!r}, and it should be 'release'"
    )
    on = workflow.get("on")
    assert on == {"push": {"tags": ["v*.*.*"]}}, (
        f"`on` is {on!r}, and it should be exactly push with tags: ['v*.*.*']"
    )
    assert workflow.get("permissions") == {"contents": "read"}, (
        f"the workflow's permissions are {workflow.get('permissions')!r}, and they should "
        "be exactly contents: read"
    )
    jobs = workflow.get("jobs") or {}
    assert set(jobs) == {"build", "release"}, (
        f"the jobs are {sorted(jobs)}, and they should be build and release"
    )
    for name in jobs:
        assert jobs[name].get("runs-on") == "ubuntu-latest", (
            f"{name} runs on {jobs[name].get('runs-on')!r}, and it should be "
            "'ubuntu-latest'"
        )

    build = jobs["build"]
    assert "permissions" not in build, (
        "build has its own permissions, and it only reads: the workflow's are enough"
    )
    steps = build.get("steps") or []
    assert len(steps) == 4, f"build has {len(steps)} steps, and it should have four"
    checkout, tools, dist, upload = steps
    assert _uses(checkout, "actions/checkout"), (
        f"build's first step is {checkout!r}, and it should use actions/checkout"
    )
    assert tools.get("run") == "pip install build", (
        f"build's second step runs {tools.get('run')!r}, and it should run "
        "'pip install build'"
    )
    assert dist.get("run") == "python -m build", (
        f"build's third step runs {dist.get('run')!r}, and it should run 'python -m build'"
    )
    assert _uses(upload, "actions/upload-artifact"), (
        f"build's last step is {upload!r}, and it should use actions/upload-artifact"
    )
    want = {"name": b["artifact"], "path": "dist/"}
    assert upload.get("with") == want, (
        f"the upload's inputs are {upload.get('with')!r}, and they should be exactly {want}"
    )

    release = jobs["release"]
    assert _needs(release) == {"build"}, (
        f"release needs {sorted(_needs(release))}, and it should need build"
    )
    assert release.get("permissions") == {"contents": "write"}, (
        f"release's permissions are {release.get('permissions')!r}, and they should be "
        "exactly contents: write: creating a release writes to the repository"
    )
    steps = release.get("steps") or []
    assert len(steps) == 2, f"release has {len(steps)} steps, and it should have two"
    download, publish = steps
    assert _uses(download, "actions/download-artifact"), (
        f"release's first step is {download!r}, and it should use "
        "actions/download-artifact"
    )
    assert download.get("with") == want, (
        f"the download's inputs are {download.get('with')!r}, and they should be exactly "
        f"{want}"
    )
    assert publish.get("run") == COMMAND, (
        f"release's second step runs {publish.get('run')!r}, and it should run {COMMAND!r}"
    )
    env = {k: _expr(v) for k, v in (publish.get("env") or {}).items()}
    assert env == ENV, (
        f"the release step's env is {publish.get('env')!r}, and it should be exactly {ENV}"
    )
