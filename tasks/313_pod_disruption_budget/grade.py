"""What one sitting of 313 asks for, and what counts as having answered it.

The schema has already run by the time `check` does, so the shape is sound and only the
requirements are left. Every message here is what the learner reads, so each one names the
field and what it should have held."""

APPS = ["api", "checkout", "search", "gateway"]


def brief(r):
    app = r.choice(APPS)
    return {"name": f"{app}-pdb", "app": app, "minimum": r.randint(1, 4)}


def check(doc, b):
    assert doc.get("kind") == "PodDisruptionBudget", (
        f"this is a {doc.get('kind')}, and the task asks for a PodDisruptionBudget"
    )
    name = doc.get("metadata", {}).get("name")
    assert name == b["name"], f"metadata.name is {name!r}, and it should be {b['name']!r}"
    spec = doc.get("spec", {})
    selector = (spec.get("selector") or {}).get("matchLabels")
    assert selector == {"app": b["app"]}, (
        f"spec.selector.matchLabels is {selector}, and it should be {{'app': {b['app']!r}}}"
    )
    assert spec.get("minAvailable") == b["minimum"], (
        f"spec.minAvailable is {spec.get('minAvailable')!r}, and it should be the number "
        f"{b['minimum']}"
    )
    assert "maxUnavailable" not in spec, (
        "the budget sets maxUnavailable beside minAvailable, and the API refuses a "
        "budget that sets both"
    )
