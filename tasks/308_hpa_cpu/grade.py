"""What one sitting of 308 asks for, and what counts as having answered it.

The schema has already run by the time `check_many` does, and the file holds two objects,
`---`-separated, so they arrive here as a list. Every message here is what the learner
reads, so each one names the field and what it should have held."""

NAMES = ["checkout", "search", "gateway", "thumbnails"]
IMAGES = ["ghcr.io/acme/checkout:7.1", "ghcr.io/acme/gateway:2.3", "ghcr.io/acme/search:3.1"]
CPUS = ["100m", "250m", "500m"]


def brief(r):
    low = r.randint(2, 4)
    return {
        "name": r.choice(NAMES),
        "image": r.choice(IMAGES),
        "cpu": r.choice(CPUS),
        "min": low,
        "max": low + r.choice([4, 6, 8]),
        "target": r.choice([60, 70, 80]),
    }


def check_many(docs, b):
    assert len(docs) == 2, (
        f"the file holds {len(docs)} documents, and the task asks for two: the "
        "Deployment first, then its HorizontalPodAutoscaler"
    )
    deploy, hpa = docs
    assert deploy.get("kind") == "Deployment", (
        f"the first document is a {deploy.get('kind')}, and the Deployment goes first"
    )
    name = deploy.get("metadata", {}).get("name")
    assert name == b["name"], (
        f"the Deployment's metadata.name is {name!r}, and it should be {b['name']!r}"
    )
    spec = deploy.get("spec", {})
    assert "replicas" not in spec, (
        f"the Deployment sets spec.replicas: {spec.get('replicas')!r}, and every apply "
        "of this file would reset the count the autoscaler chose"
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
    cpu = ((c.get("resources") or {}).get("requests") or {}).get("cpu")
    assert cpu == b["cpu"], (
        f"resources.requests.cpu is {cpu!r}, and it should be {b['cpu']!r}: utilization "
        "is a percentage of the request, so without one the autoscaler cannot scale"
    )

    assert hpa.get("kind") == "HorizontalPodAutoscaler", (
        f"the second document is a {hpa.get('kind')}, and the task asks for a "
        "HorizontalPodAutoscaler"
    )
    assert hpa.get("apiVersion") == "autoscaling/v2", (
        f"the HPA's apiVersion is {hpa.get('apiVersion')!r}, and it should be "
        "'autoscaling/v2'"
    )
    hspec = hpa.get("spec", {})
    ref = hspec.get("scaleTargetRef") or {}
    want = {"apiVersion": "apps/v1", "kind": "Deployment", "name": b["name"]}
    got = {k: ref.get(k) for k in want}
    assert got == want, f"scaleTargetRef is {got}, and it should be {want}"
    assert hspec.get("minReplicas") == b["min"], (
        f"minReplicas is {hspec.get('minReplicas')!r}, and it should be {b['min']}"
    )
    assert hspec.get("maxReplicas") == b["max"], (
        f"maxReplicas is {hspec.get('maxReplicas')!r}, and it should be {b['max']}"
    )
    metrics = hspec.get("metrics") or []
    assert len(metrics) == 1, f"the HPA has {len(metrics)} metrics, and the task asks for one"
    metric = metrics[0]
    resource = metric.get("resource") or {}
    assert metric.get("type") == "Resource" and resource.get("name") == "cpu", (
        f"the metric is type {metric.get('type')!r} on {resource.get('name')!r}, and it "
        "should be type 'Resource' on 'cpu'"
    )
    target = resource.get("target") or {}
    assert target.get("type") == "Utilization", (
        f"the target type is {target.get('type')!r}, and it should be 'Utilization'"
    )
    assert target.get("averageUtilization") == b["target"], (
        f"averageUtilization is {target.get('averageUtilization')!r}, and it should be "
        f"{b['target']}"
    )
