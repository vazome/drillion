"""What one sitting of 359 asks for, and what counts as having answered it.

`valuesObject` is free-form in the schema, so everything about the values is checked here:
`replicaCount`, and nothing beside it."""

# (repository, chart, version); both charts take `replicaCount` at the top level
CHARTS = [
    ("https://charts.jetstack.io", "cert-manager", "v1.18.2"),
    ("https://charts.external-secrets.io", "external-secrets", "0.19.2"),
]
IN_CLUSTER = "https://kubernetes.default.svc"
OPTIONS = ["CreateNamespace=true", "ServerSideApply=true"]


def brief(r):
    repo, chart, version = r.choice(CHARTS)
    return {"repo": repo, "chart": chart, "version": version, "replicas": r.choice([2, 3])}


def check(doc, b):
    assert doc.get("kind") == "Application", (
        f"kind is {doc.get('kind')!r}, and it should be 'Application'"
    )
    meta = doc.get("metadata", {})
    assert meta.get("name") == b["chart"], (
        f"metadata.name is {meta.get('name')!r}, and it should be {b['chart']!r}"
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
    assert "path" not in source, (
        "spec.source has a `path`, and a chart from a Helm repository is named by "
        "`chart` instead"
    )
    want = {"repoURL": b["repo"], "chart": b["chart"], "targetRevision": b["version"]}
    got = {k: source.get(k) for k in want}
    assert got == want, f"spec.source is {got}, and it should be {want}"
    helm = source.get("helm") or {}
    assert helm.get("releaseName") == b["chart"], (
        f"helm.releaseName is {helm.get('releaseName')!r}, and it should be {b['chart']!r}"
    )
    assert "values" not in helm, (
        "helm.values is a string of YAML no schema can check: put the values in "
        "helm.valuesObject instead"
    )
    want = {"replicaCount": b["replicas"]}
    assert helm.get("valuesObject") == want, (
        f"helm.valuesObject is {helm.get('valuesObject')!r}, and it should be {want}, "
        "and nothing else"
    )
    dest = spec.get("destination") or {}
    want = {"server": IN_CLUSTER, "namespace": b["chart"]}
    got = {k: dest.get(k) for k in want}
    assert got == want, f"spec.destination is {got}, and it should be {want}"
    policy = spec.get("syncPolicy") or {}
    auto = policy.get("automated") or {}
    assert auto.get("prune") is True and auto.get("selfHeal") is True, (
        f"syncPolicy.automated is {policy.get('automated')!r}, and it should have "
        "prune: true and selfHeal: true"
    )
    assert policy.get("syncOptions") == OPTIONS, (
        f"syncOptions is {policy.get('syncOptions')!r}, and it should be exactly {OPTIONS}"
    )
