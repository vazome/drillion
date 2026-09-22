"""What one sitting of 311 asks for, and what counts as having answered it.

The schema has already run by the time `check_many` does, and the file holds two objects,
`---`-separated, so they arrive here as a list. Every message here is what the learner
reads, so each one names the field and what it should have held."""

PAIRS = [
    ("web", "api", 8080),
    ("api", "postgres", 5432),
    ("worker", "redis", 6379),
    ("gateway", "orders", 8000),
]


def brief(r):
    client, target, port = r.choice(PAIRS)
    return {"name": f"{target}-from-{client}", "client": client, "target": target, "port": port}


def _policy(doc, which, name):
    assert doc.get("kind") == "NetworkPolicy", (
        f"the {which} document is a {doc.get('kind')}, and the task asks for a NetworkPolicy"
    )
    got = doc.get("metadata", {}).get("name")
    assert got == name, f"the {which} policy is named {got!r}, and it should be {name!r}"
    spec = doc.get("spec", {})
    types = spec.get("policyTypes")
    assert types == ["Ingress"], (
        f"the {which} policy's policyTypes is {types!r}, and it should be ['Ingress']"
    )
    return spec


def check_many(docs, b):
    assert len(docs) == 2, (
        f"the file holds {len(docs)} documents, and the task asks for two: the default "
        "deny first, then the policy that opens one door"
    )
    deny = _policy(docs[0], "first", "default-deny")
    assert deny.get("podSelector") == {}, (
        f"default-deny's podSelector is {deny.get('podSelector')!r}, and it should be "
        "empty, {}, which selects every pod in the namespace"
    )
    assert not deny.get("ingress"), (
        "default-deny has ingress rules, and every rule it has lets something in"
    )

    allow = _policy(docs[1], "second", b["name"])
    selected = (allow.get("podSelector") or {}).get("matchLabels")
    assert selected == {"app": b["target"]}, (
        f"the second policy protects the pods matching {selected}, and it should protect "
        f"{{'app': {b['target']!r}}}"
    )
    rules = allow.get("ingress") or []
    assert len(rules) == 1, (
        f"the second policy has {len(rules)} ingress rules, and the task asks for one"
    )
    peers = rules[0].get("from") or []
    assert len(peers) == 1, (
        f"the rule's from has {len(peers)} entries, and the task asks for one: with none, "
        "the rule lets in every source"
    )
    peer = peers[0]
    assert set(peer) == {"podSelector"}, (
        f"the from entry holds {sorted(peer)}, and it should hold a podSelector alone"
    )
    client = (peer.get("podSelector") or {}).get("matchLabels")
    assert client == {"app": b["client"]}, (
        f"the rule lets in pods matching {client}, and it should let in "
        f"{{'app': {b['client']!r}}}"
    )
    ports = rules[0].get("ports") or []
    assert len(ports) == 1, (
        f"the rule has {len(ports)} ports, and the task asks for one: with none, every "
        "port is open to that source"
    )
    port = ports[0]
    assert port.get("protocol", "TCP") == "TCP" and port.get("port") == b["port"], (
        f"the rule opens {port.get('protocol', 'TCP')} {port.get('port')!r}, and it should "
        f"open TCP {b['port']}"
    )
