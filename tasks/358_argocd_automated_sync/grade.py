"""What one sitting of 358 asks for, and what counts as having answered it.

The schema has already refused a misspelt key under `syncPolicy`. It cannot refuse a sync
option spelt wrong, since each is a free string, so the list is compared exactly."""

APPS = ["checkout", "payments", "search", "orders", "catalog"]
REPOS = [
    "https://github.com/acme/platform-gitops.git",
    "https://github.com/acme/deploy.git",
    "https://gitlab.com/acme/k8s-manifests.git",
]
IN_CLUSTER = "https://kubernetes.default.svc"
BACKOFF = {"duration": "5s", "factor": 2, "maxDuration": "3m"}


def brief(r):
    name = r.choice(APPS)
    return {
        "name": name,
        "repo": r.choice(REPOS),
        "path": f"{r.choice(['apps', 'services'])}/{name}/overlays/prod",
        "namespace": r.choice([name, f"{name}-prod"]),
        "retries": r.choice([3, 5, 10]),
    }


def _application(doc, b):
    assert doc.get("kind") == "Application", (
        f"kind is {doc.get('kind')!r}, and it should be 'Application'"
    )
    meta = doc.get("metadata", {})
    assert meta.get("name") == b["name"], (
        f"metadata.name is {meta.get('name')!r}, and it should be {b['name']!r}"
    )
    assert meta.get("namespace") == "argocd", (
        f"metadata.namespace is {meta.get('namespace')!r}, and an Application lives in "
        "'argocd'"
    )
    spec = doc.get("spec", {})
    assert spec.get("project") == "default", (
        f"spec.project is {spec.get('project')!r}, and it should be 'default'"
    )
    source = spec.get("source") or {}
    want = {"repoURL": b["repo"], "targetRevision": "main", "path": b["path"]}
    got = {k: source.get(k) for k in want}
    assert got == want, f"spec.source is {got}, and it should be {want}"
    dest = spec.get("destination") or {}
    want = {"server": IN_CLUSTER, "namespace": b["namespace"]}
    got = {k: dest.get(k) for k in want}
    assert got == want, f"spec.destination is {got}, and it should be {want}"
    return spec


def check(doc, b):
    policy = _application(doc, b).get("syncPolicy") or {}
    auto = policy.get("automated")
    assert isinstance(auto, dict), (
        "spec.syncPolicy.automated is missing, so Argo CD waits for someone to press Sync"
    )
    assert auto.get("prune") is True, (
        "automated.prune is not true, so a Deployment removed from git keeps running"
    )
    assert auto.get("selfHeal") is True, (
        "automated.selfHeal is not true, so a change made by hand in the cluster stays"
    )
    options = policy.get("syncOptions")
    assert options == ["CreateNamespace=true"], (
        f"syncOptions is {options!r}, and it should be exactly ['CreateNamespace=true']: "
        "an option spelt any other way is ignored without a word"
    )
    retry = policy.get("retry") or {}
    assert retry.get("limit") == b["retries"], (
        f"retry.limit is {retry.get('limit')!r}, and it should be {b['retries']}"
    )
    backoff = retry.get("backoff") or {}
    got = {k: backoff.get(k) for k in BACKOFF}
    assert got == BACKOFF, f"retry.backoff is {got}, and it should be {BACKOFF}"
