"""What one sitting of 280 asks for, and what counts as having answered it.

The schema has already refused a misspelt key or a type outside the two the chart knows,
so what is left is whether the render exposes the port the brief asked for."""

RELEASES = ["checkout", "billing", "inventory", "search", "ledger"]
IMAGES = [("nginx", "1.27"), ("httpd", "2.4"), ("caddy", "2.8")]


def brief(r):
    repository, tag = r.choice(IMAGES)
    return {
        "release": r.choice(RELEASES),
        "replicas": r.randint(1, 4),
        "repository": repository,
        "tag": tag,
        "image": f"{repository}:{tag}",
        "port": r.choice([80, 8080, 8000]),
        "node_port": r.randint(30000, 32767),
    }


def _one(docs, kind):
    found = [d for d in docs if d.get("kind") == kind]
    assert len(found) == 1, f"the chart should render one {kind}, and it rendered {len(found)}"
    return found[0]


def check(docs, b, render):
    deployment = _one(docs, "Deployment")
    replicas = deployment["spec"]["replicas"]
    assert replicas == b["replicas"], (
        f"spec.replicas rendered as {replicas!r}, and it should be {b['replicas']}"
    )
    image = deployment["spec"]["template"]["spec"]["containers"][0]["image"]
    assert image == b["image"], f"the image rendered as {image!r}, not {b['image']!r}"

    service = _one(docs, "Service")["spec"]
    assert service.get("type") == "NodePort", (
        f"the Service rendered with type {service.get('type')!r}, and it should be "
        "NodePort: .Values.service.type decides it"
    )
    port = service["ports"][0]
    assert port.get("port") == b["port"], (
        f"the Service port rendered as {port.get('port')!r}, and it should be {b['port']}"
    )
    assert port.get("nodePort") == b["node_port"], (
        f"the nodePort rendered as {port.get('nodePort')!r}, and it should be "
        f"{b['node_port']}: the template only writes .Values.service.nodePort when the "
        "type is NodePort"
    )
