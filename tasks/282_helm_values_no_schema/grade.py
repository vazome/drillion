"""What one sitting of 282 asks for, and what counts as having answered it.

This chart has no schema and a default under every value, so a misspelt key is not an
error anywhere: the default renders instead. Every message here names the key the template
reads, because a silent default is the thing this task is about."""

RELEASES = ["mailer", "thumbnails", "exports", "webhooks"]
TAGS = ["1.5.2", "1.6.0", "2.0.1"]


def brief(r):
    return {
        "release": r.choice(RELEASES),
        "replicas": r.randint(2, 8),
        "tag": r.choice(TAGS),
        "log_level": r.choice(["debug", "info", "warn"]),
        "retries": str(r.randint(2, 9)),
        "dry_run": r.choice(["true", "false"]),
    }


def check(docs, b, render):
    kinds = [d.get("kind") for d in docs]
    assert kinds == ["Deployment"], f"the chart should render one Deployment, not {kinds}"
    spec = docs[0]["spec"]
    assert spec["replicas"] == b["replicas"], (
        f"spec.replicas rendered as {spec['replicas']!r}, and it should be "
        f"{b['replicas']}. A value the template never read leaves its default in place: "
        "the key it reads is replicaCount"
    )
    container = spec["template"]["spec"]["containers"][0]
    want = f"ghcr.io/acme/worker:{b['tag']}"
    assert container["image"] == want, (
        f"the image rendered as {container['image']!r}, and it should be {want!r}: the "
        "template reads the tag from .Values.image.tag, and falls back to 1.4.0"
    )
    env = {e.get("name"): e.get("value") for e in container.get("env") or []}
    for name, value in (
        ("LOG_LEVEL", b["log_level"]),
        ("RETRIES", b["retries"]),
        ("DRY_RUN", b["dry_run"]),
    ):
        assert env.get(name) == value, (
            f"the environment variable {name} rendered as {env.get(name)!r}, and it "
            f"should be {value!r}"
        )
    assert len(env) == 3, f"the container sets {sorted(env)}, and the task asks for three"
