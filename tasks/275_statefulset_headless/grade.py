"""What one sitting of 275 asks for, and what counts as having answered it.

The schema has already run by the time `check_many` does, and the file holds two objects,
`---`-separated, so they arrive here as a list. Every message here is what the learner
reads, so each one names the field and what it should have held."""

SETS = [
    ("ledger", "postgres:17", 5432),
    ("queue", "rabbitmq:3", 5672),
    ("sessions", "redis:7.4", 6379),
]


def brief(r):
    name, image, port = r.choice(SETS)
    return {"name": name, "image": image, "port": port, "replicas": r.randint(2, 4)}


def check_many(docs, b):
    [d0, d1] = docs
    assert d0.get("kind") == "Service", (
        f"the first document is a {d0.get('kind')}, and the headless Service goes first "
        "so it exists by the time the StatefulSet is applied"
    )
    spec0 = d0.get("spec", {})
    # Headless is the string `None`; a quoted or unquoted spelling is that string either
    # way, so a ClusterIP number or an omitted field is what fails here
    assert spec0.get("clusterIP") == "None", (
        f"spec.clusterIP is {spec0.get('clusterIP')!r}, and a StatefulSet's peers find "
        "each other by name: only a headless Service, clusterIP: None, gives every pod "
        "a DNS record of its own"
    )
    assert (spec0.get("selector") or {}).get("app") == b["name"], (
        f"the Service's spec.selector is {spec0.get('selector')}, and it should select "
        f"the pods labelled app: {b['name']}"
    )
    ports0 = spec0.get("ports") or []
    assert ports0 and ports0[0].get("port") == b["port"], (
        f"the Service's port is {ports0[0].get('port') if ports0 else None!r}, and it "
        f"should be {b['port']}"
    )

    assert d1.get("kind") == "StatefulSet", (
        f"the second document is a {d1.get('kind')}, and the task asks for a StatefulSet"
    )
    spec1 = d1.get("spec", {})
    assert spec1.get("serviceName") == b["name"], (
        f"spec.serviceName is {spec1.get('serviceName')!r}, and it must name the "
        f"headless Service {b['name']!r} from the first document: that is the whole "
        "pair, and how every pod gets its DNS name"
    )
    replicas = spec1.get("replicas")
    assert replicas == b["replicas"], (
        f"spec.replicas is {replicas!r}, and it should be {b['replicas']}"
    )
    selector = spec1.get("selector", {}).get("matchLabels") or {}
    labels = spec1.get("template", {}).get("metadata", {}).get("labels") or {}
    assert selector and labels and all(labels.get(k) == v for k, v in selector.items()), (
        f"spec.selector.matchLabels is {selector} but the pod template is labelled "
        f"{labels}, and the StatefulSet only counts the pods its selector matches"
    )
    containers = spec1.get("template", {}).get("spec", {}).get("containers") or []
    assert len(containers) == 1, (
        f"the pod template has {len(containers)} containers, and the task asks for one"
    )
    image = containers[0].get("image")
    assert image == b["image"], f"the container image is {image!r}, not {b['image']!r}"
