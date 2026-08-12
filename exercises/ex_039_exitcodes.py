"""A pipeline reads one thing from your script: the exit code."""

from _lib import rng

META = {"topic": 39, "title": "exit codes — main(argv) returns an int", "tier": 3,
        "minutes": 12, "prereqs": []}

KNOWN_SERVICES = ("api", "web", "db", "cache")      # given — do not edit
MAX_REPLICAS = 10                                   # given — do not edit


def solve(argv):
    """This is the body of a CLI's main(). `argv` is the argument list with the
    program name already stripped, e.g. ["deploy", "web", "3"].

    Return an int. Do not call sys.exit, do not print.

    Check in this order and return the first code that applies:

        2  usage error      argv is not exactly 3 items, or argv[0] is not
                            "deploy" or "rollback", or argv[2] is not a
                            non-negative whole number
        3  unknown service  argv[1] is not in KNOWN_SERVICES
        1  refused          the replica count is above MAX_REPLICAS
        0  success

        ["deploy", "web", "3"]     ->  0
        ["deploy", "web", "99"]    ->  1
        ["ship", "web", "3"]       ->  2
        ["deploy", "ftp", "3"]     ->  3

    The real program ends with one line:

        sys.exit(main(sys.argv[1:]))

    Keep the decisions in a function that returns a code and let that single
    line do the exiting — then tests can call main() directly, which is exactly
    what is happening here.

    Why this matters: a shell && chain, a Makefile and every CI step read the
    exit code and nothing else. A script that prints ERROR and exits 0 gives
    you a green pipeline sitting on top of a broken deploy. 0 means success,
    anything else means failure, and distinct codes let the caller tell which
    failure it was without parsing your output.
    """
    raise NotImplementedError


HINTS = [
    "A process hands its parent one small integer, and only zero means "
    "success. So the interesting design question is not how to print an error, "
    "it is which number each kind of failure gets. Bad usage, bad input and a "
    "refused operation are three different things to whoever is calling you. "
    "Also note what the spec asks for: a function that RETURNS the number, not "
    "one that exits — those are different jobs and only one of them is "
    "testable.",
    "A chain of guard clauses, each returning early, in the order the spec "
    "lists them. The numeric check is str.isdigit on argv[2] — it is False for "
    "'-1', '3.5' and '', which is what you want here. Unpack the three items "
    "only after you know there are three. int() the count for the last "
    "comparison.",
    "A different tool, same shape:\n"
    "    import sys\n"
    "\n"
    "    def main(argv):\n"
    "        if len(argv) != 1:\n"
    "            return 2                    # usage\n"
    "        if not argv[0].endswith('.conf'):\n"
    "            return 3                    # wrong kind of input\n"
    "        return 0\n"
    "\n"
    "    if __name__ == '__main__':\n"
    "        sys.exit(main(sys.argv[1:]))\n"
    "\n"
    "    # $ python check.py a.conf b.conf ; echo $?\n"
    "    # 2\n"
    "One function returns codes, one line turns the code into an exit.",
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    cmd = r.choice(["deploy", "rollback"])
    good = r.choice(KNOWN_SERVICES)
    kind = r.choices(["ok", "refused", "arity", "cmd", "count", "service"],
                     weights=[3, 2, 2, 2, 2, 2])[0]
    if kind == "ok":
        return [cmd, good, str(r.randint(0, MAX_REPLICAS))]
    if kind == "refused":
        return [cmd, good, str(r.randint(MAX_REPLICAS + 1, 200))]
    if kind == "arity":
        full = [cmd, good, str(r.randint(0, 20)), "--now"]
        return full[: r.choice([0, 1, 2, 4])]
    if kind == "cmd":
        return [r.choice(["ship", "status", "restart", "Deploy", ""]),
                good, str(r.randint(0, 20))]
    if kind == "count":
        return [cmd, good, r.choice(["two", "-1", "3.5", "", "1e2", "0x4"])]
    return [cmd, r.choice(["ftp", "nginx", "postgres", "www", "API"]),
            str(r.randint(0, MAX_REPLICAS))]


def _reference(argv):
    if len(argv) != 3:
        return 2
    command, service, replicas = argv
    if command not in ("deploy", "rollback") or not replicas.isdigit():
        return 2
    if service not in KNOWN_SERVICES:
        return 3
    if int(replicas) > MAX_REPLICAS:
        return 1
    return 0


def test_solve():
    r = rng()
    for _ in range(10):
        argv = _gen(r)
        got = solve(list(argv))
        assert isinstance(got, int) and not isinstance(got, bool)
        assert got == _reference(argv)
