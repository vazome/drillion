"""What one sitting of 278 asks for, and what counts as having answered it.

The schema has already run by the time `check_many` does, and the file holds two objects,
`---`-separated, so they arrive here as a list. Every message here is what the learner
reads, so each one names the field and what it should have held."""

CLASSES = ["fast", "slow", "archive"]
PROVISIONERS = ["rancher.io/local-path", "ebs.csi.aws.com", "file.csi.azure.com"]
POLICIES = ["Delete", "Retain"]
CLAIMS = ["media", "scratch", "exchange"]
CAPACITIES = ["1Gi", "5Gi"]


def brief(r):
    return {
        "name": r.choice(CLASSES),
        "provisioner": r.choice(PROVISIONERS),
        "policy": r.choice(POLICIES),
        "claim": r.choice(CLAIMS),
        "capacity": r.choice(CAPACITIES),
    }


def check_many(docs, b):
    [sc, pvc] = docs
    assert sc.get("kind") == "StorageClass", (
        f"the first document is a {sc.get('kind')}, and the class goes first so the "
        "claim naming it is never pointing at nothing"
    )
    assert sc.get("provisioner") == b["provisioner"], (
        f"the StorageClass's provisioner is {sc.get('provisioner')!r}, and it should be "
        f"{b['provisioner']!r}: that is the controller who will cut the disk"
    )
    policy = sc.get("reclaimPolicy")
    assert policy == b["policy"], (
        f"reclaimPolicy is {policy!r}, and it should be {b['policy']!r}: Delete tears "
        "the disk down with the claim, Retain keeps it for a human to deal with"
    )
    assert sc.get("volumeBindingMode") == "WaitForFirstConsumer", (
        f"volumeBindingMode is {sc.get('volumeBindingMode')!r}, and the task asks for "
        "WaitForFirstConsumer: no disk until a pod actually needs one"
    )

    assert pvc.get("kind") == "PersistentVolumeClaim", (
        f"the second document is a {pvc.get('kind')}, and the task asks for the claim "
        "that orders from the class"
    )
    assert pvc.get("metadata", {}).get("name") == b["claim"], (
        f"the claim's metadata.name is {pvc.get('metadata', {}).get('name')!r}, and it "
        f"should be {b['claim']!r}"
    )
    spec = pvc.get("spec", {})
    assert spec.get("storageClassName") == b["name"], (
        f"the claim's spec.storageClassName is {spec.get('storageClassName')!r}, and it "
        f"should name the class {b['name']!r} from the first document: that name is the "
        "whole order"
    )
    asked = spec.get("resources", {}).get("requests", {}).get("storage")
    assert asked == b["capacity"], (
        f"the claim's resources.requests.storage is {asked!r}, and it should ask for "
        f"{b['capacity']!r}"
    )
