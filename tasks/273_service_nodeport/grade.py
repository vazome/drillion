"""What one sitting of 273 asks for, and what counts as having answered it.

The schema has already run by the time `check` does, so the shape is sound and only the
requirements are left. The nodePort range is a live-API rule the schema does not model,
which is why `check` is the one enforcing it. Every message here is what the learner reads,
so each one names the field and what it should have held."""

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
    assert spec.get("type") == "NodePort", (
        f"spec.type is {spec.get('type')!r}, and the task asks for a NodePort"
    )

    selector = spec.get("selector") or {}
    assert selector.get("app") == b["name"], (
        f"spec.selector is {selector}, and it should select the pods labelled "
        f"app: {b['name']}"
    )

    ports = spec.get("ports") or []
    assert len(ports) == 1, f"spec.ports holds {len(ports)} entries, and the task asks for one"
    entry = ports[0]
    assert entry.get("port") == b["port"], (
        f"spec.ports[0].port is {entry.get('port')!r}, and it should be {b['port']}: "
        "the number cluster clients call"
    )
    assert entry.get("targetPort") == b["targetPort"], (
        f"spec.ports[0].targetPort is {entry.get('targetPort')!r}, and it should be "
        f"{b['targetPort']}: the number the container listens on"
    )
    node_port = entry.get("nodePort")
    assert node_port is not None, (
        "spec.ports[0].nodePort is missing, and the task asks you to name the hole: "
        "pick any free port in the legal range"
    )
    assert 30000 <= node_port <= 32767, (
        f"spec.ports[0].nodePort is {node_port}, and the legal range is 30000 to 32767: "
        "the API server refuses a Service outside it"
    )
