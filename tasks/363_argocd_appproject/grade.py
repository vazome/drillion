"""What one sitting of 363 asks for, and what counts as having answered it.

The project's lists are compared exactly: a second repository, a wider pattern or a
missing deny entry is a looser project, and a looser project is the thing being taught."""

TEAMS = ["payments", "search", "growth", "logistics"]
APPS = {"payments": "ledger", "search": "indexer", "growth": "campaigns", "logistics": "tracker"}
IN_CLUSTER = "https://kubernetes.default.svc"
DENIED = [{"group": "", "kind": "ResourceQuota"}, {"group": "", "kind": "LimitRange"}]


def brief(r):
    team = r.choice(TEAMS)
    app = APPS[team]
    return {
        "team": team,
        "repo": f"https://github.com/acme/{team}-deploy.git",
        "pattern": f"{team}-*",
        "app": app,
        "path": f"apps/{app}",
        "namespace": f"{team}-{r.choice(['dev', 'staging', 'prod'])}",
    }


def check_many(docs, b):
    assert len(docs) == 2, (
        f"the file holds {len(docs)} documents, and the task asks for two: the "
        "AppProject, then the Application"
    )
    project, app = docs

    assert project.get("kind") == "AppProject", (
        f"the first document is a {project.get('kind')}, and it should be the AppProject"
    )
    meta = project.get("metadata") or {}
    assert meta.get("name") == b["team"], (
        f"the AppProject is named {meta.get('name')!r}, and it should be {b['team']!r}"
    )
    assert meta.get("namespace") == "argocd", (
        f"the AppProject's metadata.namespace is {meta.get('namespace')!r}, and a project "
        "lives in 'argocd'"
    )
    spec = project.get("spec") or {}
    assert spec.get("sourceRepos") == [b["repo"]], (
        f"sourceRepos is {spec.get('sourceRepos')!r}, and it should be exactly "
        f"[{b['repo']!r}]"
    )
    want = [{"server": IN_CLUSTER, "namespace": b["pattern"]}]
    assert spec.get("destinations") == want, (
        f"destinations is {spec.get('destinations')!r}, and it should be exactly {want}"
    )
    assert not spec.get("clusterResourceWhitelist"), (
        f"clusterResourceWhitelist allows {spec['clusterResourceWhitelist']!r}, and this "
        "team should create no cluster-scoped object: leave it out"
    )
    denied = spec.get("namespaceResourceBlacklist") or []
    assert sorted(denied, key=str) == sorted(DENIED, key=str), (
        f"namespaceResourceBlacklist is {denied!r}, and it should deny exactly "
        "ResourceQuota and LimitRange, both in the core group ''"
    )

    assert app.get("kind") == "Application", (
        f"the second document is a {app.get('kind')}, and it should be the Application"
    )
    meta = app.get("metadata") or {}
    assert meta.get("name") == b["app"], (
        f"the Application is named {meta.get('name')!r}, and it should be {b['app']!r}"
    )
    assert meta.get("namespace") == "argocd", (
        f"the Application's metadata.namespace is {meta.get('namespace')!r}, and it "
        "lives in 'argocd'"
    )
    spec = app.get("spec") or {}
    assert spec.get("project") == b["team"], (
        f"the Application's spec.project is {spec.get('project')!r}, and it should be "
        f"{b['team']!r}: in 'default' none of these limits apply"
    )
    source = spec.get("source") or {}
    want = {"repoURL": b["repo"], "targetRevision": "main", "path": b["path"]}
    got = {k: source.get(k) for k in want}
    assert got == want, f"the Application's source is {got}, and it should be {want}"
    dest = spec.get("destination") or {}
    want = {"server": IN_CLUSTER, "namespace": b["namespace"]}
    got = {k: dest.get(k) for k in want}
    assert got == want, f"the Application's destination is {got}, and it should be {want}"
    policy = spec.get("syncPolicy") or {}
    auto = policy.get("automated") or {}
    assert auto.get("prune") is True and auto.get("selfHeal") is True, (
        f"the Application's syncPolicy.automated is {auto or None}, and it should have "
        "prune: true and selfHeal: true"
    )
    assert "CreateNamespace=true" not in (policy.get("syncOptions") or []), (
        "the Application has CreateNamespace=true, and its project may create no "
        "Namespace: the sync would be refused"
    )
