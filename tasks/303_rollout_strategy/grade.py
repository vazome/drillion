"""What one sitting of 303 asks for, and what counts as having answered it.

The schema has already run by the time `check` does, so the shape is sound and only the
requirements are left. Every message here is what the learner reads, so each one names the
field and what it should have held."""

NAMES = ["checkout", "billing", "search", "gateway"]
IMAGES = ["ghcr.io/acme/checkout:7.1", "ghcr.io/acme/gateway:2.3", "ghcr.io/acme/search:3.1"]
PROBES = ("httpGet", "tcpSocket", "exec", "grpc")


def brief(r):
    return {
        "name": r.choice(NAMES),
        "image": r.choice(IMAGES),
        "replicas": r.randint(3, 8),
        "surge": r.choice([1, 2]),
        "wait": r.choice([10, 15, 30]),
    }


def check(doc, b):
    assert doc.get("kind") == "Deployment", (
        f"this is a {doc.get('kind')}, and the task asks for a Deployment"
    )
    name = doc.get("metadata", {}).get("name")
    assert name == b["name"], f"metadata.name is {name!r}, and it should be {b['name']!r}"
    spec = doc.get("spec", {})
    assert spec.get("replicas") == b["replicas"], (
        f"spec.replicas is {spec.get('replicas')!r}, and it should be {b['replicas']}"
    )
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

    strategy = spec.get("strategy") or {}
    assert strategy.get("type") == "RollingUpdate", (
        f"spec.strategy.type is {strategy.get('type')!r}, and it should be "
        "'RollingUpdate': Recreate stops every old pod before starting a new one"
    )
    rolling = strategy.get("rollingUpdate") or {}
    unavailable = rolling.get("maxUnavailable")
    assert unavailable in (0, "0%"), (
        f"maxUnavailable is {unavailable!r}, so the rollout may take pods away before "
        "their replacements are ready; it should be 0"
    )
    assert rolling.get("maxSurge") == b["surge"], (
        f"maxSurge is {rolling.get('maxSurge')!r}, and it should be {b['surge']}"
    )
    assert spec.get("minReadySeconds") == b["wait"], (
        f"spec.minReadySeconds is {spec.get('minReadySeconds')!r}, and it should be "
        f"{b['wait']}"
    )
    probe = c.get("readinessProbe") or {}
    assert any(k in probe for k in PROBES), (
        "the container has no readinessProbe, so a pod counts as ready the moment it "
        "starts and the rollout has nothing to wait for"
    )
