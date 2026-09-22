"""What one sitting of 289 asks for, and what counts as having answered it.

hadolint has passed and every COPY source is in the build context by the time `check`
runs. What is left is whether the image is the one the brief describes."""

PYTHONS = ["3.12", "3.13", "3.14"]


def brief(r):
    return {"python": r.choice(PYTHONS), "port": r.choice([8000, 8080, 5000, 9000])}


def _env(stage):
    """ENV as the builder sets it, in both spellings: `K=v K2=v2` and the older `K v`."""
    out = {}
    for step in stage.all("ENV"):
        words = step["words"]
        if words and "=" not in words[0]:
            out[words[0]] = " ".join(words[1:])
        else:
            out.update(w.split("=", 1) for w in words if "=" in w)
    return out


def check(stages, b):
    assert len(stages) == 1, f"one FROM, one stage: this file has {len(stages)}"
    stage = stages[0]
    base = f"python:{b['python']}-slim"
    assert stage["base"] == base, f"the image is built FROM {stage['base']!r}, and it should be {base!r}"
    workdir = stage.all("WORKDIR")
    assert workdir and workdir[0]["words"] == ["/app"], "set WORKDIR /app before copying anything"
    copies = stage.all("COPY")
    assert copies, "COPY app.py into the image"
    assert workdir[0]["line"] < copies[0]["line"], "WORKDIR comes before the COPY that relies on it"
    assert any(c["words"][:-1] == ["app.py"] and c["words"][-1] in (".", "./", "/app", "/app/") for c in copies), (
        "copy app.py alone into /app: `COPY app.py .` once WORKDIR is set"
    )
    env = _env(stage)
    assert env.get("PORT") == str(b["port"]), (
        f"the app reads its port from PORT, which is {env.get('PORT')!r} here and should be {b['port']}"
    )
    exposed = [w for s in stage.all("EXPOSE") for w in s["words"]]
    assert exposed in ([str(b["port"])], [f"{b['port']}/tcp"]), (
        f"EXPOSE the one port the app listens on, {b['port']}; this file exposes {exposed or 'none'}"
    )
    cmd = stage.all("CMD")
    assert len(cmd) == 1, "one CMD, the last word on what the container runs"
    assert cmd[0]["exec"] in (["python", "app.py"], ["python3", "app.py"], ["python", "/app/app.py"]), (
        f"CMD runs {cmd[0]['args']}, and it should run app.py with python, in exec form"
    )
