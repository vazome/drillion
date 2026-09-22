"""What one sitting of 321 asks for, and what counts as having answered it.

A RUN's `--mount` arrives as the step's `mount` flag, the comma-separated options as one
string, which `_options` splits back into a mapping."""

PYTHONS = ["3.12", "3.13", "3.14"]
PIP_CACHE = "/root/.cache/pip"


def brief(r):
    return {"python": r.choice(PYTHONS), "port": r.choice([8000, 8080, 9000])}


def _options(mount):
    return dict(part.partition("=")[::2] for part in str(mount).split(",") if part)


def _opt(run, name):
    """The value given to `name` in an exec-form CMD, as `--name value` or `--name=value`."""
    for i, w in enumerate(run):
        if w == name and i + 1 < len(run):
            return run[i + 1]
        if w.startswith(name + "="):
            return w[len(name) + 1 :]
    return None


def check(stages, b):
    assert len(stages) == 1, f"one stage is enough here: this file has {len(stages)}"
    stage = stages[0]
    base = f"python:{b['python']}-slim"
    assert stage["base"] == base, f"line {stage['line']}: FROM {base}"
    installs = [s for s in stage.all("RUN") if "pip" in s["words"] and "install" in s["words"]]
    assert len(installs) == 1, "install the requirements with one `RUN pip install`"
    install = installs[0]
    assert "-r" in install["words"] and "requirements.txt" in install["words"], (
        f"line {install['line']}: install from the file, `pip install -r requirements.txt`"
    )
    mount = _options(install["flags"].get("mount", ""))
    assert mount.get("type") == "cache", (
        f"line {install['line']}: give this RUN a cache mount, `--mount=type=cache,...`"
    )
    target = mount.get("target") or mount.get("dst") or mount.get("destination")
    assert target == PIP_CACHE, (
        f"line {install['line']}: mount the cache at {PIP_CACHE}, where pip running as root "
        f"keeps it, and not at {target!r}"
    )
    assert "--no-cache-dir" not in install["words"], (
        f"line {install['line']}: --no-cache-dir tells pip not to use the cache you just "
        "mounted. The mount is never part of the image, so there is nothing to leave out"
    )
    copies = stage.all("COPY")
    reqs = [c for c in copies if c["words"][:1] == ["requirements.txt"]]
    code = [c for c in copies if "app.py" in c["words"][:-1] or "." in c["words"][:-1]]
    assert reqs and reqs[0]["line"] < install["line"], (
        "copy requirements.txt on its own before the install, as in 290"
    )
    assert code and all(c["line"] > install["line"] for c in code), (
        "copy app.py after the install, as in 290"
    )
    exposed = [w for s in stage.all("EXPOSE") for w in s["words"]]
    assert exposed in ([str(b["port"])], [f"{b['port']}/tcp"]), f"EXPOSE {b['port']}"
    cmd = stage.all("CMD")
    assert len(cmd) == 1 and cmd[0]["exec"], "one CMD, in exec form"
    run = cmd[0]["exec"]
    assert run[0] == "uvicorn" and "app:app" in run, "CMD starts uvicorn serving `app:app`"
    assert _opt(run, "--host") == "0.0.0.0", "pass `--host 0.0.0.0` to uvicorn"
    assert _opt(run, "--port") == str(b["port"]), f"pass `--port {b['port']}` to uvicorn"
