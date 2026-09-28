"""What one sitting of 377 asks for, and what counts as having answered it.

Both permission blocks are compared exactly: a scope too many is the lesson failing, and
a job block missing `contents: read` is the replace-not-merge rule missed."""

LABELS = ["needs-review", "triage", "size/check"]
ENV = {
    "GH_TOKEN": "${{ github.token }}",
    "GH_REPO": "${{ github.repository }}",
    "NUMBER": "${{ github.event.pull_request.number }}",
}


def brief(r):
    label = r.choice(LABELS)
    return {"label": label, "command": f'gh pr edit "$NUMBER" --add-label "{label}"'}


def _expr(text):
    return " ".join(str(text).split())


def check(workflow, b):
    assert workflow.get("name") == "label", (
        f"the workflow's name is {workflow.get('name')!r}, and it should be 'label'"
    )
    on = workflow.get("on")
    assert isinstance(on, dict) and set(on) == {"pull_request"}, (
        f"`on` is {on!r}, and it should be pull_request alone"
    )
    assert on["pull_request"] == {"types": ["opened"]}, (
        f"on.pull_request is {on['pull_request']!r}, and it should be types: [opened]"
    )
    assert workflow.get("permissions") == {"contents": "read"}, (
        f"the workflow's permissions are {workflow.get('permissions')!r}, and they should "
        "be exactly contents: read"
    )
    jobs = workflow.get("jobs") or {}
    assert list(jobs) == ["label"], (
        f"the jobs are {list(jobs)}, and there should be one, 'label'"
    )
    job = jobs["label"]
    assert job.get("runs-on") == "ubuntu-latest", (
        f"the job runs on {job.get('runs-on')!r}, and it should be 'ubuntu-latest'"
    )
    want = {"contents": "read", "pull-requests": "write"}
    got = job.get("permissions")
    assert got == want, (
        f"the job's permissions are {got!r}, and they should be exactly {want}"
        + (
            ": a job's block replaces the workflow's, so contents: read has to be "
            "named again"
            if isinstance(got, dict) and "contents" not in got
            else ""
        )
    )
    steps = job.get("steps") or []
    assert len(steps) == 1, f"the job has {len(steps)} steps, and it should have one"
    step = steps[0]
    assert step.get("run") == b["command"], (
        f"the step runs {step.get('run')!r}, and it should run {b['command']!r}"
    )
    env = {k: _expr(v) for k, v in (step.get("env") or {}).items()}
    assert env == ENV, (
        f"the step's env is {step.get('env')!r}, and it should be exactly {ENV}"
    )
