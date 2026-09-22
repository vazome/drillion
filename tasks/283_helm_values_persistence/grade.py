"""What one sitting of 283 asks for, and what counts as having answered it.

With persistence off the chart renders a Deployment and nothing else, and it is a valid
render. So the first thing checked is that the claim exists at all, and that the pod
actually mounts it: the chart wires both from the same switch."""

RELEASES = ["notes", "wiki", "journal", "drafts"]
IMAGES = ["ghcr.io/acme/notes:3.1", "ghcr.io/acme/notes:3.2"]


def brief(r):
    return {
        "release": r.choice(RELEASES),
        "image": r.choice(IMAGES),
        "size": r.choice(["2Gi", "5Gi", "10Gi", "500Mi"]),
        "storage_class": r.choice(["fast-ssd", "standard-rwo", "local-path"]),
    }


def check(docs, b, render):
    claims = [d for d in docs if d.get("kind") == "PersistentVolumeClaim"]
    assert claims, (
        "the chart rendered no PersistentVolumeClaim: the claim only renders when "
        ".Values.persistence.enabled is true"
    )
    claim = claims[0]
    want = f"{render['release']}-data"
    assert claim["metadata"]["name"] == want, "the claim should be named " + want
    size = claim["spec"]["resources"]["requests"]["storage"]
    assert size == b["size"], (
        f"the claim requests {size!r}, and it should request {b['size']!r}: the template "
        "reads .Values.persistence.size and falls back to 1Gi"
    )
    storage_class = claim["spec"].get("storageClassName")
    assert storage_class == b["storage_class"], (
        f"the claim's storageClassName is {storage_class!r}, and it should be "
        f"{b['storage_class']!r}: the template reads .Values.persistence.storageClass "
        "and falls back to standard"
    )
    deployment = [d for d in docs if d.get("kind") == "Deployment"][0]
    pod = deployment["spec"]["template"]["spec"]
    assert pod["containers"][0]["image"] == b["image"], (
        f"the image rendered as {pod['containers'][0]['image']!r}, not {b['image']!r}"
    )
    claimed = [
        v["persistentVolumeClaim"]["claimName"]
        for v in pod.get("volumes") or []
        if "persistentVolumeClaim" in v
    ]
    assert claimed == [want], "the pod should mount the claim " + want
