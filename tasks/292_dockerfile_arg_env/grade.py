"""What one sitting of 292 asks for, and what counts as having answered it.

The task is which value is an ARG, which is an ENV, and which is both, so each message says
when the value exists: while building, while running, or both."""

PYTHONS = ["3.12", "3.13", "3.14"]


def brief(r):
    return {
        "python": r.choice(PYTHONS),
        "version": f"{r.randint(1, 4)}.{r.randint(0, 9)}.{r.randint(0, 20)}",
        "level": r.choice(["debug", "info", "warning"]),
    }


def _args(steps):
    out = {}
    for step in (s for s in steps if s["cmd"] == "ARG"):
        for w in step["words"]:
            name, _, default = w.partition("=")
            out[name] = (default or None, step["line"])
    return out


def _env(steps):
    out = {}
    for step in (s for s in steps if s["cmd"] == "ENV"):
        words = step["words"]
        if words and "=" not in words[0]:
            out[words[0]] = (" ".join(words[1:]), step["line"])
        else:
            out.update((w.split("=", 1)[0], (w.split("=", 1)[1], step["line"])) for w in words if "=" in w)
    return out


def _refers(value, name):
    return value in (f"${{{name}}}", f"${name}")


def check(stages, b):
    assert len(stages) == 1, f"one FROM, one stage: this file has {len(stages)}"
    stage = stages[0]
    top = _args(stage["globals"])
    assert "PYTHON_VERSION" in top, (
        "declare `ARG PYTHON_VERSION` above FROM: an ARG inside the stage does not exist yet "
        "when FROM is read"
    )
    assert top["PYTHON_VERSION"][0] == b["python"], (
        f"PYTHON_VERSION defaults to {top['PYTHON_VERSION'][0]!r}, and it should default to {b['python']!r}"
    )
    assert stage["base"] in ("python:${PYTHON_VERSION}-slim", "python:$PYTHON_VERSION-slim"), (
        f"FROM {stage['base']} should read the version from the ARG: `python:${{PYTHON_VERSION}}-slim`"
    )
    args, env = _args(stage["steps"]), _env(stage["steps"])
    assert "APP_VERSION" in args, "APP_VERSION is set at build time, so it is an ARG inside the stage"
    assert args["APP_VERSION"][0] == b["version"], (
        f"ARG APP_VERSION defaults to {args['APP_VERSION'][0]!r}, and it should default to {b['version']!r}"
    )
    assert "APP_VERSION" in env, (
        "an ARG is gone once the build ends, and the app reads APP_VERSION when it runs: "
        "hand it on with ENV"
    )
    value, line = env["APP_VERSION"]
    assert _refers(value, "APP_VERSION"), (
        f"line {line}: ENV APP_VERSION={value} should take the ARG's value, `${{APP_VERSION}}`, "
        "so `--build-arg APP_VERSION=...` still reaches the app"
    )
    assert line > args["APP_VERSION"][1], f"line {line} reads APP_VERSION before the ARG declares it"
    assert "LOG_LEVEL" not in args and "LOG_LEVEL" not in top, (
        "LOG_LEVEL is only needed while the app runs: ENV, not ARG"
    )
    assert env.get("LOG_LEVEL", (None,))[0] == b["level"], f"set ENV LOG_LEVEL={b['level']}"
    cmd = stage.all("CMD")
    assert len(cmd) == 1 and cmd[0]["exec"] and cmd[0]["exec"][-1].endswith("app.py"), (
        "one CMD, in exec form, running app.py with python"
    )
