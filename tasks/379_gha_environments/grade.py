"""What one sitting of 379 asks for, and what counts as having answered it.

Only the workflow is graded: which environment each job names, in which order, and how
each is guarded against a second run. The protection rules in ENVIRONMENTS.md are
repository settings, and nothing here can see them."""

APPS = ["cart", "checkout", "search", "ledger"]
ORDER = [("dev", None), ("staging", "dev"), ("production", "staging")]


def brief(r):
    app = r.choice(APPS)
    return {
        "app": app,
        "dev_url": f"https://dev.{app}.acme.io",
        "staging_url": f"https://staging.{app}.acme.io",
        "production_url": f"https://{app}.acme.io",
    }


def _needs(job):
    needs = job.get("needs") or []
    return {needs} if isinstance(needs, str) else set(needs)


def _uses(step, action):
    return isinstance(step, dict) and str(step.get("uses", "")).startswith(action + "@")


def check(workflow, b):
    assert workflow.get("name") == "release", (
        f"the workflow's name is {workflow.get('name')!r}, and it should be 'release'"
    )
    on = workflow.get("on")
    assert on == {"push": {"branches": ["main"]}}, (
        f"`on` is {on!r}, and it should be exactly push with branches: [main]"
    )
    jobs = workflow.get("jobs") or {}
    names = {f"deploy-{env}" for env, _ in ORDER}
    assert set(jobs) == names, (
        f"the jobs are {sorted(jobs)}, and they should be {sorted(names)}"
    )
    for env, before in ORDER:
        name = f"deploy-{env}"
        job = jobs[name]
        assert job.get("runs-on") == "ubuntu-latest", (
            f"{name} runs on {job.get('runs-on')!r}, and it should be 'ubuntu-latest'"
        )
        want = {f"deploy-{before}"} if before else set()
        assert _needs(job) == want, (
            f"{name} needs {sorted(_needs(job))}, and it should need "
            + (f"deploy-{before}" if before else "nothing")
        )
        environment = job.get("environment")
        want = {"name": env, "url": b[f"{env}_url"]}
        assert environment == want, (
            f"{name}'s environment is {environment!r}, and it should be exactly {want}"
            + (
                ": an environment spelt differently is a new one, with no protection"
                if isinstance(environment, dict) and environment.get("name") != env
                else ""
            )
        )
        want = {"group": f"deploy-{env}", "cancel-in-progress": False}
        assert job.get("concurrency") == want, (
            f"{name}'s concurrency is {job.get('concurrency')!r}, and it should be "
            f"exactly {want}"
        )
        steps = job.get("steps") or []
        assert len(steps) == 2, f"{name} has {len(steps)} steps, and it should have two"
        assert _uses(steps[0], "actions/checkout"), (
            f"{name}'s first step is {steps[0]!r}, and it should use actions/checkout"
        )
        assert steps[1].get("run") == f"./deploy.sh {env}", (
            f"{name}'s second step runs {steps[1].get('run')!r}, and it should run "
            f"'./deploy.sh {env}'"
        )
