"""What one sitting of 373 asks for, and what counts as having answered it.

`needs` is read as GitHub reads it: one name or a list of names, compared as a set. An `if`
is compared as the expression it is, with any `${{ }}` around it taken off and its
whitespace collapsed."""

IF = "github.ref == 'refs/heads/main' && github.event_name == 'push'"


def brief(r):
    return {"deploy": f"./deploy.sh {r.choice(['production', 'prod-weu', 'live'])}"}


def _expr(text):
    text = " ".join(str(text).split())
    if text.startswith("${{") and text.endswith("}}"):
        text = text[3:-2].strip()
    return text


def _needs(job):
    needs = job.get("needs") or []
    return {needs} if isinstance(needs, str) else set(needs)


def _job(jobs, name, last):
    job = jobs[name]
    assert job.get("runs-on") == "ubuntu-latest", (
        f"{name} runs on {job.get('runs-on')!r}, and it should be 'ubuntu-latest'"
    )
    steps = job.get("steps") or []
    assert len(steps) == 2, f"{name} has {len(steps)} steps, and it should have two"
    first = steps[0] if isinstance(steps[0], dict) else {}
    assert str(first.get("uses", "")).startswith("actions/checkout@"), (
        f"{name}'s first step is {steps[0]!r}, and it should use actions/checkout: each "
        "job starts on a clean machine"
    )
    assert steps[1].get("run") == last, (
        f"{name}'s second step runs {steps[1].get('run')!r}, and it should run {last!r}"
    )
    return job


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
    jobs = workflow.get("jobs") or {}
    assert set(jobs) == {"lint", "test", "deploy"}, (
        f"the jobs are {sorted(jobs)}, and they should be lint, test and deploy"
    )
    lint = _job(jobs, "lint", "ruff check .")
    assert not _needs(lint), (
        f"lint needs {sorted(_needs(lint))}, and it should need nothing"
    )
    assert "if" not in lint, "lint has an `if`, and it should always run"
    test = _job(jobs, "test", "pytest")
    assert _needs(test) == {"lint"}, (
        f"test needs {sorted(_needs(test))}, and it should need lint"
    )
    assert "if" not in test, (
        "test has an `if`, and it should always run once lint passed"
    )
    deploy = _job(jobs, "deploy", b["deploy"])
    assert _needs(deploy) == {"lint", "test"}, (
        f"deploy needs {sorted(_needs(deploy))}, and it should need lint and test"
    )
    assert _expr(deploy.get("if", "")) == IF, (
        f"deploy's if is {deploy.get('if')!r}, and it should be {IF!r}: the ref alone "
        "does not rule out every other event"
    )
