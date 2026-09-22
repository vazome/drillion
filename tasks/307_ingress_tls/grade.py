"""What one sitting of 307 asks for, and what counts as having answered it.

The schema has already run by the time `check` does, so the shape is sound and only the
requirements are left. Every message here is what the learner reads, so each one names the
field and what it should have held."""

SITES = [
    ("shop", "shop.example.com", "storefront"),
    ("api", "api.example.com", "orders-api"),
    ("status", "status.example.com", "status-page"),
]
CLASSES = ["nginx", "traefik"]


def brief(r):
    name, host, service = r.choice(SITES)
    return {
        "name": name,
        "host": host,
        "service": service,
        "secret": f"{name}-tls",
        "ingressClass": r.choice(CLASSES),
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
        f"spec.ingressClassName is {cls!r}, and it should be {b['ingressClass']!r}"
    )

    tls = spec.get("tls") or []
    assert len(tls) == 1, f"spec.tls has {len(tls)} entries, and the task asks for one"
    assert tls[0].get("secretName") == b["secret"], (
        f"the tls entry's secretName is {tls[0].get('secretName')!r}, and the "
        f"certificate is in {b['secret']!r}"
    )
    hosts = tls[0].get("hosts") or []
    assert hosts == [b["host"]], (
        f"the tls entry covers {hosts}, and it should cover exactly [{b['host']!r}]: "
        "a certificate for any other name is refused by the browser"
    )

    rules = spec.get("rules") or []
    assert len(rules) == 1, f"spec.rules has {len(rules)} rules, and the task asks for one"
    rule = rules[0]
    assert rule.get("host") == b["host"], (
        f"the rule's host is {rule.get('host')!r}, and it should be {b['host']!r}, the "
        "same name the tls entry covers"
    )
    paths = (rule.get("http") or {}).get("paths") or []
    assert len(paths) == 1, f"the rule has {len(paths)} paths, and the task asks for one"
    path = paths[0]
    assert path.get("path") == "/" and path.get("pathType") == "Prefix", (
        f"the path is {path.get('path')!r} with pathType {path.get('pathType')!r}, and "
        "it should be '/' with 'Prefix', so that every request for the host matches"
    )
    service = (path.get("backend") or {}).get("service") or {}
    assert service.get("name") == b["service"], (
        f"the backend Service is {service.get('name')!r}, and it should be {b['service']!r}"
    )
    number = (service.get("port") or {}).get("number")
    assert number == 80, f"the backend port.number is {number!r}, and it should be 80"
