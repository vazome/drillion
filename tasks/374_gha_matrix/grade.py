"""What one sitting of 374 asks for, and what counts as having answered it.

The matrix is compared as written, with each version a string: `3.10` unquoted is the
number 3.1, and a matrix of numbers is a quiet way to test the wrong Python."""

PYTHONS = ["3.12", "3.13", "3.14"]


def brief(r):
    return {"skipped": r.choice(["3.12", "3.13"])}


def _expr(text):
    return " ".join(str(text).split())


def _uses(step, action):
    return isinstance(step, dict) and str(step.get("uses", "")).startswith(action + "@")


def check(workflow, b):
    assert workflow.get("name") == "CI", (
        f"the workflow's name is {workflow.get('name')!r}, and it should be 'CI'"
    )
    on = workflow.get("on")
    assert (
        on == "push"
        or on == ["push"]
        or (isinstance(on, dict) and set(on) == {"push"} and not on["push"])
    ), f"`on` is {on!r}, and it should be push with nothing under it"
    jobs = workflow.get("jobs") or {}
    assert list(jobs) == ["test"], (
        f"the jobs are {list(jobs)}, and there should be one, 'test'"
    )
    job = jobs["test"]
    assert _expr(job.get("runs-on")) == "${{ matrix.os }}", (
        f"runs-on is {job.get('runs-on')!r}, and it should read the combination's system, "
        "${{ matrix.os }}"
    )
    strategy = job.get("strategy") or {}
    assert strategy.get("fail-fast") is False, (
        f"strategy.fail-fast is {strategy.get('fail-fast')!r}, and it should be false, so "
        "one failure does not cancel the rest"
    )
    matrix = strategy.get("matrix") or {}
    assert matrix.get("os") == ["ubuntu-latest", "windows-latest"], (
        f"matrix.os is {matrix.get('os')!r}, and it should be ['ubuntu-latest', "
        "'windows-latest']"
    )
    assert matrix.get("python") == PYTHONS, (
        f"matrix.python is {matrix.get('python')!r}, and it should be {PYTHONS}, each a "
        "quoted string"
    )
    want = [{"os": "windows-latest", "python": b["skipped"]}]
    assert matrix.get("exclude") == want, (
        f"matrix.exclude is {matrix.get('exclude')!r}, and it should be {want}"
    )
    want = [{"os": "macos-latest", "python": "3.14"}]
    assert matrix.get("include") == want, (
        f"matrix.include is {matrix.get('include')!r}, and it should be {want}"
    )
    extra = sorted(set(matrix) - {"os", "python", "exclude", "include"})
    assert not extra, f"the matrix also has {extra}, and every key multiplies the jobs"
    steps = job.get("steps") or []
    assert len(steps) == 3, (
        f"the job has {len(steps)} steps, and the task asks for three"
    )
    checkout, python, test = steps
    assert _uses(checkout, "actions/checkout"), (
        f"the first step is {checkout!r}, and it should use actions/checkout"
    )
    assert _uses(python, "actions/setup-python"), (
        f"the second step is {python!r}, and it should use actions/setup-python"
    )
    got = {k: _expr(v) for k, v in (python.get("with") or {}).items()}
    assert got == {"python-version": "${{ matrix.python }}"}, (
        f"setup-python's inputs are {python.get('with')!r}, and they should be exactly "
        "python-version: ${{ matrix.python }}"
    )
    assert test.get("run") == "pytest", (
        f"the third step runs {test.get('run')!r}, and it should run 'pytest'"
    )
