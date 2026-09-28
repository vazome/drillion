"""What one sitting of 380 asks for, and what counts as having answered it.

Both concurrency values are compared as expression text with the whitespace collapsed: a
plain `true` for cancel-in-progress is the very thing this task is about not writing."""

GROUP = "${{ github.workflow }}-${{ github.ref }}"
CANCEL = "${{ github.event_name == 'pull_request' }}"


def brief(r):
    return {"command": r.choice(["make test", "npm test", "go test ./..."])}


def _expr(text):
    return " ".join(str(text).split())


def check(workflow, b):
    assert workflow.get("name") == "CI", (
        f"the workflow's name is {workflow.get('name')!r}, and it should be 'CI'"
    )
    on = workflow.get("on")
    assert isinstance(on, dict) and set(on) == {"push", "pull_request"}, (
        f"`on` is {on!r}, and it should be exactly push and pull_request"
    )
    assert on["push"] == {"branches": ["main"]} and not on["pull_request"], (
        f"`on` is {on!r}: push should be limited to branches: [main], and pull_request "
        "should have nothing under it"
    )
    concurrency = workflow.get("concurrency")
    assert isinstance(concurrency, dict), (
        f"the workflow's concurrency is {concurrency!r}, and it should be a map with "
        "group and cancel-in-progress"
    )
    assert set(concurrency) == {"group", "cancel-in-progress"}, (
        f"concurrency has {sorted(concurrency)}, and it should have exactly group and "
        "cancel-in-progress"
    )
    assert _expr(concurrency["group"]) == GROUP, (
        f"the group is {concurrency['group']!r}, and it should be {GROUP}: the workflow "
        "and the ref, so no branch cancels another's run"
    )
    cancel = concurrency["cancel-in-progress"]
    assert _expr(cancel) == CANCEL, (
        f"cancel-in-progress is {cancel!r}, and it should be {CANCEL}"
        + (
            ": a run on main may be a deploy, and must never be cancelled"
            if cancel is True
            else ""
        )
    )
    jobs = workflow.get("jobs") or {}
    assert list(jobs) == ["test"], (
        f"the jobs are {list(jobs)}, and there should be one, 'test'"
    )
    job = jobs["test"]
    assert job.get("runs-on") == "ubuntu-latest", (
        f"the job runs on {job.get('runs-on')!r}, and it should be 'ubuntu-latest'"
    )
    assert "concurrency" not in job, (
        "the job has its own concurrency, and this task sets it once, for the whole run"
    )
    steps = job.get("steps") or []
    assert len(steps) == 2, f"the job has {len(steps)} steps, and it should have two"
    first = steps[0] if isinstance(steps[0], dict) else {}
    assert str(first.get("uses", "")).startswith("actions/checkout@"), (
        f"the first step is {steps[0]!r}, and it should use actions/checkout"
    )
    assert steps[1].get("run") == b["command"], (
        f"the second step runs {steps[1].get('run')!r}, and it should run {b['command']!r}"
    )
