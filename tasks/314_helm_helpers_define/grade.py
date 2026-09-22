"""What one sitting of 314 asks for, and what counts as having answered it.

The chart's Deployment and Service call three named templates that the learner's
`_helpers.tpl` defines. Two renders under two release names, so a helper that types a
name in instead of reading it fails the one that does not match."""

RELEASES = ["checkout", "billing", "inventory", "search", "ledger"]
CHART = "web-1.4.0"


def brief(r):
    one, two = r.sample(RELEASES, 2)
    return {"release": one, "other_release": two}


def renders(b):
    return [
        {"release": b["release"], "values": {"replicaCount": 2}},
        {"release": b["other_release"], "values": {"replicaCount": 3}},
    ]


def check(docs, b, render):
    release = render["release"]
    by_kind = {d.get("kind"): d for d in docs}
    assert sorted(by_kind) == ["Deployment", "Service"], (
        f"the chart should render a Deployment and a Service, not {sorted(by_kind)}"
    )
    selector = {"app.kubernetes.io/name": "web", "app.kubernetes.io/instance": release}
    labels = {
        **selector,
        "helm.sh/chart": CHART,
        "app.kubernetes.io/managed-by": "Helm",
    }
    for kind, doc in sorted(by_kind.items()):
        name = doc["metadata"]["name"]
        assert name == f"{release}-web", (
            f"the {kind} is named {name!r}, and web.fullname should make it "
            f"{release + '-web'!r}: the release name, a dash, the chart name"
        )
        got = doc["metadata"].get("labels") or {}
        assert got == labels, (
            f"the {kind}'s labels rendered as {got}, and web.labels should give exactly "
            f"{labels}"
        )
    spec = by_kind["Deployment"]["spec"]
    got = spec["selector"].get("matchLabels") or {}
    assert got == selector, (
        f"the Deployment's selector rendered as {got}, and web.selectorLabels should "
        f"give exactly {selector}"
    )
    got = spec["template"]["metadata"].get("labels") or {}
    assert got == selector, (
        f"the pod template's labels rendered as {got}, not {selector}"
    )
    got = by_kind["Service"]["spec"].get("selector") or {}
    assert got == selector, f"the Service's selector rendered as {got}, not {selector}"
