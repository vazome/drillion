KNOWN_SERVICES = ("api", "web", "db", "cache")      # given — do not edit
MAX_REPLICAS = 10                                   # given — do not edit


def solve(argv: list[str]):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


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
