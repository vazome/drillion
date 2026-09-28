"""What one sitting of 378 asks for, and what counts as having answered it.

"No secret" is checked over the whole file as the grader sees it, every string in it, so a
`secrets.` expression anywhere fails however it got there."""

CLUSTERS = [("rg-shop-prod", "aks-shop-prod"), ("rg-platform-weu", "aks-platform-weu")]
LOGIN = {
    "client-id": "${{ vars.AZURE_CLIENT_ID }}",
    "tenant-id": "${{ vars.AZURE_TENANT_ID }}",
    "subscription-id": "${{ vars.AZURE_SUBSCRIPTION_ID }}",
}


def brief(r):
    group, cluster = r.choice(CLUSTERS)
    return {
        "group": group,
        "cluster": cluster,
        "credentials": f"az aks get-credentials --resource-group {group} --name {cluster}",
    }


def _expr(text):
    return " ".join(str(text).split())


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
        "the workflow reads a secret, and with OIDC there is none to read: every ID "
        "comes from vars"
    )
    assert workflow.get("name") == "deploy", (
        f"the workflow's name is {workflow.get('name')!r}, and it should be 'deploy'"
    )
    on = workflow.get("on")
    assert on == {"push": {"branches": ["main"]}}, (
        f"`on` is {on!r}, and it should be exactly push with branches: [main]"
    )
    jobs = workflow.get("jobs") or {}
    assert list(jobs) == ["deploy"], (
        f"the jobs are {list(jobs)}, and there should be one, 'deploy'"
    )
    job = jobs["deploy"]
    assert job.get("runs-on") == "ubuntu-latest", (
        f"the job runs on {job.get('runs-on')!r}, and it should be 'ubuntu-latest'"
    )
    assert job.get("environment") == "production", (
        f"the job's environment is {job.get('environment')!r}, and it should be "
        "'production': the federated credential trusts that environment's token only"
    )
    want = {"id-token": "write", "contents": "read"}
    assert job.get("permissions") == want, (
        f"the job's permissions are {job.get('permissions')!r}, and they should be "
        f"exactly {want}: without id-token: write GitHub issues no token"
    )
    steps = job.get("steps") or []
    assert len(steps) == 4, f"the job has {len(steps)} steps, and it should have four"
    checkout, login, creds, apply = steps
    assert _uses(checkout, "actions/checkout"), (
        f"the first step is {checkout!r}, and it should use actions/checkout"
    )
    assert _uses(login, "azure/login"), (
        f"the second step is {login!r}, and it should use azure/login"
    )
    got = {k: _expr(v) for k, v in (login.get("with") or {}).items()}
    assert "creds" not in got, (
        "azure/login has `creds`, a stored service principal secret: OIDC needs only the "
        "three IDs"
    )
    assert got == LOGIN, (
        f"azure/login's inputs are {login.get('with')!r}, and they should be exactly {LOGIN}"
    )
    assert creds.get("run") == b["credentials"], (
        f"the third step runs {creds.get('run')!r}, and it should run {b['credentials']!r}"
    )
    assert apply.get("run") == "kubectl apply -k k8s/overlays/production", (
        f"the fourth step runs {apply.get('run')!r}, and it should run "
        "'kubectl apply -k k8s/overlays/production'"
    )
