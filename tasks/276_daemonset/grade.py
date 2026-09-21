"""What one sitting of 276 asks for, and what counts as having answered it.

The schema has already run by the time `check` does, so the shape is sound and only the
requirements are left. Every message here is what the learner reads, so each one names the
field and what it should have held."""

AGENTS = [
    ("node-log", "fluent/fluentd:v1.17"),
    ("node-metrics", "prometheus/node-exporter:v1.9"),
    ("node-forward", "fluent/fluent-bit:3.2"),
]


def brief(r):
    name, image = r.choice(AGENTS)
    return {"name": name, "image": image}


def check(doc, b):
    assert doc.get("kind") == "DaemonSet", (
        f"this is a {doc.get('kind')}, and the task asks for a DaemonSet"
    )
    name = doc.get("metadata", {}).get("name")
    assert name == b["name"], f"metadata.name is {name!r}, and it should be {b['name']!r}"

    spec = doc.get("spec", {})
    assert "replicas" not in spec, (
        "spec.replicas is not a field of a DaemonSet: it puts one pod on every node, "
        "and sizing it by hand would fight the nodes joining and leaving"
    )

    selector = spec.get("selector", {}).get("matchLabels") or {}
    labels = spec.get("template", {}).get("metadata", {}).get("labels") or {}
    assert selector and labels and all(labels.get(k) == v for k, v in selector.items()), (
        f"spec.selector.matchLabels is {selector} but the pod template is labelled "
        f"{labels}, and a DaemonSet only counts the pods its selector matches"
    )
    assert labels.get("app") == b["name"], (
        f"the pod template is labelled app: {labels.get('app')!r}, and it should be "
        f"app: {b['name']!r}"
    )

    containers = spec.get("template", {}).get("spec", {}).get("containers") or []
    assert len(containers) == 1, (
        f"the pod template has {len(containers)} containers, and the task asks for one"
    )
    cname = containers[0].get("name")
    assert cname == b["name"], (
        f"the container is named {cname!r}, and it should be {b['name']!r}"
    )
    image = containers[0].get("image")
    assert image == b["image"], f"the container image is {image!r}, not {b['image']!r}"
