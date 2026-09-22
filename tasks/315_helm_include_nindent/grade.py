"""What one sitting of 315 asks for, and what counts as having answered it.

The chart's `_helpers.tpl` defines the names and labels; the learner's Deployment calls
them. Two renders, with different releases and values, so a name, a label or a number
typed in by hand fails the render it does not match."""

RELEASES = ["checkout", "billing", "inventory", "search", "ledger"]
TAGS = ["2.3.1", "2.4.0", "3.0.2"]
CHART = "api-2.1.0"


def brief(r):
    one, two = r.sample(RELEASES, 2)
    first, second = r.sample(TAGS, 2)
    return {
        "release": one,
        "replicas": r.randint(2, 4),
        "tag": first,
        "port": r.choice([8080, 8000]),
        "other_release": two,
        "other_replicas": r.randint(5, 8),
        "other_tag": second,
        "other_port": r.choice([3000, 9090]),
    }


def renders(b):
    return [
        {
            "release": b[f"{p}release"],
            "values": {
                "replicaCount": b[f"{p}replicas"],
                "image": {"tag": b[f"{p}tag"]},
                "port": b[f"{p}port"],
            },
        }
        for p in ("", "other_")
    ]


def check(docs, b, render):
    kinds = [d.get("kind") for d in docs]
    assert kinds == ["Deployment"], (
        f"the template should render one Deployment, not {kinds}"
    )
    release, values = render["release"], render["values"]
    doc = docs[0]
    selector = {"app.kubernetes.io/name": "api", "app.kubernetes.io/instance": release}
    labels = {
        **selector,
        "helm.sh/chart": CHART,
        "app.kubernetes.io/managed-by": "Helm",
    }

    name = doc["metadata"]["name"]
    assert name == f"{release}-api", (
        f"metadata.name rendered as {name!r}, and api.fullname makes it {release + '-api'!r}"
    )
    got = doc["metadata"].get("labels") or {}
    assert got == labels, (
        f"metadata.labels rendered as {got}, and api.labels gives exactly {labels}"
    )
    spec = doc["spec"]
    got = spec["selector"].get("matchLabels") or {}
    assert got == selector, (
        f"spec.selector.matchLabels rendered as {got}, and api.selectorLabels gives "
        f"exactly {selector}"
    )
    got = spec["template"]["metadata"].get("labels") or {}
    assert got == selector, (
        f"the pod template's labels rendered as {got}, and api.selectorLabels gives "
        f"exactly {selector}"
    )
    assert spec["replicas"] == values["replicaCount"], (
        f"spec.replicas rendered as {spec['replicas']!r}, and these values set "
        f"replicaCount to {values['replicaCount']}"
    )
    containers = spec["template"]["spec"]["containers"]
    assert len(containers) == 1, f"the pod runs {len(containers)} containers, not one"
    want = f"{values['image']['repository']}:{values['image']['tag']}"
    assert containers[0]["image"] == want, (
        f"the image rendered as {containers[0]['image']!r}, and these values make it {want!r}"
    )
    ports = [p.get("containerPort") for p in containers[0].get("ports") or []]
    assert ports == [values["port"]], (
        f"the container's ports rendered as {ports}, and these values set port to "
        f"{values['port']}"
    )
