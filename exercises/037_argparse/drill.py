def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import argparse
import contextlib
import io

from _lib import rng


def _gen(r):
    """(argv, is_valid). The positional always comes first to keep nargs sane."""
    service = r.choice(["web", "api", "db", "cache", "worker", "gateway"])
    tags = ["canary", "blue", "green", "hotfix", "eu", "beta"]

    if r.random() < 0.6:                     # a valid command line
        argv = [service]
        parts = []
        if r.random() < 0.7:
            parts.append([r.choice(["-r", "--replicas"]), str(r.randint(0, 12))])
        if r.random() < 0.6:
            parts.append(["--env", r.choice(["dev", "stage", "prod"])])
        if r.random() < 0.5:
            parts.append(["--dry-run"])
        if r.random() < 0.6:
            parts.append(["--tag"] + r.sample(tags, r.randint(0, 3)))
        r.shuffle(parts)
        for part in parts:
            argv += part
        return argv, True

    kind = r.choice(["arity", "cmd", "int", "choice", "unknown"])
    if kind == "arity":
        return ([] if r.random() < 0.5 else [service, r.choice(tags)]), False
    if kind == "cmd":
        return [service, "--tag"] + r.sample(tags, 2) + ["--env"], False
    if kind == "int":
        return [service, r.choice(["-r", "--replicas"]),
                r.choice(["two", "3.5", "", "-", "1e3"])], False
    if kind == "choice":
        return [service, "--env", r.choice(["qa", "staging", "PROD", "live"])], False
    return [service, r.choice(["--force", "--replica", "-x", "--dryrun"])], False


def _reference():
    p = argparse.ArgumentParser(prog="deployctl")
    p.add_argument("service")
    p.add_argument("-r", "--replicas", type=int, default=1)
    p.add_argument("--env", default="dev", choices=["dev", "stage", "prod"])
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--tag", nargs="*", default=[])
    return p


def test_solve():
    r = rng()
    parser = solve()
    assert isinstance(parser, argparse.ArgumentParser)
    ref = _reference()
    for _ in range(8):
        argv, valid = _gen(r)
        if valid:
            assert vars(parser.parse_args(argv)) == vars(ref.parse_args(argv))
        else:
            with contextlib.redirect_stderr(io.StringIO()):   # argparse is chatty
                for p in (parser, ref):
                    try:
                        p.parse_args(argv)
                    except SystemExit:
                        continue
                    raise AssertionError(f"{argv} should have raised SystemExit")
