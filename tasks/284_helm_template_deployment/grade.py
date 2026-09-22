"""What one sitting of 284 asks for, and what counts as having answered it.

The template is rendered twice, with a different release and different values each time,
and `check` runs on both. A template that hardcodes what it should read passes whichever
render happens to match, and fails the other one."""

RELEASES = ["checkout", "billing", "inventory", "search", "ledger"]
IMAGES = [("nginx", "1.27"), ("httpd", "2.4"), ("caddy", "2.8"), ("traefik/whoami", "1.10")]


def brief(r):
    first, second = r.sample(IMAGES, 2)
    one, two = r.sample(RELEASES, 2)
    return {
        "release": one,
        "replicas": r.randint(2, 5),
        "repository": first[0],
        "tag": first[1],
        "other_release": two,
        "other_replicas": r.randint(6, 9),
        "other_repository": second[0],
        "other_tag": second[1],
    }


def renders(b):
    return [
        {
            "release": b["release"],
            "values": {
                "replicaCount": b["replicas"],
                "image": {"repository": b["repository"], "tag": b["tag"]},
            },
        },
        {
            "release": b["other_release"],
            "values": {
                "replicaCount": b["other_replicas"],
                "image": {"repository": b["other_repository"], "tag": b["other_tag"]},
            },
        },
    ]


def check(docs, b, render):
    kinds = [d.get("kind") for d in docs]
    assert kinds == ["Deployment"], f"the template should render one Deployment, not {kinds}"
    release, values = render["release"], render["values"]
    doc = docs[0]
    name = doc["metadata"]["name"]
    assert name == release, (
        f"metadata.name rendered as {name!r}, and it should be the release name "
        f"{release!r}: that is .Release.Name"
    )
    spec = doc["spec"]
    assert spec["replicas"] == values["replicaCount"], (
        f"spec.replicas rendered as {spec['replicas']!r}, and these values set "
        f"replicaCount to {values['replicaCount']}"
    )
    selector = spec["selector"].get("matchLabels") or {}
    labels = spec["template"]["metadata"].get("labels") or {}
    assert selector.get("app") == release, (
        f"spec.selector.matchLabels.app rendered as {selector.get('app')!r}, and it "
        f"should be the release name {release!r}"
    )
    assert labels.get("app") == release, (
        f"the pod template's app label rendered as {labels.get('app')!r}, and it should "
        f"be the release name {release!r}, the same as the selector"
    )
    containers = spec["template"]["spec"]["containers"]
    assert len(containers) == 1, f"the pod runs {len(containers)} containers, not one"
    want = f"{values['image']['repository']}:{values['image']['tag']}"
    assert containers[0]["image"] == want, (
        f"the image rendered as {containers[0]['image']!r}, and these values make it "
        f"{want!r}"
    )
