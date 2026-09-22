"""What one sitting of 316 asks for, and what counts as having answered it.

Four renders. Two with good values, which must render and are checked like any
Deployment. Two the chart must refuse: one with no database URL, one with the image tag
`latest`. A refused render passes only when Helm stops and its message says the words the
rules give, which is what the person running `helm install` would read."""

RELEASES = ["checkout", "billing", "inventory", "search", "ledger"]
TAGS = ["1.8.0", "1.9.2", "2.0.0"]
HOSTS = ["orders-db", "pg-primary", "db.internal"]
NO_URL = "database.url is required"
LATEST = "image.tag must be a pinned version, not latest"


def brief(r):
    one, two = r.sample(RELEASES, 2)
    first, second = r.sample(TAGS, 2)
    a, c = r.sample(HOSTS, 2)
    return {
        "release": one,
        "tag": first,
        "url": f"postgres://{a}:5432/orders",
        "other_release": two,
        "other_tag": second,
        "other_url": f"postgres://{c}:5432/orders",
    }


def renders(b):
    good = [
        {
            "release": b[f"{p}release"],
            "values": {
                "image": {"tag": b[f"{p}tag"]},
                "database": {"url": b[f"{p}url"]},
            },
        }
        for p in ("", "other_")
    ]
    return good + [
        {
            "release": b["release"],
            "values": {"image": {"tag": b["tag"]}},
            "refuses": NO_URL,
        },
        {
            "release": b["release"],
            "values": {"image": {"tag": "latest"}, "database": {"url": b["url"]}},
            "refuses": LATEST,
        },
    ]


def check(docs, b, render):
    kinds = [d.get("kind") for d in docs]
    assert kinds == ["Deployment"], (
        f"the template should render one Deployment, not {kinds}"
    )
    release, values = render["release"], render["values"]
    doc = docs[0]
    assert doc["metadata"]["name"] == release, (
        f"metadata.name rendered as {doc['metadata']['name']!r}, and it should be the "
        f"release name {release!r}"
    )
    spec = doc["spec"]
    selector = spec["selector"].get("matchLabels") or {}
    labels = spec["template"]["metadata"].get("labels") or {}
    assert selector.get("app") == release and labels.get("app") == release, (
        f"the selector and the pod template should both carry app: {release}, and they "
        f"rendered as {selector} and {labels}"
    )
    containers = spec["template"]["spec"]["containers"]
    assert len(containers) == 1, f"the pod runs {len(containers)} containers, not one"
    c = containers[0]
    want = f"{values['image']['repository']}:{values['image']['tag']}"
    assert c["image"] == want, (
        f"the image rendered as {c['image']!r}, and it should be {want!r}"
    )
    env = {e.get("name"): e.get("value") for e in c.get("env") or []}
    assert env.get("DATABASE_URL") == values["database"]["url"], (
        f"DATABASE_URL rendered as {env.get('DATABASE_URL')!r}, and these values set "
        f"database.url to {values['database']['url']!r}"
    )
