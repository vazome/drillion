"""What one sitting of 309 asks for, and what counts as having answered it.

The schema has already run by the time `check` does, so the shape is sound and only the
requirements are left. Every message here is what the learner reads, so each one names the
field and what it should have held."""

NAMES = ["db-migrate", "nightly-export", "resize-images", "reindex"]
IMAGES = ["ghcr.io/acme/tools:3.2", "python:3.13-slim", "ghcr.io/acme/export:1.1"]


def brief(r):
    return {
        "name": r.choice(NAMES),
        "image": r.choice(IMAGES),
        "completions": r.randint(1, 5),
        "retries": r.choice([2, 3, 4, 6]),
        "ttl": r.choice([600, 3600, 86400]),
    }


def check(doc, b):
    assert doc.get("kind") == "Job", f"this is a {doc.get('kind')}, and the task asks for a Job"
    name = doc.get("metadata", {}).get("name")
    assert name == b["name"], f"metadata.name is {name!r}, and it should be {b['name']!r}"
    spec = doc.get("spec", {})
    for key, want in (
        ("completions", b["completions"]),
        ("backoffLimit", b["retries"]),
        ("ttlSecondsAfterFinished", b["ttl"]),
    ):
        assert spec.get(key) == want, f"spec.{key} is {spec.get(key)!r}, and it should be {want}"
    pod = spec.get("template", {}).get("spec", {})
    containers = pod.get("containers") or []
    assert len(containers) == 1, (
        f"the pod template has {len(containers)} containers, and the task asks for one"
    )
    c = containers[0]
    assert c.get("image") == b["image"], (
        f"the container image is {c.get('image')!r}, not {b['image']!r}"
    )
    assert c.get("command"), "the container has no command, so the Job runs nothing of yours"
    policy = pod.get("restartPolicy")
    assert policy in ("Never", "OnFailure"), (
        f"the pod's restartPolicy is {policy!r}, and a Job needs 'Never' or 'OnFailure': "
        "the default, Always, restarts a finished container and is refused"
    )
