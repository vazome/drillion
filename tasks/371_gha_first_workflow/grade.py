"""What one sitting of 371 asks for, and what counts as having answered it.

actionlint has already run, so the file is a valid workflow. What is left is what the task
asks: the events, the one job, and its steps in order. An action is matched by name at any
version, since the version is not what this task teaches."""


def brief(r):
    return {"python": r.choice(["3.12", "3.13", "3.14"])}


def _uses(step, action):
    return isinstance(step, dict) and str(step.get("uses", "")).startswith(action + "@")


def check(workflow, b):
    assert workflow.get("name") == "CI", (
        f"the workflow's name is {workflow.get('name')!r}, and it should be 'CI'"
    )
    on = workflow.get("on")
    assert isinstance(on, dict) and set(on) == {"push", "pull_request"}, (
        f"`on` is {on!r}, and it should be exactly two events: push and pull_request"
    )
    assert on["push"] == {"branches": ["main"]}, (
        f"on.push is {on['push']!r}, and it should be limited to branches: [main]"
    )
    assert not on["pull_request"], (
        f"on.pull_request is {on['pull_request']!r}, and it should have nothing under it, "
        "so every pull request runs the tests"
    )
    jobs = workflow.get("jobs") or {}
    assert list(jobs) == ["test"], (
        f"the jobs are {list(jobs)}, and there should be one, 'test'"
    )
    job = jobs["test"]
    assert job.get("runs-on") == "ubuntu-latest", (
        f"the job runs on {job.get('runs-on')!r}, and it should be 'ubuntu-latest'"
    )
    steps = job.get("steps") or []
    assert len(steps) == 4, (
        f"the job has {len(steps)} steps, and the task asks for four"
    )
    checkout, python, install, test = steps
    assert _uses(checkout, "actions/checkout"), (
        f"the first step is {checkout!r}, and it should use actions/checkout: the machine "
        "starts without your code"
    )
    assert _uses(python, "actions/setup-python"), (
        f"the second step is {python!r}, and it should use actions/setup-python"
    )
    assert python.get("with") == {"python-version": b["python"]}, (
        f"setup-python's inputs are {python.get('with')!r}, and they should be exactly "
        f"python-version: {b['python']!r}, quoted"
    )
    assert install.get("run") == "pip install -r requirements.txt", (
        f"the third step runs {install.get('run')!r}, and it should run "
        "'pip install -r requirements.txt'"
    )
    assert test.get("run") == "pytest", (
        f"the fourth step runs {test.get('run')!r}, and it should run 'pytest'"
    )
