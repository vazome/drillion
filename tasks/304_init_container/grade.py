"""What one sitting of 304 asks for, and what counts as having answered it.

The schema has already run by the time `check` does, so the shape is sound and only the
requirements are left. Every message here is what the learner reads, so each one names the
field and what it should have held."""

NAMES = ["docs", "landing", "status-page", "handbook"]
SERVERS = [
    ("nginx:1.27", "/usr/share/nginx/html"),
    ("httpd:2.4", "/usr/local/apache2/htdocs"),
    ("caddy:2.10", "/srv"),
]
INIT_IMAGE = "busybox:1.37"


def brief(r):
    image, path = r.choice(SERVERS)
    return {"name": r.choice(NAMES), "image": image, "path": path}


def check(doc, b):
    assert doc.get("kind") == "Pod", f"this is a {doc.get('kind')}, and the task asks for a Pod"
    name = doc.get("metadata", {}).get("name")
    assert name == b["name"], f"metadata.name is {name!r}, and it should be {b['name']!r}"
    spec = doc.get("spec", {})
    inits = spec.get("initContainers") or []
    apps = spec.get("containers") or []
    assert len(inits) == 1, (
        f"spec.initContainers has {len(inits)} entries, and the task asks for one"
    )
    assert len(apps) == 1, (
        f"spec.containers has {len(apps)} entries, and the task asks for one app "
        "container: the init container belongs under initContainers"
    )
    init, app = inits[0], apps[0]
    assert init.get("image") == INIT_IMAGE, (
        f"the init container runs {init.get('image')!r}, and it should run {INIT_IMAGE!r}"
    )
    assert app.get("image") == b["image"], (
        f"the app container runs {app.get('image')!r}, and it should run {b['image']!r}"
    )

    scratch = {v.get("name") for v in spec.get("volumes") or [] if "emptyDir" in v}
    assert scratch, "the pod has no emptyDir volume for the two containers to share"
    init_at = {m.get("mountPath") for m in init.get("volumeMounts") or [] if m.get("name") in scratch}
    app_at = {m.get("mountPath") for m in app.get("volumeMounts") or [] if m.get("name") in scratch}
    assert init_at, "the init container does not mount the emptyDir, so its work goes nowhere"
    assert b["path"] in app_at, (
        f"the app container mounts the emptyDir at {sorted(app_at)}, and it should be at "
        f"{b['path']!r}, where {b['image']} looks for its files"
    )
    command = " ".join(str(part) for part in (init.get("command") or []) + (init.get("args") or []))
    assert command, "the init container has no command, so it writes nothing"
    assert any(path in command for path in init_at), (
        f"the init container's command never names {sorted(init_at)}, the directory "
        "where the shared volume is mounted in it"
    )
