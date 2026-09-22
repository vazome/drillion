"""What one sitting of 319 asks for, and what counts as having answered it.

A HEALTHCHECK's options arrive as the step's flags, and what follows them is `CMD` and the
probe, which is read back out of the step's arguments here."""

import json
import re

PYTHONS = ["3.12", "3.13", "3.14"]
FETCHERS = ("curl", "wget")


def brief(r):
    return {
        "python": r.choice(PYTHONS),
        "port": r.choice([8000, 8080, 9000]),
        "interval": r.choice([10, 15, 30]),
    }


def _opt(run, name):
    """The value given to `name` in an exec-form CMD, as `--name value` or `--name=value`."""
    for i, w in enumerate(run):
        if w == name and i + 1 < len(run):
            return run[i + 1]
        if w.startswith(name + "="):
            return w[len(name) + 1 :]
    return None


def _seconds(value):
    match = re.fullmatch(r"(\d+)s", str(value))
    return int(match.group(1)) if match else None


def check(stages, b):
    assert len(stages) == 1, f"one stage is enough here: this file has {len(stages)}"
    stage = stages[0]
    base = f"python:{b['python']}-slim"
    assert stage["base"] == base, f"line {stage['line']}: FROM {base}"
    for step in stage.all("RUN"):
        assert not any(f in step["words"] for f in FETCHERS), (
            f"line {step['line']}: installing curl or wget for a health check adds a tool "
            "the app never uses: Python can fetch a URL on its own"
        )
    checks = stage.all("HEALTHCHECK")
    assert len(checks) == 1, f"one HEALTHCHECK, and this file has {len(checks)}"
    hc = checks[0]
    interval = _seconds(hc["flags"].get("interval"))
    assert interval == b["interval"], (
        f"line {hc['line']}: --interval={b['interval']}s, and it is "
        f"{hc['flags'].get('interval')!r}"
    )
    timeout = _seconds(hc["flags"].get("timeout"))
    assert timeout and timeout < b["interval"], (
        f"line {hc['line']}: set --timeout in seconds, shorter than the interval. The "
        "default is 30s, and a probe that hangs that long tells you nothing in time"
    )
    kind, _, probe = hc["args"].partition(" ")
    assert kind.upper() == "CMD", f"line {hc['line']}: HEALTHCHECK options, then CMD and the probe"
    try:
        probe = json.loads(probe)
    except ValueError:
        probe = None
    assert isinstance(probe, list) and probe, (
        f"line {hc['line']}: write the probe in exec form, a JSON array, so no shell is "
        "needed to run it"
    )
    assert probe[0] == "python" and not any(f in probe for f in FETCHERS), (
        f"line {hc['line']}: the probe runs python, which the image already has"
    )
    script = " ".join(probe)
    urls = re.findall(r"http://(localhost|127\.0\.0\.1):(\d+)(/\S*?)['\"]", script)
    assert urls, f"line {hc['line']}: the probe fetches http://localhost:{b['port']}/health"
    _, port, path = urls[0]
    assert (int(port), path) == (b["port"], "/health"), (
        f"line {hc['line']}: the probe fetches port {port} path {path!r}, and the app "
        f"answers on port {b['port']} at '/health'"
    )

    exposed = [w for s in stage.all("EXPOSE") for w in s["words"]]
    assert exposed in ([str(b["port"])], [f"{b['port']}/tcp"]), f"EXPOSE {b['port']}"
    cmd = stage.all("CMD")
    assert len(cmd) == 1 and cmd[0]["exec"], "one CMD, in exec form"
    run = cmd[0]["exec"]
    assert run[0] == "uvicorn" and "app:app" in run, "CMD starts uvicorn serving `app:app`"
    assert _opt(run, "--host") == "0.0.0.0", "pass `--host 0.0.0.0` to uvicorn"
    assert _opt(run, "--port") == str(b["port"]), f"pass `--port {b['port']}` to uvicorn"
