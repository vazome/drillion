"""What one sitting of 291 asks for, and what counts as having answered it.

hadolint already refuses a last USER that is root (DL3002). It asks for `useradd -l` only
from six-digit UIDs up (DL3046); the log it prevents grows with any UID, so `check` asks at
every one, along with what the brief fixes: which UID, and in what order."""

PYTHONS = ["3.12", "3.13", "3.14"]


def brief(r):
    return {
        "python": r.choice(PYTHONS),
        "uid": r.choice([10001, 10100, 20000, 65532]),
        "port": r.choice([8000, 8080, 9000]),
    }


def _all(stage, cmd):
    return [s for s in stage["steps"] if s["cmd"] == cmd]


def check(stages, b):
    assert len(stages) == 1, f"one FROM, one stage: this file has {len(stages)}"
    stage, uid = stages[0], str(b["uid"])
    base = f"python:{b['python']}-slim"
    assert stage["base"] == base, f"the image is built FROM {stage['base']!r}, and it should be {base!r}"
    made = [s for s in _all(stage, "RUN") if {"useradd", "adduser"} & set(s["words"])]
    assert made, "create the user with `useradd` in a RUN, so the UID has a name in /etc/passwd"
    assert uid in made[0]["words"] or f"--uid={uid}" in made[0]["words"], (
        f"line {made[0]['line']}: the user is created without UID {uid}"
    )
    if "useradd" in made[0]["words"]:
        assert {"-l", "--no-log-init"} & set(made[0]["words"]), (
            f"line {made[0]['line']}: useradd without -l writes a lastlog record for every "
            f"UID below {uid}"
        )
    users = _all(stage, "USER")
    assert users, f"switch to the user with `USER {uid}`"
    last = users[-1]
    assert last["words"] and last["words"][0].split(":")[0] == uid, (
        f"line {last['line']}: USER {last['args']} should be the number {uid}: Kubernetes can "
        "only prove a numeric user is not root, so `runAsNonRoot` refuses a name"
    )
    assert last["line"] > made[0]["line"], "USER comes after the RUN that creates the user"
    copies = _all(stage, "COPY")
    assert copies, "copy app.py into the image"
    for c in copies:
        assert str(c["flags"].get("chown", "")).split(":")[0] == uid, (
            f"line {c['line']}: COPY without `--chown={uid}:{uid}` leaves the files owned "
            "by root"
        )
    runs_after = [s for s in _all(stage, "RUN") if s["line"] > last["line"]]
    assert not runs_after, (
        f"line {runs_after[0]['line']} runs after USER, as the app's user: do the root work first"
        if runs_after else ""
    )
    assert b["port"] >= 1024
    env = {w.split("=", 1)[0]: w.split("=", 1)[1] for s in _all(stage, "ENV") for w in s["words"] if "=" in w}
    assert env.get("PORT") == str(b["port"]), f"set ENV PORT={b['port']}"
    exposed = [w for s in _all(stage, "EXPOSE") for w in s["words"]]
    assert exposed in ([str(b["port"])], [f"{b['port']}/tcp"]), f"EXPOSE {b['port']}, the port in PORT"
    cmd = _all(stage, "CMD")
    assert len(cmd) == 1 and cmd[0]["exec"] and cmd[0]["exec"][-1].endswith("app.py"), (
        "one CMD, in exec form, running app.py with python"
    )
