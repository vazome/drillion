"""What one sitting of 287 asks for, and what counts as having answered it.

Three renders: a type given, no type given, and the Service switched off. The third one
renders the Deployment alone, and that is the correct answer for it, so `check` asserts
the count of Services first, in every render."""

RELEASES = ["checkout", "billing", "inventory", "search", "ledger"]


def brief(r):
    one, two, three = r.sample(RELEASES, 3)
    return {
        "release": one,
        "port": r.choice([80, 8080, 8000]),
        "other_release": two,
        "other_port": r.choice([3000, 9090]),
        "off_release": three,
    }


def renders(b):
    return [
        {"release": b["release"], "values": {"service": {"type": "NodePort", "port": b["port"]}}},
        {"release": b["other_release"], "values": {"service": {"port": b["other_port"]}}},
        {"release": b["off_release"], "values": {"service": {"enabled": False}}},
    ]


def check(docs, b, render):
    service = render["values"]["service"]
    services = [d for d in docs if d.get("kind") == "Service"]
    if not service["enabled"]:
        assert not services, (
            "service.enabled is false in these values, and a Service still rendered: the "
            "whole file should sit inside an if on .Values.service.enabled"
        )
        return
    assert len(services) == 1, (
        f"service.enabled is true in these values, and {len(services)} Services rendered"
    )
    doc = services[0]
    release = render["release"]
    assert doc["metadata"]["name"] == release, (
        f"metadata.name rendered as {doc['metadata']['name']!r}, and it should be the "
        f"release name {release!r}"
    )
    spec = doc["spec"]
    want = service.get("type") or "ClusterIP"
    assert spec.get("type") == want, (
        f"spec.type rendered as {spec.get('type')!r}, and with these values it should be "
        f"{want!r}: an empty type falls back to ClusterIP"
    )
    assert (spec.get("selector") or {}).get("app") == release, (
        f"spec.selector should select app: {release}, the label the Deployment's pods carry"
    )
    ports = spec.get("ports") or []
    assert len(ports) == 1, f"the Service rendered {len(ports)} ports, and it needs one"
    assert ports[0].get("port") == service["port"], (
        f"the port rendered as {ports[0].get('port')!r}, and these values set it to "
        f"{service['port']}"
    )
    assert ports[0].get("targetPort") == 80, (
        f"targetPort rendered as {ports[0].get('targetPort')!r}; the container listens on 80"
    )
