"""`with` is a promise that cleanup runs — including on the way out through an error."""

from _lib import rng

META = {"topic": 13, "title": "context managers — @contextmanager with guaranteed exit", "tier": 3,
        "minutes": 12, "prereqs": [12]}


def solve(events, name):
    """A context manager that brackets a block with two markers.

    Entering appends f"enter {name}" to the list events. Leaving appends
    f"exit {name}" — always, including when the body of the with-block raises.
    The exception must still reach the caller; you are logging, not swallowing.

        events = []
        with solve(events, "deploy"):
            events.append("work")
        # events == ["enter deploy", "work", "exit deploy"]

        events = []
        try:
            with solve(events, "deploy"):
                raise ValueError("pod 404")
        except ValueError:
            pass
        # events == ["enter deploy", "exit deploy"]   <- exit still ran

    Build it with contextlib.contextmanager: put that decorator on this
    function and place exactly one yield where the with-block's body belongs.
    Nothing needs to come back out of the yield — a bare `yield` is fine, and
    the caller uses no `as`.
    """
    raise NotImplementedError


HINTS = [
    "The easy half is a marker before and a marker after. The whole exercise "
    "is the second marker surviving a body that blows up. Ask what happens to "
    "the lines after the yield when the with-block raises — and which Python "
    "keyword exists precisely to make a block run either way.",
    "Import contextmanager from contextlib and decorate solve with it. That "
    "turns a generator into a context manager: everything before the yield runs "
    "on entry, everything after runs on exit. The catch is that an exception in "
    "the body is thrown back into your generator at the yield, so a plain line "
    "underneath it never executes. Wrap the yield in try, and put the exit "
    "marker in finally. Do not catch the exception — finally re-raises for you.",
    "Different data — a start/stop log around a block:\n"
    "    from contextlib import contextmanager\n"
    "\n"
    "    @contextmanager\n"
    "    def phase(log):\n"
    "        log.append('start')\n"
    "        try:\n"
    "            yield\n"
    "        finally:\n"
    "            log.append('stop')\n"
    "\n"
    "    log = []\n"
    "    try:\n"
    "        with phase(log):\n"
    "            raise RuntimeError('boom')\n"
    "    except RuntimeError:\n"
    "        pass\n"
    "    print(log)        # ['start', 'stop']\n"
    "Change finally to a bare line after the yield and the list stops at "
    "['start'] — the file handle, the lock, the temp dir all leak the same way.",
]


# ─────────────────────────────  below here is the machinery  ──────────────

from contextlib import contextmanager


def _gen(r):
    name = r.choice(["deploy", "drain", "migrate", "rollout", "backup", "reindex"])
    body = [r.choice(["step", "check", "wait", "push"]) + str(r.randint(1, 9))
            for _ in range(r.randint(1, 3))]
    boom = r.choice([ValueError, KeyError, RuntimeError, TimeoutError])
    msg = f"{r.choice(['pod', 'node', 'disk'])} {r.randint(100, 999)}"
    return name, body, boom, msg


def _run(factory, name, body, boom, msg):
    """Drive one context manager down both paths and report what happened."""
    clean = []
    with factory(clean, name):
        clean.extend(body)

    dirty, caught = [], None
    try:
        with factory(dirty, name):
            dirty.extend(body)
            raise boom(msg)
    except boom as exc:
        caught = str(exc)
    return clean, dirty, caught


@contextmanager
def _reference(events, name):
    events.append(f"enter {name}")
    try:
        yield
    finally:
        events.append(f"exit {name}")


def test_solve():
    r = rng()
    for _ in range(4):
        name, body, boom, msg = _gen(r)
        assert _run(solve, name, body, boom, msg) == _run(_reference, name, body, boom, msg)
