"""What one sitting of 290 asks for, and what counts as having answered it.

The point is the order of three lines, so every message names the lines involved."""

PYTHONS = ["3.12", "3.13", "3.14"]


def brief(r):
    return {"python": r.choice(PYTHONS), "port": r.choice([8000, 8080, 5000, 9000])}


def _all(stage, cmd):
    return [s for s in stage["steps"] if s["cmd"] == cmd]


def _copies(stage, name):
    return [c for c in _all(stage, "COPY") if name in c["words"][:-1] or "." in c["words"][:-1]]


def check(stages, b):
    assert len(stages) == 1, f"one FROM, one stage: this file has {len(stages)}"
    stage = stages[0]
    base = f"python:{b['python']}-slim"
    assert stage["base"] == base, f"the image is built FROM {stage['base']!r}, and it should be {base!r}"
    installs = [s for s in _all(stage, "RUN") if "pip" in s["words"] and "install" in s["words"]]
    assert len(installs) == 1, "install the dependencies with one `RUN pip install`"
    install = installs[0]
    assert "-r" in install["words"] and "requirements.txt" in install["words"], (
        f"line {install['line']}: install from the file, `pip install -r requirements.txt`, "
        "so the versions it pins are the ones installed"
    )
    reqs = _copies(stage, "requirements.txt")
    assert reqs and reqs[0]["words"][:-1] == ["requirements.txt"], (
        "copy requirements.txt on its own, before anything else is copied"
    )
    assert reqs[0]["line"] < install["line"], (
        f"line {install['line']} installs from requirements.txt before line "
        f"{reqs[0]['line']} has copied it in"
    )
    code = _copies(stage, "app.py")
    assert code, "copy app.py into the image"
    assert all(c["line"] > install["line"] for c in code), (
        f"line {code[0]['line']} copies the code before line {install['line']} installs the "
        "dependencies, so every edit to app.py reinstalls them all"
    )
    exposed = [w for s in _all(stage, "EXPOSE") for w in s["words"]]
    assert exposed in ([str(b["port"])], [f"{b['port']}/tcp"]), (
        f"EXPOSE the one port gunicorn binds, {b['port']}; this file exposes {exposed or 'none'}"
    )
    cmd = _all(stage, "CMD")
    assert len(cmd) == 1 and cmd[0]["exec"], "one CMD, in exec form"
    run = cmd[0]["exec"]
    assert run[0] == "gunicorn" and run[-1] == "app:app", (
        "CMD starts gunicorn and names the app last, as `app:app`: the module, then the Flask object"
    )
    bind = f"0.0.0.0:{b['port']}"
    assert bind in run or f"--bind={bind}" in run or f"-b={bind}" in run, (
        f"gunicorn binds 127.0.0.1:8000 unless told otherwise, which nothing outside the "
        f"container can reach: pass `--bind {bind}`"
    )
