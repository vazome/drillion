"""What one sitting of 365 asks for, and what counts as having answered it.

Nothing expands the set: the elements are compared as the three the brief names, and the
template's values as the Go template text each has to be. A name that does not read the
environment is refused by name, since every element would then write the same Application."""

APPS = ["checkout", "payments", "search", "orders"]
REPOS = [
    "https://github.com/acme/platform-gitops.git",
    "https://github.com/acme/deploy.git",
]
REGIONS = {"weu": "westeurope", "neu": "northeurope", "sdc": "swedencentral"}
ENVS = ("dev", "staging", "prod")


def brief(r):
    app = r.choice(APPS)
    short = r.choice(sorted(REGIONS))
    urls = {
        f"{env}_url": f"https://aks-{env}-{short}.hcp.{REGIONS[short]}.azmk8s.io:443"
        for env in ENVS
    }
    return {
        "app": app,
        "repo": r.choice(REPOS),
        "name_tpl": "{{.env}}-" + app,
        "path_tpl": f"apps/{app}/envs/" + "{{.env}}",
        **urls,
    }


def _env(element):
    return str(element.get("env")) if isinstance(element, dict) else ""


def check(doc, b):
    assert doc.get("kind") == "ApplicationSet", (
        f"kind is {doc.get('kind')!r}, and it should be 'ApplicationSet'"
    )
    meta = doc.get("metadata") or {}
    assert meta.get("name") == b["app"], (
        f"metadata.name is {meta.get('name')!r}, and it should be {b['app']!r}"
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
        "['missingkey=error']: without it a misspelt parameter renders as nothing"
    )

    generators = spec.get("generators") or []
    assert len(generators) == 1 and set(generators[0]) == {"list"}, (
        f"spec.generators is {generators!r}, and it should be exactly one list generator"
    )
    elements = (generators[0]["list"] or {}).get("elements") or []
    want = [{"env": env, "url": b[f"{env}_url"]} for env in ENVS]
    assert sorted(elements, key=_env) == sorted(want, key=_env), (
        f"the list elements are {elements!r}, and they should be exactly {want}"
    )

    template = spec.get("template") or {}
    name = (template.get("metadata") or {}).get("name")
    assert name is not None and "{{.env}}" in name, (
        f"the template's metadata.name is {name!r}, and it does not read .env: every "
        "element would write the same Application"
    )
    assert name == b["name_tpl"], (
        f"the template's metadata.name is {name!r}, and it should be {b['name_tpl']!r}"
    )
    tspec = template.get("spec") or {}
    assert tspec.get("project") == "default", (
        f"the template's project is {tspec.get('project')!r}, and it should be 'default'"
    )
    source = tspec.get("source") or {}
    want = {"repoURL": b["repo"], "targetRevision": "main", "path": b["path_tpl"]}
    got = {k: source.get(k) for k in want}
    assert got == want, f"the template's source is {got}, and it should be {want}"
    dest = tspec.get("destination") or {}
    want = {"server": "{{.url}}", "namespace": b["app"]}
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
