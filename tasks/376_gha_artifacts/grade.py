"""What one sitting of 376 asks for, and what counts as having answered it."""

PACKAGES = ["ledger", "pricing", "catalog-client", "retry-kit"]


def brief(r):
    return {
        "artifact": f"{r.choice(PACKAGES)}-dist",
        "days": r.choice([3, 5, 7]),
    }


def _uses(step, action):
    return isinstance(step, dict) and str(step.get("uses", "")).startswith(action + "@")


def _needs(job):
    needs = job.get("needs") or []
    return {needs} if isinstance(needs, str) else set(needs)


def check(workflow, b):
    assert workflow.get("name") == "package", (
        f"the workflow's name is {workflow.get('name')!r}, and it should be 'package'"
    )
    on = workflow.get("on")
    assert (
        on == "push"
        or on == ["push"]
        or (isinstance(on, dict) and set(on) == {"push"} and not on["push"])
    ), f"`on` is {on!r}, and it should be push with nothing under it"
    jobs = workflow.get("jobs") or {}
    assert set(jobs) == {"build", "check"}, (
        f"the jobs are {sorted(jobs)}, and they should be build and check"
    )
    for name in jobs:
        assert jobs[name].get("runs-on") == "ubuntu-latest", (
            f"{name} runs on {jobs[name].get('runs-on')!r}, and it should be "
            "'ubuntu-latest'"
        )

    build = jobs["build"]
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
    want = {"name": b["artifact"], "path": "dist/", "retention-days": b["days"]}
    assert upload.get("with") == want, (
        f"the upload's inputs are {upload.get('with')!r}, and they should be exactly {want}"
    )
    assert _needs(build) == set(), (
        f"build needs {sorted(_needs(build))}, and it should need nothing"
    )

    check_job = jobs["check"]
    assert _needs(check_job) == {"build"}, (
        f"check needs {sorted(_needs(check_job))}, and it should need build: without it, "
        "it can start before there is anything to download"
    )
    steps = check_job.get("steps") or []
    assert len(steps) == 2, (
        f"check has {len(steps)} steps, and it should have two: it downloads what build "
        "made, and builds nothing itself"
    )
    download, twine = steps
    assert _uses(download, "actions/download-artifact"), (
        f"check's first step is {download!r}, and it should use actions/download-artifact"
    )
    want = {"name": b["artifact"], "path": "dist/"}
    assert download.get("with") == want, (
        f"the download's inputs are {download.get('with')!r}, and they should be exactly "
        f"{want}"
    )
    assert twine.get("run") == "pipx run twine check dist/*", (
        f"check's second step runs {twine.get('run')!r}, and it should run "
        "'pipx run twine check dist/*'"
    )
