"""What one sitting of 317 asks for, and what counts as having answered it.

The chart's ConfigMap template is fixed, so what `include` renders from it is known
exactly, and the checksum a correct Deployment carries can be computed here and compared.
Two renders with different config, so a checksum typed in by hand, or one taken over the
unrendered file, matches neither."""

import hashlib

RELEASES = ["checkout", "billing", "inventory", "search", "ledger"]
LEVELS = ["debug", "info", "warn", "error"]


def brief(r):
    one, two = r.sample(RELEASES, 2)
    first, second = r.sample(LEVELS, 2)
    return {
        "release": one,
        "level": first,
        "concurrency": r.randint(2, 8),
        "other_release": two,
        "other_level": second,
        "other_concurrency": r.randint(9, 16),
    }


def renders(b):
    return [
        {
            "release": b[f"{p}release"],
            "values": {
                "config": {
                    "logLevel": b[f"{p}level"],
                    "concurrency": b[f"{p}concurrency"],
                }
            },
        }
        for p in ("", "other_")
    ]


def _configmap(release, config):
    """templates/configmap.yaml as Helm renders it for these values."""
    return (
        "apiVersion: v1\nkind: ConfigMap\nmetadata:\n"
        f"  name: {release}-config\ndata:\n"
        f'  LOG_LEVEL: "{config["logLevel"]}"\n'
        f'  CONCURRENCY: "{config["concurrency"]}"\n'
    )


def check(docs, b, render):
    release, values = render["release"], render["values"]
    by_kind = {d.get("kind"): d for d in docs}
    assert sorted(by_kind) == ["ConfigMap", "Deployment"], (
        f"the chart should render its ConfigMap and your Deployment, not {sorted(by_kind)}"
    )
    doc = by_kind["Deployment"]
    assert doc["metadata"]["name"] == release, (
        f"metadata.name rendered as {doc['metadata']['name']!r}, and it should be the "
        f"release name {release!r}"
    )
    spec = doc["spec"]
    selector = spec["selector"].get("matchLabels") or {}
    template = spec["template"]["metadata"]
    labels = template.get("labels") or {}
    assert selector.get("app") == release and labels.get("app") == release, (
        f"the selector and the pod template should both carry app: {release}, and they "
        f"rendered as {selector} and {labels}"
    )
    annotations = template.get("annotations") or {}
    assert "checksum/config" in annotations, (
        "the pod template has no checksum/config annotation, so changing the config "
        "leaves the pods running with the old one. On the Deployment's own metadata "
        "it would not help: only a change to the pod template rolls the pods"
    )
    want = hashlib.sha256(_configmap(release, values["config"]).encode()).hexdigest()
    got = annotations["checksum/config"]
    assert got == want, (
        f"checksum/config rendered as {got!r}, and the sha256 of the rendered ConfigMap "
        f"is {want!r}: include the rendered configmap.yaml and pipe it through sha256sum"
    )
    containers = spec["template"]["spec"]["containers"]
    assert len(containers) == 1, f"the pod runs {len(containers)} containers, not one"
    c = containers[0]
    want = f"{values['image']['repository']}:{values['image']['tag']}"
    assert c["image"] == want, (
        f"the image rendered as {c['image']!r}, and it should be {want!r}"
    )
    refs = [(e.get("configMapRef") or {}).get("name") for e in c.get("envFrom") or []]
    assert refs == [f"{release}-config"], (
        f"envFrom reads the ConfigMaps {refs}, and it should read {release + '-config'!r}"
    )
