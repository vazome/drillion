"""What one sitting of 366 asks for, and what counts as having answered it.

The directories are compared as a set of entries, since an exclude wins whatever order it
is written in; an entry without `exclude` is read as `exclude: false`, as Argo CD reads it."""

ROOTS = ["apps", "services", "workloads"]
SKIPPED = ["legacy-billing", "sandbox", "experimental"]
REPOS = [
    "https://github.com/acme/platform-gitops.git",
    "https://github.com/acme/deploy.git",
]
IN_CLUSTER = "https://kubernetes.default.svc"


def brief(r):
    root, skipped = r.choice(ROOTS), r.choice(SKIPPED)
    return {
        "name": f"every-{root}",
        "repo": r.choice(REPOS),
        "root": root,
        "skipped": skipped,
        "pattern": f"{root}/*",
        "excluded": f"{root}/{skipped}",
    }


def _entry(d):
    if not isinstance(d, dict):
        return (repr(d), False)
    return (d.get("path"), bool(d.get("exclude", False)))


def check(doc, b):
    assert doc.get("kind") == "ApplicationSet", (
        f"kind is {doc.get('kind')!r}, and it should be 'ApplicationSet'"
    )
    meta = doc.get("metadata") or {}
    assert meta.get("name") == b["name"], (
        f"metadata.name is {meta.get('name')!r}, and it should be {b['name']!r}"
    )
    assert meta.get("namespace") == "argocd", (
        f"metadata.namespace is {meta.get('namespace')!r}, and an ApplicationSet lives "
        "in 'argocd'"
    )
    spec = doc.get("spec") or {}
    assert spec.get("goTemplate") is True, (
        "spec.goTemplate is not true, so the template's Go expressions are never filled in"
    )
    assert spec.get("goTemplateOptions") == ["missingkey=error"], (
        f"spec.goTemplateOptions is {spec.get('goTemplateOptions')!r}, and it should be "
        "['missingkey=error']"
    )

    generators = spec.get("generators") or []
    assert len(generators) == 1 and set(generators[0]) == {"git"}, (
        f"spec.generators is {generators!r}, and it should be exactly one git generator"
    )
    git = generators[0]["git"] or {}
    want = {"repoURL": b["repo"], "revision": "main"}
    got = {k: git.get(k) for k in want}
    assert got == want, f"the git generator scans {got}, and it should scan {want}"
    assert not git.get("files"), (
        "the git generator has `files`, and this task generates from directories alone"
    )
    dirs = git.get("directories") or []
    want = {(b["pattern"], False), (b["excluded"], True)}
    got = {_entry(d) for d in dirs}
    assert len(dirs) == 2 and got == want, (
        f"directories is {dirs!r}, and it should be exactly two entries: "
        f"path {b['pattern']!r}, and path {b['excluded']!r} with exclude: true"
    )

    template = spec.get("template") or {}
    name = (template.get("metadata") or {}).get("name")
    assert name == "{{.path.basename}}", (
        f"the template's metadata.name is {name!r}, and it should be '{{{{.path.basename}}}}'"
    )
    tspec = template.get("spec") or {}
    assert tspec.get("project") == "default", (
        f"the template's project is {tspec.get('project')!r}, and it should be 'default'"
    )
    source = tspec.get("source") or {}
    want = {"repoURL": b["repo"], "targetRevision": "main", "path": "{{.path.path}}"}
    got = {k: source.get(k) for k in want}
    assert got == want, f"the template's source is {got}, and it should be {want}"
    dest = tspec.get("destination") or {}
    want = {"server": IN_CLUSTER, "namespace": "{{.path.basename}}"}
    got = {k: dest.get(k) for k in want}
    assert got == want, f"the template's destination is {got}, and it should be {want}"
    policy = tspec.get("syncPolicy") or {}
    auto = policy.get("automated") or {}
    assert auto.get("prune") is True and auto.get("selfHeal") is True, (
        f"the template's syncPolicy.automated is {auto or None}, and it should have "
        "prune: true and selfHeal: true"
    )
    assert policy.get("syncOptions") == ["CreateNamespace=true"], (
        f"the template's syncOptions is {policy.get('syncOptions')!r}, and it should be "
        "exactly ['CreateNamespace=true']"
    )
