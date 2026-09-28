"""What one sitting of 367 asks for, and what counts as having answered it.

The Rollouts schema types a weight as an integer with no range, and lets a step carry any
mix of keys. Argo Rollouts' own validator refuses both, so both are refused here, before
the steps are compared with the brief's."""

APPS = ["checkout", "search", "pricing", "gateway"]
TAGS = ["4.2.0", "2.9.1", "7.0.3"]


def brief(r):
    name = r.choice(APPS)
    return {
        "name": name,
        "image": f"ghcr.io/acme/{name}:{r.choice(TAGS)}",
        "replicas": 10,
        "first": r.choice([10, 20]),
        "pause": r.choice(["5m", "10m", "15m"]),
        "second": r.choice([40, 50, 60]),
    }


def _steps(steps):
    """Each step as (what it does, its value), after Argo Rollouts' own rules."""
    out = []
    for i, step in enumerate(steps, 1):
        assert isinstance(step, dict) and len(step) == 1, (
            f"step {i} is {step!r}, and a step does exactly one thing: one key, such as "
            "setWeight or pause"
        )
        (what, value), = step.items()
        if what == "setWeight":
            assert isinstance(value, int) and 0 <= value <= 100, (
                f"step {i} sets the weight to {value!r}, and a weight is a percentage "
                "from 0 to 100"
            )
        out.append((what, value))
    return out


def check(doc, b):
    assert doc.get("kind") == "Rollout", (
        f"kind is {doc.get('kind')!r}, and it should be 'Rollout'"
    )
    meta = doc.get("metadata") or {}
    assert meta.get("name") == b["name"], (
        f"metadata.name is {meta.get('name')!r}, and it should be {b['name']!r}"
    )
    spec = doc.get("spec") or {}
    assert spec.get("replicas") == b["replicas"], (
        f"spec.replicas is {spec.get('replicas')!r}, and it should be {b['replicas']}"
    )
    selector = (spec.get("selector") or {}).get("matchLabels")
    assert selector == {"app": b["name"]}, (
        f"spec.selector.matchLabels is {selector}, and it should be {{'app': {b['name']!r}}}"
    )
    labels = ((spec.get("template") or {}).get("metadata") or {}).get("labels") or {}
    assert all(labels.get(k) == v for k, v in selector.items()), (
        f"the selector is {selector} and the pod template is labelled {labels}: the "
        "controller refuses a Rollout whose selector does not match its template"
    )
    containers = ((spec.get("template") or {}).get("spec") or {}).get("containers") or []
    assert len(containers) == 1, (
        f"the pod template has {len(containers)} containers, and it should have one"
    )
    c = containers[0]
    assert c.get("name") == b["name"] and c.get("image") == b["image"], (
        f"the container is {c.get('name')!r} running {c.get('image')!r}, and it should be "
        f"{b['name']!r} running {b['image']!r}"
    )

    canary = (spec.get("strategy") or {}).get("canary")
    assert isinstance(canary, dict), (
        "spec.strategy has no canary, so the Rollout replaces every pod at once"
    )
    steps = _steps(canary.get("steps") or [])
    want = [
        ("setWeight", b["first"]),
        ("pause", {"duration": b["pause"]}),
        ("setWeight", b["second"]),
        ("pause", {}),
    ]
    assert steps == want, (
        f"the steps are {[dict([s]) for s in steps]}, and they should be "
        f"{[dict([s]) for s in want]}"
    )
