"""What one sitting of 301 asks for, and what counts as having answered it.

The schema has already run by the time `check` does, so the shape is sound and only the
requirements are left. Every message here is what the learner reads, so each one names the
field and what it should have held."""

import re

NAMES = ["payments", "ledger", "postgres", "billing"]
IMAGES = ["postgres:17", "redis:7.4", "ghcr.io/acme/payments:4.2"]
CPUS = ["250m", "500m", "1", "2"]
MEMORIES = ["256Mi", "512Mi", "1Gi", "2Gi"]
_UNITS = {"": 1, "k": 10**3, "M": 10**6, "G": 10**9, "Ki": 2**10, "Mi": 2**20, "Gi": 2**30}


def brief(r):
    return {
        "name": r.choice(NAMES),
        "image": r.choice(IMAGES),
        "cpu": r.choice(CPUS),
        "memory": r.choice(MEMORIES),
    }


def _amount(value):
    """A quantity as a number: `500m` and `0.5` both come back as 0.5."""
    match = re.fullmatch(r"([0-9.]+)(m|k|M|G|Ki|Mi|Gi)?", str(value))
    if not match:
        return None
    number, unit = float(match.group(1)), match.group(2) or ""
    return number / 1000 if unit == "m" else number * _UNITS[unit]


def _same(got, want, where):
    assert got is not None, f"{where} is not set"
    assert _amount(got) == _amount(want), f"{where} is {got!r}, and it should be {want!r}"


def check(doc, b):
    assert doc.get("kind") == "Deployment", (
        f"this is a {doc.get('kind')}, and the task asks for a Deployment"
    )
    name = doc.get("metadata", {}).get("name")
    assert name == b["name"], f"metadata.name is {name!r}, and it should be {b['name']!r}"
    spec = doc.get("spec", {})
    selector = spec.get("selector", {}).get("matchLabels") or {}
    labels = spec.get("template", {}).get("metadata", {}).get("labels") or {}
    assert selector and all(labels.get(k) == v for k, v in selector.items()), (
        f"spec.selector.matchLabels is {selector} and the pod template is labelled "
        f"{labels}, and the two have to agree"
    )
    containers = spec.get("template", {}).get("spec", {}).get("containers") or []
    assert len(containers) == 1, (
        f"the pod template has {len(containers)} containers, and the task asks for one"
    )
    c = containers[0]
    assert c.get("image") == b["image"], (
        f"the container image is {c.get('image')!r}, not {b['image']!r}"
    )
    resources = c.get("resources") or {}
    requests = resources.get("requests") or {}
    limits = resources.get("limits") or {}
    _same(requests.get("cpu"), b["cpu"], "resources.requests.cpu")
    _same(requests.get("memory"), b["memory"], "resources.requests.memory")
    _same(limits.get("cpu"), b["cpu"], "resources.limits.cpu")
    _same(limits.get("memory"), b["memory"], "resources.limits.memory")
