"""What 369 asks for, and what counts as having answered it.

The evidence names fixed objects, so the brief is empty. The answer is the manifest from git
with one field fixed; the likely wrong fixes get their own message first, and anything else
that moved is named by the first path where it differs."""

IMAGE = "ghcr.io/acme/catalog:2.8.0"
CONTAINER = {
    "name": "catalog",
    "image": IMAGE,
    "ports": [{"containerPort": 8080}],
    "readinessProbe": {
        "httpGet": {"path": "/readyz", "port": 8080},
        "periodSeconds": 10,
    },
    "livenessProbe": {"tcpSocket": {"port": 8080}, "periodSeconds": 20},
}
WANT = {
    "apiVersion": "apps/v1",
    "kind": "Deployment",
    "metadata": {"name": "catalog"},
    "spec": {
        "replicas": 3,
        "selector": {"matchLabels": {"app": "catalog"}},
        "template": {
            "metadata": {"labels": {"app": "catalog"}},
            "spec": {"containers": [CONTAINER]},
        },
    },
}


def brief(r):
    return {}


def difference(got, want, path=""):
    """The first place `got` leaves `want`, in words, or None when they match."""
    here = path or "the document"
    if isinstance(want, dict):
        if not isinstance(got, dict):
            return f"{here} is {got!r}, and in git it is a mapping"
        for key in want:
            if key not in got:
                return f"{path}.{key} is missing, and git has it".lstrip(".")
        for key in got:
            if key not in want:
                return f"{path}.{key} is not in git's manifest; leave it out".lstrip(".")
        for key in want:
            found = difference(got[key], want[key], f"{path}.{key}")
            if found:
                return found
        return None
    if isinstance(want, list):
        if not isinstance(got, list) or len(got) != len(want):
            return f"{here} is {got!r}, and it should be {want!r}".lstrip(".")
        for i, (g, w) in enumerate(zip(got, want)):
            found = difference(g, w, f"{path}[{i}]")
            if found:
                return found
        return None
    if got != want:
        return f"{here} is {got!r}, and it should be {want!r}".lstrip(".")
    return None


def check(doc, b):
    assert doc.get("kind") == "Deployment", (
        f"kind is {doc.get('kind')!r}, and the fix is to the Deployment"
    )
    containers = (
        ((doc.get("spec") or {}).get("template") or {}).get("spec") or {}
    ).get("containers") or [{}]
    c = containers[0] if isinstance(containers[0], dict) else {}
    assert c.get("image") == IMAGE, (
        f"the image is {c.get('image')!r}: going back to the old release hides the "
        f"problem until the next one. Keep {IMAGE!r} and fix what it is asked"
    )
    path = ((c.get("readinessProbe") or {}).get("httpGet") or {}).get("path")
    assert path != "/health", (
        "the readiness probe still asks /health, the page the log says 2.8.0 removed: "
        "that is the 404 in the events"
    )
    assert path == "/readyz", (
        f"the readiness probe asks {path!r}, and 2.8.0 serves readiness at /readyz"
    )
    found = difference(doc, WANT)
    assert found is None, found
