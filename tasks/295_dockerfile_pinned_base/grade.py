"""What one sitting of 295 asks for, and what counts as having answered it.

Nothing is pulled, so the digest is only checked for being the one the brief gives. The
labels are read as the builder reads them, with their quotes taken off."""

PYTHONS = ["3.12", "3.13", "3.14"]
REPOS = ["acme/checkout", "acme/ledger", "northwind/api", "contoso/search"]
SOURCE = "org.opencontainers.image.source"
REVISION = "org.opencontainers.image.revision"


def brief(r):
    return {
        "python": r.choice(PYTHONS),
        "digest": f"{r.getrandbits(256):064x}",
        "repo": f"https://github.com/{r.choice(REPOS)}",
    }


def _all(stage, cmd):
    return [s for s in stage["steps"] if s["cmd"] == cmd]


def _labels(stage):
    out = {}
    for step in _all(stage, "LABEL"):
        for w in step["words"]:
            key, _, value = w.partition("=")
            out[key.strip("\"'")] = (value.strip("\"'"), step["line"])
    return out


def check(stages, b):
    assert len(stages) == 1, f"one FROM, one stage: this file has {len(stages)}"
    stage = stages[0]
    tag = f"python:{b['python']}-slim"
    name, _, digest = stage["base"].partition("@")
    assert name == tag, f"the image is built FROM {name!r}, and it should be {tag!r}"
    assert digest, (
        f"FROM {tag} follows whatever the tag points at today; pin it with @sha256:, "
        "the digest in the brief"
    )
    assert digest == f"sha256:{b['digest']}", (
        f"the digest is {digest!r}, and it should be sha256: followed by the brief's"
    )
    labels = _labels(stage)
    assert labels.get(SOURCE, (None,))[0] == b["repo"], (
        f"LABEL {SOURCE} should be {b['repo']}: it is how a registry links the image to its code"
    )
    args = [w.partition("=")[0] for s in _all(stage, "ARG") for w in s["words"]]
    assert "REVISION" in args, "the commit is only known when the build runs: declare `ARG REVISION`"
    value, line = labels.get(REVISION, (None, 0))
    assert value in ("${REVISION}", "$REVISION"), (
        f"LABEL {REVISION} should be the build argument, `${{REVISION}}`, and not a fixed value"
    )
    arg_line = min(s["line"] for s in _all(stage, "ARG") if "REVISION" in s["args"])
    assert arg_line < line, f"line {line} reads REVISION before line {arg_line} declares it"
    cmd = _all(stage, "CMD")
    assert len(cmd) == 1 and cmd[0]["exec"] and cmd[0]["exec"][-1].endswith("app.py"), (
        "one CMD, in exec form, running app.py with python"
    )
