"""What 382 asks for, and what counts as having answered it.

The reusable deploy ships read-only, so the brief is empty. actionlint has already checked
every `with` against the deploy's inputs; the permissions the deploy needs are a rule it
does not check, so this does."""

DEPLOY = "./.github/workflows/deploy.yml"
TAG = "${{ github.ref_name }}"


def brief(r):
    return {}


def _needs(job):
    needs = job.get("needs") or []
    return {needs} if isinstance(needs, str) else set(needs)


def _calls(jobs, name, environment, needs):
    job = jobs[name]
    assert job.get("uses") == DEPLOY, (
        f"{name} uses {job.get('uses')!r}, and it should call {DEPLOY!r}"
    )
    extra = sorted({"runs-on", "steps"} & set(job))
    assert not extra, (
        f"{name} has {extra}, and a job that calls a workflow has neither: the called "
        "workflow brings its own"
    )
    given = {k: " ".join(str(v).split()) for k, v in (job.get("with") or {}).items()}
    want = {"environment": environment, "image-tag": TAG}
    assert given == want, (
        f"{name}'s with is {job.get('with')!r}, and it should be exactly {want}"
    )
    assert _needs(job) == needs, (
        f"{name} needs {sorted(_needs(job))}, and it should need "
        + (", ".join(sorted(needs)) or "nothing")
    )


def check(workflow, b):
    assert workflow.get("name") == "release", (
        f"the workflow's name is {workflow.get('name')!r}, and it should be 'release'"
    )
    on = workflow.get("on")
    assert on == {"push": {"tags": ["v*"]}}, (
        f"`on` is {on!r}, and it should be exactly push with tags: ['v*']"
    )
    want = {"contents": "read", "id-token": "write"}
    got = workflow.get("permissions")
    assert got == want, (
        f"the workflow's permissions are {got!r}, and they should be exactly {want}"
        + (
            ": the deploy asks for id-token: write, and a called workflow can only "
            "narrow the caller's token"
            if isinstance(got, dict) and got.get("id-token") != "write"
            else ""
        )
    )
    jobs = workflow.get("jobs") or {}
    assert set(jobs) == {"staging", "production"}, (
        f"the jobs are {sorted(jobs)}, and they should be staging and production"
    )
    _calls(jobs, "staging", "staging", set())
    _calls(jobs, "production", "production", {"staging"})
