"""What one sitting of 383 asks for, and what counts as having answered it."""

REGISTRIES = ["acmeshop", "acmeplatform", "contosoprod"]
REPOSITORIES = ["shop/web", "shop/api", "platform/gateway"]
LOGIN = {
    "client-id": "${{ vars.AZURE_CLIENT_ID }}",
    "tenant-id": "${{ vars.AZURE_TENANT_ID }}",
    "subscription-id": "${{ vars.AZURE_SUBSCRIPTION_ID }}",
}


def brief(r):
    acr, repository = r.choice(REGISTRIES), r.choice(REPOSITORIES)
    return {
        "acr": acr,
        "repository": repository,
        "login": f"az acr login --name {acr}",
        "tags": f"{acr}.azurecr.io/{repository}:" + "${{ github.ref_name }}",
    }


def _expr(value):
    return " ".join(value.split()) if isinstance(value, str) else value


def _uses(step, action):
    return isinstance(step, dict) and str(step.get("uses", "")).startswith(action + "@")


def _strings(node):
    if isinstance(node, dict):
        for k, v in node.items():
            yield str(k)
            yield from _strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from _strings(v)
    elif isinstance(node, str):
        yield node


def check(workflow, b):
    assert not any("secrets." in s for s in _strings(workflow)), (
        "the workflow reads a secret, and with OIDC and az acr login there is none to read"
    )
    assert workflow.get("name") == "image", (
        f"the workflow's name is {workflow.get('name')!r}, and it should be 'image'"
    )
    on = workflow.get("on")
    assert on == {"push": {"tags": ["v*"]}}, (
        f"`on` is {on!r}, and it should be exactly push with tags: ['v*']"
    )
    jobs = workflow.get("jobs") or {}
    assert list(jobs) == ["image"], (
        f"the jobs are {list(jobs)}, and there should be one, 'image'"
    )
    job = jobs["image"]
    assert job.get("runs-on") == "ubuntu-latest", (
        f"the job runs on {job.get('runs-on')!r}, and it should be 'ubuntu-latest'"
    )
    want = {"id-token": "write", "contents": "read"}
    assert job.get("permissions") == want, (
        f"the job's permissions are {job.get('permissions')!r}, and they should be "
        f"exactly {want}"
    )
    steps = job.get("steps") or []
    assert len(steps) == 5, f"the job has {len(steps)} steps, and it should have five"
    checkout, azure, acr, buildx, build = steps
    assert _uses(checkout, "actions/checkout"), (
        f"the first step is {checkout!r}, and it should use actions/checkout"
    )
    assert _uses(azure, "azure/login"), (
        f"the second step is {azure!r}, and it should use azure/login"
    )
    got = {k: _expr(v) for k, v in (azure.get("with") or {}).items()}
    assert got == LOGIN, (
        f"azure/login's inputs are {azure.get('with')!r}, and they should be exactly {LOGIN}"
    )
    assert acr.get("run") == b["login"], (
        f"the third step runs {acr.get('run')!r}, and it should run {b['login']!r}"
    )
    assert _uses(buildx, "docker/setup-buildx-action") and not buildx.get("with"), (
        f"the fourth step is {buildx!r}, and it should use docker/setup-buildx-action "
        "with no inputs: the default driver cannot export a cache"
    )
    assert _uses(build, "docker/build-push-action"), (
        f"the fifth step is {build!r}, and it should use docker/build-push-action"
    )
    want = {
        "context": ".",
        "push": True,
        "tags": b["tags"],
        "cache-from": "type=gha",
        "cache-to": "type=gha,mode=max",
    }
    got = {k: _expr(v) for k, v in (build.get("with") or {}).items()}
    assert got == want, (
        f"the build's inputs are {build.get('with')!r}, and they should be exactly {want}"
    )
