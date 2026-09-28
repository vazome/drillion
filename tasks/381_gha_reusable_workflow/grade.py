"""What 381 asks for, and what counts as having answered it.

The caller ships read-only, so the brief is empty. actionlint has already read the caller
beside this file and refused an input, secret or output that does not line up; this checks
the declaration as the task states it, and the steps behind it."""

REQUIRED = {"type": "string", "required": True}
LOGIN = {
    "registry": "acmeshop.azurecr.io",
    "username": "acmeshop",
    "password": "${{ secrets.REGISTRY_PASSWORD }}",
}
BUILD = {
    "context": "${{ inputs.context }}",
    "push": True,
    "tags": "acmeshop.azurecr.io/${{ inputs.image }}:${{ github.sha }}",
}


def brief(r):
    return {}


def _expr(value):
    return " ".join(value.split()) if isinstance(value, str) else value


def _uses(step, action):
    return isinstance(step, dict) and str(step.get("uses", "")).startswith(action + "@")


def check(workflow, b):
    assert workflow.get("name") == "build-image", (
        f"the workflow's name is {workflow.get('name')!r}, and it should be 'build-image'"
    )
    on = workflow.get("on")
    assert isinstance(on, dict) and set(on) == {"workflow_call"}, (
        f"`on` is {on!r}, and it should be workflow_call alone: this workflow only runs "
        "when another calls it"
    )
    call = on["workflow_call"] or {}
    inputs = call.get("inputs") or {}
    want = {"image": REQUIRED, "context": REQUIRED}
    assert inputs == want, (
        f"the inputs are {inputs!r}, and they should be exactly {want}"
    )
    secrets = call.get("secrets") or {}
    assert secrets == {"REGISTRY_PASSWORD": {"required": True}}, (
        f"the secrets are {secrets!r}, and they should be exactly REGISTRY_PASSWORD, "
        "required: a secret is declared as a secret, never as an input"
    )
    outputs = {
        k: {kk: _expr(vv) for kk, vv in (v or {}).items()}
        for k, v in (call.get("outputs") or {}).items()
    }
    want = {"digest": {"value": "${{ jobs.build.outputs.digest }}"}}
    assert outputs == want, (
        f"workflow_call.outputs is {call.get('outputs')!r}, and it should be exactly {want}"
    )

    jobs = workflow.get("jobs") or {}
    assert list(jobs) == ["build"], (
        f"the jobs are {list(jobs)}, and there should be one, 'build'"
    )
    job = jobs["build"]
    assert job.get("runs-on") == "ubuntu-latest", (
        f"the job runs on {job.get('runs-on')!r}, and it should be 'ubuntu-latest'"
    )
    got = {k: _expr(v) for k, v in (job.get("outputs") or {}).items()}
    assert got == {"digest": "${{ steps.push.outputs.digest }}"}, (
        f"the job's outputs are {job.get('outputs')!r}, and they should be exactly "
        "digest: ${{ steps.push.outputs.digest }}"
    )
    steps = job.get("steps") or []
    assert len(steps) == 3, f"the job has {len(steps)} steps, and it should have three"
    checkout, login, build = steps
    assert _uses(checkout, "actions/checkout"), (
        f"the first step is {checkout!r}, and it should use actions/checkout"
    )
    assert _uses(login, "docker/login-action"), (
        f"the second step is {login!r}, and it should use docker/login-action"
    )
    got = {k: _expr(v) for k, v in (login.get("with") or {}).items()}
    assert got == LOGIN, (
        f"the login's inputs are {login.get('with')!r}, and they should be exactly {LOGIN}"
    )
    assert _uses(build, "docker/build-push-action") and build.get("id") == "push", (
        f"the third step is {build!r}, and it should use docker/build-push-action with "
        "id: push, the name the job's output reads it by"
    )
    got = {k: _expr(v) for k, v in (build.get("with") or {}).items()}
    assert got == BUILD, (
        f"the build's inputs are {build.get('with')!r}, and they should be exactly {BUILD}"
    )
