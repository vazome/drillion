"""What one sitting of 268 asks for, and what counts as having answered it.

The schema has already run by the time `check` does, so the shape is sound and only the
requirements are left. Every message here is what the learner reads, so each one names the
field and what it should have held."""

SERVICES = ["checkout", "billing", "inventory", "search", "ledger"]
IMAGES = ["nginx:1.27", "redis:7.4", "httpd:2.4", "postgres:17"]


def brief(r):
    return {
        "name": r.choice(SERVICES),
        "replicas": r.randint(2, 6),
        "image": r.choice(IMAGES),
    }


def check(doc, b):
    assert doc.get("kind") == "Deployment", (
        f"this is a {doc.get('kind')}, and the task asks for a Deployment"
    )
    name = doc.get("metadata", {}).get("name")
    assert name == b["name"], f"metadata.name is {name!r}, and it should be {b['name']!r}"

    spec = doc.get("spec", {})
    replicas = spec.get("replicas")
    assert replicas == b["replicas"], (
        f"spec.replicas is {replicas!r}, and it should be {b['replicas']}"
    )

    # the pair the API server refuses a mismatch on, which is the point of the task
    selector = spec.get("selector", {}).get("matchLabels") or {}
    labels = spec.get("template", {}).get("metadata", {}).get("labels") or {}
    assert selector, "spec.selector.matchLabels is empty, so this Deployment finds no pods"
    assert labels, "the pod template has no labels for spec.selector.matchLabels to find"
    assert all(labels.get(k) == v for k, v in selector.items()), (
        f"spec.selector.matchLabels is {selector} but the pod template is labelled "
        f"{labels}, and a Deployment only counts the pods its selector matches"
    )

    containers = spec.get("template", {}).get("spec", {}).get("containers") or []
    assert len(containers) == 1, (
        f"the pod template has {len(containers)} containers, and the task asks for one"
    )
    image = containers[0].get("image")
    assert image == b["image"], f"the container image is {image!r}, not {b['image']!r}"
