"""What 385 asks for, and what counts as having answered it.

The report ships read-only, so the brief is empty. actionlint has already refused the
title inside `run`; this also refuses any expression left in the script, and checks the
fix kept everything else the reported workflow did."""

LINES = ['echo "New issue: $TITLE"', 'gh issue edit "$NUMBER" --add-label triage']
ENV = {
    "GH_TOKEN": "${{ github.token }}",
    "GH_REPO": "${{ github.repository }}",
    "TITLE": "${{ github.event.issue.title }}",
    "NUMBER": "${{ github.event.issue.number }}",
}


def brief(r):
    return {}


def _expr(value):
    return " ".join(value.split()) if isinstance(value, str) else value


def check(workflow, b):
    assert workflow.get("name") == "triage", (
        f"the workflow's name is {workflow.get('name')!r}, and it should be 'triage'"
    )
    on = workflow.get("on")
    assert on == {"issues": {"types": ["opened"]}}, (
        f"`on` is {on!r}, and it should be exactly issues with types: [opened]"
    )
    assert workflow.get("permissions") == {"issues": "write"}, (
        f"the workflow's permissions are {workflow.get('permissions')!r}, and they should "
        "be exactly issues: write"
    )
    jobs = workflow.get("jobs") or {}
    assert list(jobs) == ["triage"], (
        f"the jobs are {list(jobs)}, and there should be one, 'triage'"
    )
    job = jobs["triage"]
    assert job.get("runs-on") == "ubuntu-latest", (
        f"the job runs on {job.get('runs-on')!r}, and it should be 'ubuntu-latest'"
    )
    steps = job.get("steps") or []
    assert len(steps) == 1, f"the job has {len(steps)} steps, and it should have one"
    step = steps[0]
    script = str(step.get("run", ""))
    assert "${{" not in script, (
        "the script still holds an expression, and GitHub pastes its value into the "
        "script before the shell reads it: pass it through env instead"
    )
    lines = [ln.strip() for ln in script.strip().splitlines() if ln.strip()]
    assert lines == LINES, (
        f"the script is {lines}, and it should be exactly {LINES}: the variables quoted, "
        "so the shell reads each as one value"
    )
    env = {k: _expr(v) for k, v in (step.get("env") or {}).items()}
    assert env == ENV, (
        f"the step's env is {step.get('env')!r}, and it should be exactly {ENV}"
    )
