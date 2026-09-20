"""What one sitting of 269 asks for, and what counts as having answered it.

The schema has already run by the time `check` does, so the shape is sound and only the
requirements are left. Every message here is what the learner reads, so each one names the
field and what it should have held."""

PAIRS = [
    ("web", "nginx:1.27", 80),
    ("cache", "redis:7.4", 6379),
    ("docs", "httpd:2.4", 80),
    ("db", "postgres:17", 5432),
]


def brief(r):
    name, image, port = r.choice(PAIRS)
    return {"name": name, "image": image, "port": port}


def check(doc, b):
    assert doc.get("kind") == "Pod", (
        f"this is a {doc.get('kind')}, and the task asks for a bare Pod"
    )
    name = doc.get("metadata", {}).get("name")
    assert name == b["name"], f"metadata.name is {name!r}, and it should be {b['name']!r}"

    containers = doc.get("spec", {}).get("containers") or []
    assert len(containers) == 1, (
        f"spec.containers holds {len(containers)} containers, and the task asks for one"
    )
    container = containers[0]
    image = container.get("image")
    assert image == b["image"], f"the container image is {image!r}, not {b['image']!r}"

    ports = container.get("ports") or []
    assert ports, (
        "the container declares no ports, and the task asks it to name the one it listens on"
    )
    port = ports[0].get("containerPort")
    assert port == b["port"], (
        f"containerPort is {port!r}, and it should be {b['port']}: a port is a number, "
        "so it carries no quotes"
    )
