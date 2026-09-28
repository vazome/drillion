"""What one sitting of 364 asks for, and what counts as having answered it.

The schema allows any group, kind and pointer, so the one entry is compared exactly: a wrong
group or a pointer to the wrong field ignores nothing the autoscaler touches."""

APPS = ["checkout", "search", "gateway", "thumbnails"]
REPOS = [
    "https://github.com/acme/platform-gitops.git",
    "https://github.com/acme/deploy.git",
]
IN_CLUSTER = "https://kubernetes.default.svc"


def brief(r):
    name = r.choice(APPS)
    return {
        "name": name,
        "repo": r.choice(REPOS),
        "path": f"apps/{name}",
        "namespace": r.choice([name, f"{name}-prod"]),
    }


def check(doc, b):
    assert doc.get("kind") == "Application", (
        f"kind is {doc.get('kind')!r}, and it should be 'Application'"
    )
    meta = doc.get("metadata") or {}
    assert meta.get("name") == b["name"], (
        f"metadata.name is {meta.get('name')!r}, and it should be {b['name']!r}"
    )
    assert meta.get("namespace") == "argocd", (
        f"metadata.namespace is {meta.get('namespace')!r}, and an Application lives in "
        "'argocd'"
    )
    spec = doc.get("spec") or {}
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
    policy = spec.get("syncPolicy") or {}
    auto = policy.get("automated") or {}
    assert auto.get("prune") is True and auto.get("selfHeal") is True, (
        f"syncPolicy.automated is {auto or None}, and it should have prune: true and "
        "selfHeal: true"
    )
    assert policy.get("syncOptions") == ["RespectIgnoreDifferences=true"], (
        f"syncOptions is {policy.get('syncOptions')!r}, and it should be exactly "
        "['RespectIgnoreDifferences=true']: without it the diff ignores replicas, and "
        "the next sync resets them anyway"
    )
    ignored = spec.get("ignoreDifferences") or []
    assert len(ignored) == 1, (
        f"ignoreDifferences has {len(ignored)} entries, and the task asks for one"
    )
    entry = ignored[0]
    want = {"group": "apps", "kind": "Deployment", "name": b["name"]}
    got = {k: entry.get(k) for k in want}
    assert got == want, f"the ignoreDifferences entry is {got}, and it should be {want}"
    assert entry.get("jsonPointers") == ["/spec/replicas"], (
        f"jsonPointers is {entry.get('jsonPointers')!r}, and it should be exactly "
        "['/spec/replicas']"
    )
    extra = sorted(set(entry) - {"group", "kind", "name", "jsonPointers"})
    assert not extra, (
        f"the ignoreDifferences entry also sets {extra}, and it needs only group, kind, "
        "name and jsonPointers"
    )
