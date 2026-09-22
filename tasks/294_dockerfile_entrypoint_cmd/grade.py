"""What one sitting of 294 asks for, and what counts as having answered it.

hadolint refuses a shell-form ENTRYPOINT or CMD (DL3025). `check` asks which of the two
holds the program and which holds the arguments."""

PYTHONS = ["3.12", "3.13", "3.14"]
QUEUES = ["emails", "invoices", "thumbnails", "webhooks", "exports"]
PROGRAMS = (["python", "worker.py"], ["python3", "worker.py"], ["python", "/app/worker.py"])


def brief(r):
    return {"python": r.choice(PYTHONS), "queue": r.choice(QUEUES), "concurrency": r.randint(2, 8)}


def _one(stage, cmd):
    found = [s for s in stage["steps"] if s["cmd"] == cmd]
    assert len(found) == 1, f"one {cmd}: this file has {len(found)}"
    return found[0]


def check(stages, b):
    assert len(stages) == 1, f"one FROM, one stage: this file has {len(stages)}"
    stage = stages[0]
    base = f"python:{b['python']}-slim"
    assert stage["base"] == base, f"the image is built FROM {stage['base']!r}, and it should be {base!r}"
    entry, cmd = _one(stage, "ENTRYPOINT"), _one(stage, "CMD")
    assert entry["exec"] in PROGRAMS, (
        f"line {entry['line']}: ENTRYPOINT is the program, and only the program: "
        "`python worker.py`, in exec form"
    )
    wanted = ["--queue", b["queue"], "--concurrency", str(b["concurrency"])]
    assert cmd["exec"] is not None and "worker.py" not in cmd["exec"], (
        f"line {cmd['line']}: CMD is only the default arguments; the program is ENTRYPOINT's"
    )
    assert cmd["exec"] == wanted, (
        f"line {cmd['line']}: CMD should be {wanted}, each option and each value its own string"
    )
