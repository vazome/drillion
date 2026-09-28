"""What one sitting of 375 asks for, and what counts as having answered it.

The key is compared as the expression text, whitespace collapsed: which contexts it reads,
and in which order, is what decides when the cache is stale."""

LOCKS = ["requirements.txt", "requirements-dev.txt", "requirements/ci.txt"]
PREFIX = "${{ runner.os }}-pip-${{ matrix.python }}-"


def brief(r):
    lock = r.choice(LOCKS)
    return {
        "lock": lock,
        "install": f"pip install -r {lock}",
        "key": PREFIX + "${{ hashFiles('" + lock + "') }}",
        "restore": PREFIX,
    }


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
    assert job.get("runs-on") == "ubuntu-latest", (
        f"the job runs on {job.get('runs-on')!r}, and it should be 'ubuntu-latest'"
    )
    matrix = (job.get("strategy") or {}).get("matrix")
    assert matrix == {"python": ["3.13", "3.14"]}, (
        f"the matrix is {matrix!r}, and it should be exactly python: ['3.13', '3.14'], "
        "as strings"
    )
    steps = job.get("steps") or []
    assert len(steps) == 5, (
        f"the job has {len(steps)} steps, and the task asks for five"
    )
    checkout, python, cache, install, test = steps
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
    assert _uses(cache, "actions/cache"), (
        f"the third step is {cache!r}, and it should use actions/cache, before anything "
        "installs"
    )
    got = {k: _expr(v) for k, v in (cache.get("with") or {}).items()}
    assert set(got) == {"path", "key", "restore-keys"}, (
        f"the cache's inputs are {sorted(got)}, and they should be exactly path, key and "
        "restore-keys"
    )
    assert got["path"] == "~/.cache/pip", (
        f"the cache's path is {got['path']!r}, and pip keeps its downloads in "
        "'~/.cache/pip'"
    )
    assert got["key"] == b["key"], (
        f"the cache's key is {got['key']!r}, and it should be {b['key']!r}: the system, "
        "the Python version and a hash of the lockfile"
    )
    assert got["restore-keys"] == b["restore"], (
        f"restore-keys is {got['restore-keys']!r}, and it should be the key's prefix, "
        f"{b['restore']!r}"
    )
    assert install.get("run") == b["install"], (
        f"the fourth step runs {install.get('run')!r}, and it should run {b['install']!r}"
    )
    assert test.get("run") == "pytest", (
        f"the fifth step runs {test.get('run')!r}, and it should run 'pytest'"
    )
