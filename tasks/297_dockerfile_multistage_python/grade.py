"""What one sitting of 297 asks for, and what counts as having answered it.

`check` follows the virtualenv: where the build stage makes it, what pip installs into it,
and whether the runtime stage copies it to the same path and finds it on PATH."""

PYTHONS = ["3.12", "3.13", "3.14"]


def brief(r):
    return {"python": r.choice(PYTHONS), "port": r.choice([8000, 8080, 9000])}


def _all(stage, cmd):
    return [s for s in stage["steps"] if s["cmd"] == cmd]


def _path(stage, before=None):
    """PATH as the stage's ENV lines set it, up to the line `before`."""
    value = ""
    for step in _all(stage, "ENV"):
        if before is not None and step["line"] > before:
            break
        for w in step["words"]:
            if w.startswith("PATH="):
                value = w[5:].strip("\"'")
    return value


def check(stages, b):
    assert len(stages) == 2, f"two stages, one to build and one to run: this file has {len(stages)}"
    build, final = stages
    base = f"python:{b['python']}-slim"
    for stage in stages:
        assert stage["base"] == base, (
            f"line {stage['line']}: both stages are FROM {base}. A virtualenv points at the "
            "interpreter that made it, so it only works on the same Python"
        )
    assert build["name"], "name the build stage, `FROM ... AS build`, so the next one can copy from it"
    made = [s for s in _all(build, "RUN") if "venv" in s["words"]]
    assert made, "make the virtualenv in the build stage: `RUN python -m venv /opt/venv`"
    venv = made[0]["words"][-1].rstrip("/")
    assert venv.startswith("/"), f"line {made[0]['line']}: give the virtualenv an absolute path"
    installs = [s for s in _all(build, "RUN") if "install" in s["words"] and any(w.endswith("pip") for w in s["words"])]
    assert len(installs) == 1, "install the requirements with one `RUN pip install` in the build stage"
    install = installs[0]
    assert "-r" in install["words"] and "requirements.txt" in install["words"], (
        f"line {install['line']}: install from the file, `pip install -r requirements.txt`"
    )
    into = f"{venv}/bin" in _path(build, install["line"]) or any(
        w.startswith(f"{venv}/bin/") for w in install["words"]
    )
    assert into, (
        f"line {install['line']}: this pip is the system one, and the packages land outside "
        f"{venv}: put {venv}/bin first on PATH before installing"
    )
    assert install["line"] > made[0]["line"], "make the virtualenv before installing into it"
    assert not [s for s in _all(final, "RUN") if "install" in s["words"]], (
        "the runtime stage installs nothing: everything it needs is in the virtualenv"
    )
    copied = [c for c in _all(final, "COPY") if c["flags"].get("from") == build["name"]]
    assert copied, f"copy the virtualenv `--from={build['name']}`"
    words = copied[0]["words"]
    assert [w.rstrip("/") for w in words] == [venv, venv], (
        f"line {copied[0]['line']}: copy {venv} to the same path. A virtualenv's scripts name "
        "its path inside them, so a moved one breaks"
    )
    cmd = _all(final, "CMD")
    assert len(cmd) == 1 and cmd[0]["exec"], "one CMD, in exec form"
    run = cmd[0]["exec"]
    assert f"{venv}/bin" in _path(final) or run[0].startswith(f"{venv}/bin/"), (
        f"ENV PATH resets with the stage: put {venv}/bin on PATH again, so the CMD finds gunicorn"
    )
    assert run[0].endswith("gunicorn") and run[-1] == "app:app", "CMD starts gunicorn serving `app:app`"
    bind = f"0.0.0.0:{b['port']}"
    assert bind in run or f"--bind={bind}" in run, f"pass `--bind {bind}` to gunicorn"
    exposed = [w for s in _all(final, "EXPOSE") for w in s["words"]]
    assert exposed in ([str(b["port"])], [f"{b['port']}/tcp"]), f"EXPOSE {b['port']}"
