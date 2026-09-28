"""What one sitting of 372 asks for, and what counts as having answered it.

Path patterns are compared as sets, since their order does not matter to GitHub; an
expression is compared with its whitespace collapsed."""

SERVICES = ["cart", "payments", "search", "notifications"]
SELF = ".github/workflows/service.yml"


def brief(r):
    svc = r.choice(SERVICES)
    return {
        "svc": svc,
        "pattern": f"services/{svc}/**",
        "test": f"make -C services/{svc} test",
        "deploy": f"make -C services/{svc} deploy",
    }


def _expr(text):
    return " ".join(str(text).split())


def _uses(step, action):
    return isinstance(step, dict) and str(step.get("uses", "")).startswith(action + "@")


def check(workflow, b):
    assert workflow.get("name") == b["svc"], (
        f"the workflow's name is {workflow.get('name')!r}, and it should be {b['svc']!r}"
    )
    on = workflow.get("on")
    assert isinstance(on, dict), f"`on` is {on!r}, and it should be a map of events"
    assert set(on) == {"push", "pull_request", "workflow_dispatch"}, (
        f"the events are {sorted(on)}, and they should be push, pull_request and "
        "workflow_dispatch"
    )
    paths = {b["pattern"], SELF}
    push = on["push"] or {}
    assert push.get("branches") == ["main"], (
        f"on.push.branches is {push.get('branches')!r}, and it should be ['main']"
    )
    assert set(push.get("paths") or []) == paths and len(push["paths"]) == 2, (
        f"on.push.paths is {push.get('paths')!r}, and it should be exactly "
        f"{sorted(paths)}: without the workflow's own path, a change to it is never tested"
    )
    pr = on["pull_request"] or {}
    assert set(pr) == {"paths"} and set(pr["paths"] or []) == paths, (
        f"on.pull_request is {pr!r}, and it should hold only the same paths as push"
    )
    assert len(pr["paths"]) == 2, (
        f"on.pull_request.paths is {pr['paths']!r}, and it should be exactly {sorted(paths)}"
    )
    inputs = (on["workflow_dispatch"] or {}).get("inputs") or {}
    assert set(inputs) == {"environment"}, (
        f"workflow_dispatch's inputs are {sorted(inputs)}, and there should be one, "
        "environment"
    )
    env_input = inputs["environment"] or {}
    want = {
        "type": "choice",
        "options": ["staging", "production"],
        "default": "staging",
    }
    got = {k: env_input.get(k) for k in want}
    assert got == want, f"the environment input is {got}, and it should be {want}"

    jobs = workflow.get("jobs") or {}
    assert list(jobs) == ["build"], (
        f"the jobs are {list(jobs)}, and there should be one, 'build'"
    )
    job = jobs["build"]
    assert job.get("runs-on") == "ubuntu-latest", (
        f"the job runs on {job.get('runs-on')!r}, and it should be 'ubuntu-latest'"
    )
    steps = job.get("steps") or []
    assert len(steps) == 3, (
        f"the job has {len(steps)} steps, and the task asks for three"
    )
    checkout, test, deploy = steps
    assert _uses(checkout, "actions/checkout"), (
        f"the first step is {checkout!r}, and it should use actions/checkout"
    )
    assert test.get("run") == b["test"] and "env" not in test, (
        f"the second step is {test!r}, and it should run {b['test']!r} and nothing else"
    )
    assert deploy.get("run") == b["deploy"], (
        f"the third step runs {deploy.get('run')!r}, and it should run {b['deploy']!r}"
    )
    env = deploy.get("env") or {}
    want = "${{ inputs.environment || 'staging' }}"
    assert set(env) == {"TARGET"} and _expr(env["TARGET"]) == want, (
        f"the deploy step's env is {env!r}, and it should be exactly TARGET: {want}"
    )
