"""What one sitting of 306 asks for, and what counts as having answered it.

The schema has already run by the time `check` does, so the shape is sound and only the
requirements are left. Every message here is what the learner reads, so each one names the
field and what it should have held."""

SITES = [
    ("shop", "shop.example.com", "storefront"),
    ("api", "api.example.com", "orders-api"),
    ("docs", "docs.example.com", "handbook"),
]
PATHS = ["/", "/v2", "/shop"]
CLASSES = ["nginx", "traefik"]
PORTS = [80, 8080]


def brief(r):
    name, host, service = r.choice(SITES)
    return {
        "name": name,
        "host": host,
        "service": service,
        "path": r.choice(PATHS),
        "ingressClass": r.choice(CLASSES),
        "port": r.choice(PORTS),
    }


def check(doc, b):
    assert doc.get("kind") == "Ingress", (
        f"this is a {doc.get('kind')}, and the task asks for an Ingress"
    )
    name = doc.get("metadata", {}).get("name")
    assert name == b["name"], f"metadata.name is {name!r}, and it should be {b['name']!r}"
    spec = doc.get("spec", {})
    cls = spec.get("ingressClassName")
    assert cls == b["ingressClass"], (
        f"spec.ingressClassName is {cls!r}, and it should be {b['ingressClass']!r}: "
        "without it, which controller serves this Ingress is up to the cluster"
    )
    rules = spec.get("rules") or []
    assert len(rules) == 1, f"spec.rules has {len(rules)} rules, and the task asks for one"
    rule = rules[0]
    assert rule.get("host") == b["host"], (
        f"the rule's host is {rule.get('host')!r}, and it should be {b['host']!r}"
    )
    paths = (rule.get("http") or {}).get("paths") or []
    assert len(paths) == 1, f"the rule has {len(paths)} paths, and the task asks for one"
    path = paths[0]
    assert path.get("path") == b["path"], (
        f"the path is {path.get('path')!r}, and it should be {b['path']!r}"
    )
    assert path.get("pathType") == "Prefix", (
        f"pathType is {path.get('pathType')!r}, and it should be 'Prefix' so that "
        "everything under the path matches too"
    )
    service = (path.get("backend") or {}).get("service") or {}
    assert service.get("name") == b["service"], (
        f"the backend Service is {service.get('name')!r}, and it should be {b['service']!r}"
    )
    number = (service.get("port") or {}).get("number")
    assert number == b["port"], (
        f"the backend port.number is {number!r}, and it should be {b['port']}"
    )
