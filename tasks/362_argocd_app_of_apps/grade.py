"""What one sitting of 362 asks for, and what counts as having answered it.

Three Applications with the same frame and three different jobs: the root deploys into
`argocd`, and each child carries the finalizer and its own wave."""

REPOS = [
    "https://github.com/acme/platform-gitops.git",
    "https://github.com/acme/clusters.git",
]
CLUSTERS = ["aks-prod-weu", "aks-prod-neu", "aks-dev-weu"]
INFRA = ["cert-manager", "external-secrets", "ingress-nginx"]
APPS = ["checkout", "payments", "orders", "catalog"]
IN_CLUSTER = "https://kubernetes.default.svc"
WAVE = "argocd.argoproj.io/sync-wave"
FINALIZER = "resources-finalizer.argocd.argoproj.io"


def brief(r):
    cluster, infra, app = r.choice(CLUSTERS), r.choice(INFRA), r.choice(APPS)
    return {
        "repo": r.choice(REPOS),
        "cluster": cluster,
        "root": f"{cluster}-root",
        "root_path": f"clusters/{cluster}",
        "infra": infra,
        "infra_path": f"platform/{infra}",
        "app": app,
        "app_path": f"apps/{app}",
    }


def _application(doc, which, name, path, namespace, b):
    assert doc.get("kind") == "Application", (
        f"the {which} document is a {doc.get('kind')}, and it should be an Application"
    )
    meta = doc.get("metadata") or {}
    assert meta.get("name") == name, (
        f"the {which} Application is named {meta.get('name')!r}, and it should be {name!r}"
    )
    assert meta.get("namespace") == "argocd", (
        f"{name}'s metadata.namespace is {meta.get('namespace')!r}, and an Application "
        "lives in 'argocd'"
    )
    spec = doc.get("spec") or {}
    assert spec.get("project") == "default", (
        f"{name}'s spec.project is {spec.get('project')!r}, and it should be 'default'"
    )
    source = spec.get("source") or {}
    want = {"repoURL": b["repo"], "targetRevision": "main", "path": path}
    got = {k: source.get(k) for k in want}
    assert got == want, f"{name}'s spec.source is {got}, and it should be {want}"
    dest = spec.get("destination") or {}
    want = {"server": IN_CLUSTER, "namespace": namespace}
    got = {k: dest.get(k) for k in want}
    assert got == want, (
        f"{name}'s spec.destination is {got}, and it should be {want}"
        + (
            ": the root deploys Applications, and they live in argocd"
            if namespace == "argocd"
            else ""
        )
    )
    auto = (spec.get("syncPolicy") or {}).get("automated") or {}
    assert auto.get("prune") is True and auto.get("selfHeal") is True, (
        f"{name}'s syncPolicy.automated is {auto or None}, and it should have prune: true "
        "and selfHeal: true: the root creating an Application does not sync it"
    )
    return meta, spec


def _child(doc, which, name, path, wave, b):
    meta, spec = _application(doc, which, name, path, name, b)
    assert meta.get("finalizers") == [FINALIZER], (
        f"{name}'s finalizers are {meta.get('finalizers')!r}, and they should be "
        f"[{FINALIZER!r}]: without it, deleting {name} leaves everything it deployed "
        "running with no owner"
    )
    got = (meta.get("annotations") or {}).get(WAVE, "0")
    assert got == wave, f"{name} is in wave {got}, and it should be in wave {wave}"
    options = (spec.get("syncPolicy") or {}).get("syncOptions")
    assert options == ["CreateNamespace=true"], (
        f"{name}'s syncOptions is {options!r}, and it should be exactly "
        "['CreateNamespace=true']"
    )


def check_many(docs, b):
    assert len(docs) == 3, (
        f"the file holds {len(docs)} documents, and the task asks for three: the root, "
        f"then {b['infra']}, then {b['app']}"
    )
    root, infra, app = docs
    meta, _ = _application(root, "first", b["root"], b["root_path"], "argocd", b)
    assert not meta.get("finalizers"), (
        f"the root has the finalizers {meta['finalizers']!r}, and the task asks for none: "
        "deleting the root should not take the whole cluster with it"
    )
    _child(infra, "second", b["infra"], b["infra_path"], "-1", b)
    _child(app, "third", b["app"], b["app_path"], "0", b)
