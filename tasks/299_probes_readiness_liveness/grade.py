"""What one sitting of 299 asks for, and what counts as having answered it.

The schema has already run by the time `check` does, so the shape is sound and only the
requirements are left. Every message here is what the learner reads, so each one names the
field and what it should have held."""

NAMES = ["checkout", "billing", "inventory", "search", "ledger"]
IMAGES = ["ghcr.io/acme/orders:2.4", "ghcr.io/acme/billing:1.9", "ghcr.io/acme/search:3.1"]
PORTS = [8000, 8080, 3000]


def brief(r):
    return {"name": r.choice(NAMES), "image": r.choice(IMAGES), "port": r.choice(PORTS)}


def _probe(container, key, path, b):
    ports = {p.get("name"): p.get("containerPort") for p in container.get("ports") or []}
    probe = container.get(key)
    assert probe, f"the container has no {key}"
    get = probe.get("httpGet")
    assert get, f"the {key} is not an httpGet, and the task asks for an HTTP check"
    assert get.get("path") == path, (
        f"the {key} asks {get.get('path')!r}, and it should ask {path!r}"
    )
    port = get.get("port")
    port = ports.get(port, port)
    assert port == b["port"], (
        f"the {key} knocks on port {get.get('port')!r}, and the app listens on {b['port']}"
    )


def check(doc, b):
    assert doc.get("kind") == "Deployment", (
        f"this is a {doc.get('kind')}, and the task asks for a Deployment"
    )
    name = doc.get("metadata", {}).get("name")
    assert name == b["name"], f"metadata.name is {name!r}, and it should be {b['name']!r}"
    spec = doc.get("spec", {})
    selector = spec.get("selector", {}).get("matchLabels") or {}
    labels = spec.get("template", {}).get("metadata", {}).get("labels") or {}
    assert selector and all(labels.get(k) == v for k, v in selector.items()), (
        f"spec.selector.matchLabels is {selector} and the pod template is labelled "
        f"{labels}, and the two have to agree"
    )
    containers = spec.get("template", {}).get("spec", {}).get("containers") or []
    assert len(containers) == 1, (
        f"the pod template has {len(containers)} containers, and the task asks for one"
    )
    c = containers[0]
    assert c.get("image") == b["image"], (
        f"the container image is {c.get('image')!r}, not {b['image']!r}"
    )
    declared = [p.get("containerPort") for p in c.get("ports") or []]
    assert b["port"] in declared, (
        f"the container declares ports {declared}, and the app listens on {b['port']}"
    )
    _probe(c, "readinessProbe", "/ready", b)
    _probe(c, "livenessProbe", "/healthz", b)
