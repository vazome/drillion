"""What one sitting of 272 asks for, and what counts as having answered it.

The schema has already run by the time `check` does, so the shape is sound and only the
requirements are left. Every message here is what the learner reads, so each one names the
field and what it should have held."""

NAMES = ["checkout", "billing", "inventory", "search", "ledger"]
PORTS = [80, 8080]
TARGETS = [8080, 3000, 5000]


def brief(r):
    return {
        "name": r.choice(NAMES),
        "port": r.choice(PORTS),
        "targetPort": r.choice(TARGETS),
    }


def check(doc, b):
    assert doc.get("kind") == "Service", (
        f"this is a {doc.get('kind')}, and the task asks for a Service"
    )
    name = doc.get("metadata", {}).get("name")
    assert name == b["name"], f"metadata.name is {name!r}, and it should be {b['name']!r}"

    spec = doc.get("spec", {})
    kind_type = spec.get("type")
    assert kind_type in (None, "ClusterIP"), (
        f"spec.type is {kind_type!r}, and the task asks for the default: leave the type "
        "off and a Service is a ClusterIP"
    )

    selector = spec.get("selector") or {}
    assert selector.get("app") == b["name"], (
        f"spec.selector is {selector}, and it should select the pods labelled "
        f"app: {b['name']}"
    )

    ports = spec.get("ports") or []
    assert len(ports) == 1, (
        f"spec.ports holds {len(ports)} entries, and the task asks for one"
    )
    port = ports[0].get("port")
    assert port == b["port"], (
        f"spec.ports[0].port is {port!r}, and it should be {b['port']}: that is the "
        "number clients call"
    )
    target = ports[0].get("targetPort")
    assert target == b["targetPort"], (
        f"spec.ports[0].targetPort is {target!r}, and it should be {b['targetPort']}: "
        "that is the number the container listens on"
    )
