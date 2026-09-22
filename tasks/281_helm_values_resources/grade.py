"""What one sitting of 281 asks for, and what counts as having answered it.

The chart copies `resources` into the container whole, so the render holds exactly what
the values said. Quantities are compared as the strings the brief gave: `0.25` and `250m`
are the same CPU to Kubernetes, but the task asks for the spelling people read."""

RELEASES = ["orders", "payments", "catalog", "gateway"]
IMAGES = ["ghcr.io/acme/api:2.3.1", "ghcr.io/acme/api:2.4.0", "registry.local/api:1.9"]


def brief(r):
    return {
        "release": r.choice(RELEASES),
        "image": r.choice(IMAGES),
        "cpu": r.choice(["100m", "250m", "500m"]),
        "memory": r.choice(["128Mi", "256Mi", "512Mi"]),
        "limit_memory": r.choice(["768Mi", "1Gi", "2Gi"]),
    }


def check(docs, b, render):
    kinds = [d.get("kind") for d in docs]
    assert kinds == ["Deployment"], f"the chart should render one Deployment, not {kinds}"
    container = docs[0]["spec"]["template"]["spec"]["containers"][0]
    assert container.get("image") == b["image"], (
        f"the image rendered as {container.get('image')!r}, not {b['image']!r}"
    )
    resources = container.get("resources")
    assert resources, (
        "the container rendered with no resources: the template only writes them when "
        ".Values.resources is set"
    )
    want = {
        "requests": {"cpu": b["cpu"], "memory": b["memory"]},
        "limits": {"memory": b["limit_memory"]},
    }
    for part, fields in want.items():
        got = resources.get(part) or {}
        for field, value in fields.items():
            assert got.get(field) == value, (
                f"resources.{part}.{field} rendered as {got.get(field)!r}, and it should "
                f"be {value!r}"
            )
    extra = set(resources.get("limits") or {}) - {"memory"}
    assert not extra, (
        f"resources.limits also sets {sorted(extra)}, and the task asks for a memory "
        "limit only: a CPU limit throttles the pod even when the node is idle"
    )
