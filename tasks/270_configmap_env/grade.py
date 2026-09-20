"""What one sitting of 270 asks for, and what counts as having answered it.

The schema has already run by the time `check_many` does, and the file holds two objects,
`---`-separated, so they arrive here as a list. Every message here is what the learner
reads, so each one names the field and what it should have held."""

CONFIGS = ["app-config", "service-config", "worker-config"]
PODS = ["worker", "collector", "reporter"]
VALUES = ["debug", "info", "warn", "error"]
IMAGES = ["nginx:1.27", "redis:7.4", "httpd:2.4", "postgres:17"]


def brief(r):
    return {
        "name": r.choice(CONFIGS),
        "pod": r.choice(PODS),
        "value": r.choice(VALUES),
        "image": r.choice(IMAGES),
    }


def check_many(docs, b):
    [d0, d1] = docs
    assert d0.get("kind") == "ConfigMap", (
        f"the first document is a {d0.get('kind')}, and the ConfigMap goes first so it "
        "exists by the time the Pod is applied"
    )
    data = d0.get("data") or {}
    assert data.get("LOG_LEVEL") == b["value"], (
        f"the ConfigMap's data.LOG_LEVEL is {data.get('LOG_LEVEL')!r}, and it should "
        f"hold {b['value']!r}"
    )

    assert d1.get("kind") == "Pod", (
        f"the second document is a {d1.get('kind')}, and the task asks for the Pod that "
        "reads the ConfigMap"
    )
    containers = d1.get("spec", {}).get("containers") or []
    assert len(containers) == 1, (
        f"the pod has {len(containers)} containers, and the task asks for one"
    )
    env = containers[0].get("env") or []
    entry = next((e for e in env if e.get("name") == "LOG_LEVEL"), None)
    assert entry is not None, (
        "no env entry named LOG_LEVEL, which is the variable the container expects to read"
    )
    assert "value" not in entry, (
        f"the LOG_LEVEL entry carries a literal value {entry.get('value')!r} beside its "
        "valueFrom, and the literal is what wins: the ConfigMap would be ignored"
    )
    ref = entry.get("valueFrom", {}).get("configMapKeyRef") or {}
    assert ref.get("name") == b["name"], (
        f"configMapKeyRef.name is {ref.get('name')!r}, and it should name the ConfigMap "
        f"{b['name']!r} from the first document"
    )
    assert ref.get("key") == "LOG_LEVEL", (
        f"configMapKeyRef.key is {ref.get('key')!r}, and the entry in the ConfigMap is "
        "named LOG_LEVEL"
    )
