"""What one sitting of 277 asks for, and what counts as having answered it.

The schema has already run by the time `check_many` does, and the file holds two objects,
`---`-separated, so they arrive here as a list. Every message here is what the learner
reads, so each one names the field and what it should have held."""

NAMES = ["cache-data", "db-files", "uploads"]
CAPACITIES = ["1Gi", "2Gi", "5Gi"]
MODES = ["ReadWriteOnce", "ReadWriteMany"]
CLASSES = ["fast", "slow"]


def brief(r):
    return {
        "name": r.choice(NAMES),
        "capacity": r.choice(CAPACITIES),
        "accessMode": r.choice(MODES),
        "storageClass": r.choice(CLASSES),
    }


def check_many(docs, b):
    [pv, pvc] = docs
    assert pv.get("kind") == "PersistentVolume", (
        f"the first document is a {pv.get('kind')}, and the volume that holds goes first"
    )
    spec0 = pv.get("spec", {})
    capacity = spec0.get("capacity", {}).get("storage")
    assert capacity == b["capacity"], (
        f"spec.capacity.storage is {capacity!r}, and it should be {b['capacity']!r}: "
        "volumes are sized in binary units, and 1G, a decimal billion, is not 1Gi, a "
        "binary one"
    )
    modes0 = spec0.get("accessModes") or []
    assert modes0 == [b["accessMode"]], (
        f"the PV's spec.accessModes is {modes0}, and it should hold exactly "
        f"{b['accessMode']!r}"
    )
    assert spec0.get("storageClassName") == b["storageClass"], (
        f"the PV's spec.storageClassName is {spec0.get('storageClassName')!r}, and it "
        f"should be {b['storageClass']!r}: the shared class is how the claim finds it"
    )

    assert pvc.get("kind") == "PersistentVolumeClaim", (
        f"the second document is a {pvc.get('kind')}, and the task asks for the claim "
        "that asks for the volume"
    )
    spec1 = pvc.get("spec", {})
    asked = spec1.get("resources", {}).get("requests", {}).get("storage")
    assert asked == b["capacity"], (
        f"the PVC's resources.requests.storage is {asked!r}, and it should ask for "
        f"{b['capacity']!r}, the same quantity the volume holds"
    )
    modes1 = spec1.get("accessModes") or []
    assert modes1 == [b["accessMode"]], (
        f"the PVC's spec.accessModes is {modes1}, and a claim only binds a volume whose "
        f"modes cover its own: {b['accessMode']!r}"
    )
    assert spec1.get("storageClassName") == b["storageClass"], (
        f"the PVC's spec.storageClassName is {spec1.get('storageClassName')!r}, and it "
        f"should name the same class as the PV: {b['storageClass']!r}"
    )
