"""What one sitting of 360 asks for, and what counts as having answered it.

A wave is read the way Argo CD reads it: no annotation is wave 0. The messages say what order
the annotations give, assuming each wave turns healthy, since nothing here is synced."""

APPS = ["checkout", "payments", "orders", "catalog"]
WAVE = "argocd.argoproj.io/sync-wave"


def brief(r):
    name = r.choice(APPS)
    return {
        "name": name,
        "db": f"{name}-db",
        "image": f"ghcr.io/acme/{name}:{r.choice(['3.2.0', '1.9.4', '2.0.1'])}",
        "db_image": r.choice(["postgres:17.6", "postgres:16.10"]),
    }


def _wave(doc):
    return ((doc.get("metadata") or {}).get("annotations") or {}).get(WAVE, "0")


def _named(doc, which, kind, name):
    assert doc.get("kind") == kind, (
        f"the {which} document is a {doc.get('kind')}, and it should be the {kind}"
    )
    got = (doc.get("metadata") or {}).get("name")
    assert got == name, f"the {kind}'s metadata.name is {got!r}, and it should be {name!r}"


def _pods(doc, kind, app):
    spec = doc.get("spec", {})
    selector = (spec.get("selector") or {}).get("matchLabels")
    assert selector == {"app": app}, (
        f"the {kind}'s spec.selector.matchLabels is {selector}, and it should be "
        f"{{'app': {app!r}}}"
    )
    labels = ((spec.get("template") or {}).get("metadata") or {}).get("labels") or {}
    assert labels.get("app") == app, (
        f"the {kind}'s pod template is labelled {labels}, and it needs app: {app!r}"
    )
    containers = ((spec.get("template") or {}).get("spec") or {}).get("containers") or []
    assert len(containers) == 1, (
        f"the {kind}'s pod template has {len(containers)} containers, and it should have one"
    )
    return spec, containers[0]


def check_many(docs, b):
    assert len(docs) == 3, (
        f"the file holds {len(docs)} documents, and the task asks for three: the Service, "
        "the StatefulSet and the Deployment"
    )
    service, stateful, deploy = docs

    _named(service, "first", "Service", b["db"])
    spec = service.get("spec", {})
    assert spec.get("clusterIP") == "None", (
        f"the Service's clusterIP is {spec.get('clusterIP')!r}, and a headless one is 'None'"
    )
    assert spec.get("selector") == {"app": b["db"]}, (
        f"the Service selects {spec.get('selector')}, and it should select "
        f"{{'app': {b['db']!r}}}"
    )
    ports = [p.get("port") for p in spec.get("ports") or []]
    assert ports == [5432], f"the Service's ports are {ports}, and it should be [5432]"

    _named(stateful, "second", "StatefulSet", b["db"])
    spec, container = _pods(stateful, "StatefulSet", b["db"])
    assert spec.get("serviceName") == b["db"], (
        f"the StatefulSet's serviceName is {spec.get('serviceName')!r}, and it should be "
        f"{b['db']!r}"
    )
    assert spec.get("replicas") == 1, (
        f"the StatefulSet's replicas is {spec.get('replicas')!r}, and it should be 1"
    )
    assert container.get("name") == b["db"] and container.get("image") == b["db_image"], (
        f"the StatefulSet's container is {container.get('name')!r} running "
        f"{container.get('image')!r}, and it should be {b['db']!r} running {b['db_image']!r}"
    )

    for doc in (service, stateful):
        assert _wave(doc) == "0", (
            f"the {doc['kind']} is in wave {_wave(doc)}, and the database belongs in wave "
            "0: leave the annotation out"
        )

    _named(deploy, "third", "Deployment", b["name"])
    assert _wave(deploy) == "1", (
        f"the Deployment is in wave {_wave(deploy)}, so Argo CD applies it "
        + (
            "together with the database, and kind order puts a Deployment before a "
            "StatefulSet: annotate it argocd.argoproj.io/sync-wave: \"1\""
            if _wave(deploy) == "0"
            else "at the wrong point: it should be wave \"1\", right after the database"
        )
    )
    spec, container = _pods(deploy, "Deployment", b["name"])
    assert spec.get("replicas") == 2, (
        f"the Deployment's replicas is {spec.get('replicas')!r}, and it should be 2"
    )
    assert container.get("name") == b["name"] and container.get("image") == b["image"], (
        f"the Deployment's container is {container.get('name')!r} running "
        f"{container.get('image')!r}, and it should be {b['name']!r} running {b['image']!r}"
    )
    env = container.get("env") or []
    want = [{"name": "DATABASE_HOST", "value": b["db"]}]
    assert env == want, f"the container's env is {env}, and it should be {want}"
