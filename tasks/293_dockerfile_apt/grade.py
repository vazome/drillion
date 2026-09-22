"""What one sitting of 293 asks for, and what counts as having answered it.

hadolint refuses `apt` for `apt-get` and a missing `-y`; the rest of an install done right
is advice to hadolint, and a requirement here."""

PYTHONS = ["3.12", "3.13", "3.14"]
PACKAGES = ["postgresql-client", "ca-certificates"]


def brief(r):
    return {"python": r.choice(PYTHONS)}


def _at(words, *wanted):
    """The index of the first of `wanted` in words, or None."""
    return next((i for i, w in enumerate(words) if w in wanted), None)


def check(stages, b):
    assert len(stages) == 1, f"one FROM, one stage: this file has {len(stages)}"
    stage = stages[0]
    base = f"python:{b['python']}-slim"
    assert stage["base"] == base, f"the image is built FROM {stage['base']!r}, and it should be {base!r}"
    apt = [s for s in stage.all("RUN") if "apt-get" in s["words"]]
    assert apt, "install the packages with apt-get in a RUN"
    assert len(apt) == 1, (
        f"lines {', '.join(str(s['line']) for s in apt)} each run apt-get: an update in its own "
        "layer is cached and goes stale, so update, install and clean up in one RUN"
    )
    run, words = apt[0], apt[0]["words"]
    assert not {"upgrade", "dist-upgrade"} & set(words), (
        f"line {run['line']}: upgrading is the base image's job, and a newer tag of it does it"
    )
    update, install = _at(words, "update"), _at(words, "install")
    assert update is not None and install is not None and update < install, (
        f"line {run['line']}: `apt-get update` first, in the same RUN as the install: a slim "
        "image ships with no package lists"
    )
    assert "--no-install-recommends" in words, (
        f"line {run['line']}: without --no-install-recommends, apt-get installs every package "
        "the ones you named merely suggest"
    )
    missing = [p for p in PACKAGES if p not in words]
    assert not missing, f"line {run['line']}: install {' and '.join(missing)} as well"
    extra = [w for w in words[install + 1 :] if not w.startswith("-") and w != "&&"]
    extra = extra[: extra.index("rm")] if "rm" in extra else extra
    assert set(extra) <= set(PACKAGES), (
        f"line {run['line']}: install only what backup.py needs, not {', '.join(sorted(set(extra) - set(PACKAGES)))}"
    )
    clean = _at(words, "/var/lib/apt/lists/*", "/var/lib/apt/lists")
    assert clean is not None and clean > install and "rm" in words, (
        f"line {run['line']}: remove /var/lib/apt/lists/* at the end of the same RUN; in a later "
        "RUN the lists are already baked into a layer"
    )
    copies = stage.all("COPY")
    assert copies and all(c["line"] > run["line"] for c in copies), (
        "copy backup.py after the install, so an edit to it does not repeat the install"
    )
    cmd = stage.all("CMD")
    assert len(cmd) == 1 and cmd[0]["exec"] and cmd[0]["exec"][-1].endswith("backup.py"), (
        "one CMD, in exec form, running backup.py with python"
    )
