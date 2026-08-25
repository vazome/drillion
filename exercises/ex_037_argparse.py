"""Every internal tool grows a CLI; argparse is the one interviewers expect you to know."""

import argparse
import contextlib
import io

from _lib import rng

META = {"topic": 37, "title": "argparse — declare a CLI, get validation free",
        "tier": 3, "minutes": 15, "prereqs": []}


def solve():
    """WHY: The team has an internal deploy tool people run from the terminal:
    deployctl web -r 3 --env prod. It must accept a service name, a replica
    count, an environment, a dry-run switch and some tags, and it must
    reject bad input (a typo in the environment, a replica count that is not
    a number) with a clear message and a non-zero exit. Writing those checks
    by hand is tedious and buggy; you declare what the arguments are and let
    the standard library enforce them.

    YOU GET: nothing — you build the thing from scratch.

    YOU RETURN: the parser object itself, not yet used on anything. The test
    feeds it its own argument lists and checks what it accepts and what it
    rejects.

    ─── exact rules ───
    Build and return an argparse.ArgumentParser for a tool called deployctl.

    Return the parser itself. Do not parse anything, do not read sys.argv, do
    not print. The test calls parser.parse_args([...]) with its own lists.

    The command line looks like:

        deployctl web -r 3 --env prod --dry-run --tag canary blue

    Declare exactly these, with these dest names:

        service     positional, required, a string
        --replicas  int, default 1, also spelled -r
        --env       str, default "dev", only "dev" / "stage" / "prod" allowed
        --dry-run   a flag: absent -> False, present -> True (dest is dry_run)
        --tag       zero or more strings, default []

        parse_args(["web"])
          ->  Namespace(service='web', replicas=1, env='dev', dry_run=False, tag=[])

    Bad input must raise SystemExit: an unknown flag, a missing service, a
    --replicas that is not a number, an --env outside the three choices. You do
    not write any of those checks. You declare the type and the choices, and
    argparse does the rejecting, the exit code 2 and the --help text for you.
    """
    raise NotImplementedError


HINTS = [
    ("An argparse parser is a declaration, not code you step through. Each "
    "add_argument line states one argument's name, what it should be converted "
    "to, and what it defaults to. From those lines argparse builds the parsing, "
    "the error messages, the --help output and the exit code. A hand-rolled "
    "loop over sys.argv gets none of that and is the thing an interviewer is "
    "checking you have outgrown."),
    ("Five add_argument calls on an ArgumentParser. A name without dashes is a "
    "positional. type=int converts and rejects. default= supplies the fallback. "
    "choices=[...] restricts the allowed values. action='store_true' makes a "
    "flag. nargs='*' collects zero or more values into a list. argparse "
    "converts a leading -- and inner dashes into the attribute name, so "
    "--dry-run lands on .dry_run."),
    ("A different tool, same moves:\n"
    "    import argparse\n"
    "    p = argparse.ArgumentParser(prog='backupctl')\n"
    "    p.add_argument('bucket')\n"
    "    p.add_argument('-n', '--keep', type=int, default=7)\n"
    "    p.add_argument('--mode', default='full', choices=['full', 'incr'])\n"
    "    p.add_argument('--verbose', action='store_true')\n"
    "    p.add_argument('--skip', nargs='*', default=[])\n"
    "    print(p.parse_args(['logs', '-n', '3', '--skip', 'tmp', 'cache']))\n"
    "    # Namespace(bucket='logs', keep=3, mode='full', verbose=False,\n"
    "    #           skip=['tmp', 'cache'])\n"
    "Return the parser; let the caller do the parsing."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

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
