"""Twelve-factor apps read config from the environment, so every ops script does too."""

import os

from _lib import rng

META = {"topic": 36, "title": "os.environ.get — config with defaults", "tier": 3,
        "minutes": 12, "prereqs": []}

TRUTHY = {"1", "true", "yes", "on"}      # given — do not edit


def solve():
    """WHY: A service runs inside a container. Operators change its port,
    timeout, debug mode and region by setting environment variables (named
    settings the operating system hands to a process at start) instead of
    editing files. Some settings have sensible defaults; the database
    address does not, and booting against a guessed database is an incident
    waiting to happen. You write the startup code that reads them all and
    converts them from text to the right types.

    YOU GET: nothing — you build the thing from scratch. The test sets the
    environment variables before calling you; you read them.

    YOU RETURN: a dict with the keys "port", "timeout", "debug", "region"
    and "database_url", typed as described in the rules below. If
    DATABASE_URL is not set you do not return at all: the lookup must fail
    with a KeyError that you let escape.

    ─── exact rules ───
    Read this program's config out of the environment and return it.

    Takes no arguments: the environment IS the input. Read os.environ.

        APP_PORT      int,   default 8080
        APP_TIMEOUT   float, default 5.0
        APP_DEBUG     bool,  default False
        APP_REGION    str,   default "us-east-1"
        DATABASE_URL  str,   REQUIRED — no default

    APP_DEBUG is true when its value, lowercased, is in TRUTHY (given above);
    anything else is false. Every environment value arrives as a string, so
    "8080" is not 8080 and "0" is not False — convert deliberately.

    Return exactly:

        {"port": 9000, "timeout": 2.5, "debug": True,
         "region": "eu-west-1", "database_url": "postgres://db-7/app"}

    DATABASE_URL has no sensible default, so do not invent one. Read it with
    os.environ["DATABASE_URL"] and let the KeyError escape. A container that
    dies at startup with a named missing variable is a five-minute fix; one
    that boots against the wrong default database is an incident.
    """
    raise NotImplementedError


HINTS = [
    ("os.environ is a plain dict-like object of strings. Two ways to read from "
    "it, and the difference is the whole exercise: the method that takes a "
    "fallback never fails, square brackets fail loudly. Optional settings want "
    "the first, required settings want the second. Nothing in there is ever an "
    "int, a float or a bool — every value is a string, including \"0\"."),
    ("os.environ.get(NAME, default) returns a string, so wrap it: "
    "int(os.environ.get('APP_PORT', '8080')). For the bool there is no builtin "
    "parser — lowercase the string and test membership in TRUTHY. For the "
    "required one use os.environ['DATABASE_URL'] with no try/except."),
    ("Different program, same shape:\n"
    "    import os\n"
    "    cfg = {\n"
    "        'host': os.environ.get('SMTP_HOST', 'localhost'),\n"
    "        'port': int(os.environ.get('SMTP_PORT', '25')),\n"
    "        'tls': os.environ.get('SMTP_TLS', 'no').lower() in {'1', 'true', 'yes', 'on'},\n"
    "        'password': os.environ['SMTP_PASSWORD'],   # required, no default\n"
    "    }\n"
    "Defaults for what you can guess, a hard failure for what you cannot."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

_KEYS = ("APP_PORT", "APP_TIMEOUT", "APP_DEBUG", "APP_REGION", "DATABASE_URL")


def _gen(r):
    """A dict of env vars to set. Keys go missing at random."""
    regions = ["us-east-1", "eu-west-1", "ap-south-1", "us-west-2", "eu-north-1"]
    env = {}
    if r.random() < 0.7:
        env["APP_PORT"] = str(r.randint(1024, 65000))
    if r.random() < 0.6:
        env["APP_TIMEOUT"] = f"{r.randint(1, 600) / 10:.1f}"
    if r.random() < 0.7:
        env["APP_DEBUG"] = r.choice(["1", "0", "true", "TRUE", "False", "yes",
                                     "no", "on", "off", "", "True"])
    if r.random() < 0.6:
        env["APP_REGION"] = r.choice(regions)
    if r.random() < 0.75:
        host = r.choice(["db", "pg", "aurora", "primary"])
        env["DATABASE_URL"] = f"postgres://{host}-{r.randint(1, 9)}/{r.choice(['app', 'core', 'billing'])}"
    return env


def _reference():
    return {
        "port": int(os.environ.get("APP_PORT", "8080")),
        "timeout": float(os.environ.get("APP_TIMEOUT", "5.0")),
        "debug": os.environ.get("APP_DEBUG", "").lower() in TRUTHY,
        "region": os.environ.get("APP_REGION", "us-east-1"),
        "database_url": os.environ["DATABASE_URL"],
    }


def test_solve():
    r = rng()
    for _ in range(5):
        env = _gen(r)
        saved = dict(os.environ)
        try:
            for key in _KEYS:                    # never trust the ambient env
                os.environ.pop(key, None)
            os.environ.update(env)
            if "DATABASE_URL" in env:
                assert solve() == _reference()
            else:
                try:
                    solve()
                except KeyError:
                    pass
                else:
                    raise AssertionError("missing DATABASE_URL must raise KeyError")
        finally:
            os.environ.clear()
            os.environ.update(saved)
