"""What one sitting of 300 asks for, and what counts as having answered it.

The schema has already run by the time `check` does, so the shape is sound and only the
requirements are left. Every message here is what the learner reads, so each one names the
field and what it should have held.

`tries` is not shown to the learner: it is the answer key's own threshold, one of many
that cover the boot."""

NAMES = ["indexer", "reports", "catalog", "ledger"]
IMAGES = ["ghcr.io/acme/indexer:5.2", "ghcr.io/acme/reports:1.4", "ghcr.io/acme/catalog:3.0"]
PORTS = [8080, 9000]


def brief(r):
    boot = r.choice([90, 120, 180, 240, 300])
    return {
        "name": r.choice(NAMES),
        "image": r.choice(IMAGES),
        "port": r.choice(PORTS),
        "boot": boot,
        "tries": boot // 10,
    }


def _http(container, key, b):
    ports = {p.get("name"): p.get("containerPort") for p in container.get("ports") or []}
    probe = container.get(key)
    assert probe, f"the container has no {key}"
    get = probe.get("httpGet") or {}
    assert get.get("path") == "/healthz", (
        f"the {key} asks {get.get('path')!r}, and it should do an HTTP GET of '/healthz'"
    )
    port = ports.get(get.get("port"), get.get("port"))
    assert port == b["port"], (
        f"the {key} knocks on port {get.get('port')!r}, and the app listens on {b['port']}"
    )
    return probe


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

    startup = _http(c, "startupProbe", b)
    period = startup.get("periodSeconds", 10)
    tries = startup.get("failureThreshold", 3)
    assert period * tries >= b["boot"], (
        f"the startup probe gives up after {tries} x {period} = {period * tries}s, and "
        f"the app can take {b['boot']}s to boot, so a slow start gets killed"
    )
    liveness = _http(c, "livenessProbe", b)
    assert not liveness.get("initialDelaySeconds"), (
        "the liveness probe waits initialDelaySeconds before it starts, and that wait is "
        "the startup probe's job: every restart after a crash would pay it again"
    )
