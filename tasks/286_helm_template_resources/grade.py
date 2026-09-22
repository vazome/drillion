"""What one sitting of 286 asks for, and what counts as having answered it.

The first render sets a node selector and the second leaves it empty, so both halves of
`with` are exercised: the block appears when the value has something in it and is absent,
key and all, when it does not. The resources block differs between the two as well."""

RELEASES = ["orders", "payments", "catalog", "gateway"]
IMAGES = ["ghcr.io/acme/api:2.3.1", "ghcr.io/acme/api:2.4.0"]


def brief(r):
    one, two = r.sample(RELEASES, 2)
    return {
        "release": one,
        "image": r.choice(IMAGES),
        "cpu": r.choice(["100m", "250m", "500m"]),
        "memory": r.choice(["128Mi", "256Mi"]),
        "limit": r.choice(["512Mi", "1Gi"]),
        "zone": r.choice(["eu-west-1a", "eu-west-1b", "us-east-2c"]),
        "other_release": two,
        "other_memory": r.choice(["64Mi", "96Mi"]),
    }


def renders(b):
    return [
        {
            "release": b["release"],
            "values": {
                "image": b["image"],
                "resources": {
                    "requests": {"cpu": b["cpu"], "memory": b["memory"]},
                    "limits": {"memory": b["limit"]},
                },
                "nodeSelector": {
                    "topology.kubernetes.io/zone": b["zone"],
                    "kubernetes.io/arch": "arm64",
                },
            },
        },
        {
            "release": b["other_release"],
            "values": {
                "image": b["image"],
                "resources": {"requests": {"memory": b["other_memory"]}},
                "nodeSelector": {},
            },
        },
    ]


def check(docs, b, render):
    kinds = [d.get("kind") for d in docs]
    assert kinds == ["Deployment"], f"the template should render one Deployment, not {kinds}"
    release, values = render["release"], render["values"]
    doc = docs[0]
    assert doc["metadata"]["name"] == release, (
        f"metadata.name rendered as {doc['metadata']['name']!r}, and it should be the "
        f"release name {release!r}"
    )
    labels = doc["spec"]["template"]["metadata"].get("labels") or {}
    selector = doc["spec"]["selector"].get("matchLabels") or {}
    assert labels.get("app") == release and selector.get("app") == release, (
        "the selector and the pod template should both carry app set to the release name"
    )
    pod = doc["spec"]["template"]["spec"]
    container = pod["containers"][0]
    assert container["image"] == values["image"], (
        f"the image rendered as {container['image']!r}, not {values['image']!r}"
    )
    assert container.get("resources") == values["resources"], (
        f"the container's resources rendered as {container.get('resources')!r}, and "
        f"these values hold {values['resources']!r}: the block is copied whole"
    )
    if values["nodeSelector"]:
        assert pod.get("nodeSelector") == values["nodeSelector"], (
            f"the pod's nodeSelector rendered as {pod.get('nodeSelector')!r}, and these "
            f"values hold {values['nodeSelector']!r}"
        )
    else:
        assert "nodeSelector" not in pod, (
            "these values leave nodeSelector empty, and the pod still renders a "
            f"nodeSelector key ({pod['nodeSelector']!r}): with an empty value the whole "
            "block should be absent"
        )
