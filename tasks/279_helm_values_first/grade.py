"""What one sitting of 279 asks for, and what counts as having answered it.

Helm, its lint and the schema have all run by the time `check` does, so the values parsed
and the chart rendered. What is left is whether the render is the one the brief asked for,
and every message says which value the template reads, since that is the thing to change."""

RELEASES = ["checkout", "billing", "inventory", "search", "ledger"]
IMAGES = [("nginx", "1.27"), ("httpd", "2.4"), ("caddy", "2.8")]


def brief(r):
    repository, tag = r.choice(IMAGES)
    return {
        "release": r.choice(RELEASES),
        "replicas": r.randint(2, 6),
        "repository": repository,
        "tag": tag,
        "image": f"{repository}:{tag}",
        "port": r.choice([8080, 8000, 9090, 3000]),
    }


def _one(docs, kind):
    found = [d for d in docs if d.get("kind") == kind]
    assert len(found) == 1, f"the chart should render one {kind}, and it rendered {len(found)}"
    return found[0]


def check(docs, b, render):
    deployment = _one(docs, "Deployment")
    replicas = deployment["spec"]["replicas"]
    assert replicas == b["replicas"], (
        f"spec.replicas rendered as {replicas!r}, and it should be {b['replicas']}: "
        "the template reads it from .Values.replicaCount"
    )
    image = deployment["spec"]["template"]["spec"]["containers"][0]["image"]
    assert image == b["image"], (
        f"the image rendered as {image!r}, and it should be {b['image']!r}: the template "
        "joins .Values.image.repository and .Values.image.tag with a colon"
    )
    port = _one(docs, "Service")["spec"]["ports"][0]["port"]
    assert port == b["port"], (
        f"the Service port rendered as {port!r}, and it should be {b['port']}: "
        "the template reads it from .Values.service.port"
    )
