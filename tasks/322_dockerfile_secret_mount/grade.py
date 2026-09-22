"""What one sitting of 322 asks for, and what counts as having answered it.

The rules are about where the credential goes, so most of `check` is about where it must
not: an ARG, an ENV, or a file copied in are all visible in the finished image."""

import re

PYTHONS = ["3.12", "3.13", "3.14"]
SECRET = "pip_index_url"
# a name or value that carries the credential into the image's config or layers
CREDENTIAL = re.compile(r"PIP_INDEX_URL|PIP_EXTRA_INDEX_URL|TOKEN|PASSWORD|NETRC|pip\.conf", re.IGNORECASE)


def brief(r):
    return {"python": r.choice(PYTHONS), "port": r.choice([8000, 8080, 9000])}


def _all(stage, cmd):
    return [s for s in stage["steps"] if s["cmd"] == cmd]


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
    for step in stage["globals"] + stage["steps"]:
        if step["cmd"] in ("ARG", "ENV", "LABEL"):
            assert not CREDENTIAL.search(step["args"]), (
                f"line {step['line']}: {step['cmd']} is kept in the image's history, where "
                "`docker history` shows it to anyone who pulls the image. The credential "
                "only goes in through a secret mount"
            )
        if step["cmd"] in ("COPY", "ADD"):
            assert not any(CREDENTIAL.search(w) for w in step["words"]), (
                f"line {step['line']}: a copied credential is in a layer for good, even "
                "if a later RUN deletes it"
            )
    installs = [s for s in _all(stage, "RUN") if "pip" in s["words"] and "install" in s["words"]]
    assert len(installs) == 1, "install the requirements with one `RUN pip install`"
    install = installs[0]
    assert "-r" in install["words"] and "requirements.txt" in install["words"], (
        f"line {install['line']}: install from the file, `pip install -r requirements.txt`"
    )
    assert not any(CREDENTIAL.search(w) for w in install["words"]), (
        f"line {install['line']}: the index URL goes in through the secret mount, not on the "
        "command line, where it is written into the layer's history"
    )
    mount = _options(install["flags"].get("mount", ""))
    assert mount.get("type") == "secret", (
        f"line {install['line']}: give this RUN a secret mount, `--mount=type=secret,...`"
    )
    assert mount.get("id") == SECRET, (
        f"line {install['line']}: the secret's id is {SECRET!r}, the name `docker build "
        f"--secret` gives it, and not {mount.get('id')!r}"
    )
    assert mount.get("env") == "PIP_INDEX_URL", (
        f"line {install['line']}: expose the secret as the environment variable "
        "PIP_INDEX_URL, which pip reads, with `env=PIP_INDEX_URL`"
    )
    copies = _all(stage, "COPY")
    reqs = [c for c in copies if c["words"][:1] == ["requirements.txt"]]
    assert reqs and reqs[0]["line"] < install["line"], (
        "copy requirements.txt on its own before the install, as in 290"
    )
    exposed = [w for s in _all(stage, "EXPOSE") for w in s["words"]]
    assert exposed in ([str(b["port"])], [f"{b['port']}/tcp"]), f"EXPOSE {b['port']}"
    cmd = _all(stage, "CMD")
    assert len(cmd) == 1 and cmd[0]["exec"], "one CMD, in exec form"
    run = cmd[0]["exec"]
    assert run[0] == "uvicorn" and "app:app" in run, "CMD starts uvicorn serving `app:app`"
    assert _opt(run, "--host") == "0.0.0.0", "pass `--host 0.0.0.0` to uvicorn"
    assert _opt(run, "--port") == str(b["port"]), f"pass `--port {b['port']}` to uvicorn"
