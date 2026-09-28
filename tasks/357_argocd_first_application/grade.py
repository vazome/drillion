"""What one sitting of 357 asks for, and what counts as having answered it.

Argo CD's schema has already run by the time `check` does, so a misspelt field is gone. What
is left is what the schema allows and the task does not: `sources` instead of `source`, a
destination by `name`, a `syncPolicy` this first Application must not have."""

APPS = ["checkout", "payments", "search", "orders", "catalog"]
REPOS = [
    "https://github.com/acme/platform-gitops.git",
    "https://github.com/acme/deploy.git",
    "https://gitlab.com/acme/k8s-manifests.git",
]
IN_CLUSTER = "https://kubernetes.default.svc"


def brief(r):
    name = r.choice(APPS)
    return {
        "name": name,
        "repo": r.choice(REPOS),
        "revision": r.choice(["main", "HEAD", "v1.4.0"]),
        "path": f"{r.choice(['apps', 'services', 'workloads'])}/{name}",
        "namespace": r.choice([name, f"{name}-prod", "shop"]),
    }


def check(doc, b):
    assert doc.get("kind") == "Application", (
        f"kind is {doc.get('kind')!r}, and it should be 'Application'"
    )
    meta = doc.get("metadata", {})
    assert meta.get("name") == b["name"], (
        f"metadata.name is {meta.get('name')!r}, and it should be {b['name']!r}"
    )
    assert meta.get("namespace") == "argocd", (
        f"metadata.namespace is {meta.get('namespace')!r}: an Application lives where "
        "Argo CD runs, 'argocd', whatever namespace it deploys to"
    )
    spec = doc.get("spec", {})
    assert spec.get("project") == "default", (
        f"spec.project is {spec.get('project')!r}, and it should be 'default'"
    )
    assert "sources" not in spec, (
        "spec.sources is for an Application built from several sources; this one has "
        "one, and it goes in spec.source"
    )
    source = spec.get("source") or {}
    for key in ("repoURL", "targetRevision", "path"):
        want = b[{"repoURL": "repo", "targetRevision": "revision"}.get(key, key)]
        assert source.get(key) == want, (
            f"spec.source.{key} is {source.get(key)!r}, and it should be {want!r}"
        )
    dest = spec.get("destination") or {}
    assert "name" not in dest, (
        "spec.destination names the cluster by `name` as well: a cluster is named by "
        "`server` or by `name`, never both, and this task uses `server`"
    )
    assert dest.get("server") == IN_CLUSTER, (
        f"spec.destination.server is {dest.get('server')!r}, and the cluster Argo CD "
        f"runs in is {IN_CLUSTER!r}"
    )
    assert dest.get("namespace") == b["namespace"], (
        f"spec.destination.namespace is {dest.get('namespace')!r}, and it should be "
        f"{b['namespace']!r}"
    )
    assert "syncPolicy" not in spec, (
        "spec.syncPolicy is set, and this first Application waits for someone to press "
        "Sync: leave syncPolicy out"
    )
