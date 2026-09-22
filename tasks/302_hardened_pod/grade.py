"""What one sitting of 302 asks for, and what counts as having answered it.

The schema has already run by the time `check` does, so the shape is sound and only the
requirements are left. Every message here is what the learner reads, so each one names the
field and what it should have held.

A field the rules allow on either level is read the way the kubelet reads it: the
container's own value wins, and the pod's fills in where the container says nothing."""

NAMES = ["storefront", "docs", "status-page", "landing"]
IMAGES = ["nginxinc/nginx-unprivileged:1.27", "ghcr.io/acme/storefront:2.0"]
UIDS = [101, 1000, 10001, 65532]


def brief(r):
    return {"name": r.choice(NAMES), "image": r.choice(IMAGES), "uid": r.choice(UIDS)}


def check(doc, b):
    assert doc.get("kind") == "Pod", f"this is a {doc.get('kind')}, and the task asks for a Pod"
    name = doc.get("metadata", {}).get("name")
    assert name == b["name"], f"metadata.name is {name!r}, and it should be {b['name']!r}"
    spec = doc.get("spec", {})
    containers = spec.get("containers") or []
    assert len(containers) == 1, (
        f"the pod has {len(containers)} containers, and the task asks for one"
    )
    c = containers[0]
    assert c.get("image") == b["image"], (
        f"the container image is {c.get('image')!r}, not {b['image']!r}"
    )
    pod = spec.get("securityContext") or {}
    own = c.get("securityContext") or {}

    def either(key):
        return own[key] if key in own else pod.get(key)

    assert either("runAsNonRoot") is True, (
        "runAsNonRoot is not true on the pod or the container, and restricted requires it"
    )
    assert either("runAsUser") == b["uid"], (
        f"runAsUser is {either('runAsUser')!r}, and the image runs as user {b['uid']}"
    )
    seccomp = (either("seccompProfile") or {}).get("type")
    assert seccomp == "RuntimeDefault", (
        f"seccompProfile.type is {seccomp!r}, and restricted asks for 'RuntimeDefault'"
    )
    assert own.get("allowPrivilegeEscalation") is False, (
        "the container's allowPrivilegeEscalation is not false, so a setuid binary "
        "inside it could still make it root"
    )
    assert own.get("readOnlyRootFilesystem") is True, (
        "the container's readOnlyRootFilesystem is not true, so the process can rewrite "
        "its own image"
    )
    dropped = (own.get("capabilities") or {}).get("drop") or []
    assert "ALL" in dropped, (
        f"the container drops capabilities {dropped}, and restricted asks it to drop ALL"
    )

    scratch = {v.get("name") for v in spec.get("volumes") or [] if "emptyDir" in v}
    tmp = [m for m in c.get("volumeMounts") or [] if m.get("mountPath") == "/tmp"]
    assert tmp, "nothing is mounted at /tmp, and a read-only root leaves nowhere to write"
    assert tmp[0].get("name") in scratch, (
        f"the volume mounted at /tmp is {tmp[0].get('name')!r}, and it should be an "
        "emptyDir volume of the pod"
    )
