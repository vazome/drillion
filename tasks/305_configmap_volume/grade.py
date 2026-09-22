"""What one sitting of 305 asks for, and what counts as having answered it.

The schema has already run by the time `check_many` does, and the file holds two objects,
`---`-separated, so they arrive here as a list. Every message here is what the learner
reads, so each one names the field and what it should have held."""

CONFIGS = ["app-config", "worker-config", "proxy-config"]
PODS = ["worker", "proxy", "reporter"]
DIRS = ["/etc/app", "/config", "/etc/worker"]
IMAGES = ["ghcr.io/acme/worker:1.8", "ghcr.io/acme/proxy:0.9", "python:3.13-slim"]


def brief(r):
    return {
        "config": r.choice(CONFIGS),
        "pod": r.choice(PODS),
        "dir": r.choice(DIRS),
        "image": r.choice(IMAGES),
    }


def check_many(docs, b):
    assert len(docs) == 2, (
        f"the file holds {len(docs)} documents, and the task asks for two: the "
        "ConfigMap first, then the Pod that mounts it"
    )
    cm, pod = docs
    assert cm.get("kind") == "ConfigMap", (
        f"the first document is a {cm.get('kind')}, and the ConfigMap goes first"
    )
    name = cm.get("metadata", {}).get("name")
    assert name == b["config"], (
        f"the ConfigMap's metadata.name is {name!r}, and it should be {b['config']!r}"
    )
    data = cm.get("data") or {}
    assert data.get("app.conf"), (
        "the ConfigMap's data has no non-empty key 'app.conf', and that key is the "
        f"file name the Pod will see (it has {sorted(data)})"
    )

    assert pod.get("kind") == "Pod", (
        f"the second document is a {pod.get('kind')}, and the task asks for a Pod"
    )
    name = pod.get("metadata", {}).get("name")
    assert name == b["pod"], f"the Pod's metadata.name is {name!r}, and it should be {b['pod']!r}"
    spec = pod.get("spec", {})
    containers = spec.get("containers") or []
    assert len(containers) == 1, (
        f"the pod has {len(containers)} containers, and the task asks for one"
    )
    c = containers[0]
    assert c.get("image") == b["image"], (
        f"the container image is {c.get('image')!r}, not {b['image']!r}"
    )
    volumes = {
        v.get("name")
        for v in spec.get("volumes") or []
        if (v.get("configMap") or {}).get("name") == b["config"]
    }
    assert volumes, f"no volume of the Pod has configMap.name {b['config']!r}"
    mounts = [m for m in c.get("volumeMounts") or [] if m.get("name") in volumes]
    assert mounts, "the container does not mount the ConfigMap volume"
    at = [m.get("mountPath") for m in mounts]
    assert b["dir"] in at, (
        f"the ConfigMap volume is mounted at {at}, and it should be at {b['dir']!r}: "
        "the directory, not the file"
    )
    mount = next(m for m in mounts if m.get("mountPath") == b["dir"])
    assert "subPath" not in mount, (
        f"the mount uses subPath {mount['subPath']!r}, and a subPath mount is copied once "
        "and never sees the ConfigMap change"
    )
