"""Custom exceptions let callers catch a whole family of errors with one except."""

from _lib import rng

META = {"topic": 44, "title": "custom exceptions — a ConfigError family", "tier": 3,
        "minutes": 15, "prereqs": [43]}


class ConfigError(Exception):
    """Base class: anything wrong with a config. Given — do not edit."""


class MissingKeyError(ConfigError):
    """A required key is absent."""


class BadValueError(ConfigError):
    """A key is present but its value is unusable."""


def solve(configs):
    """WHY: A deploy tool reads a list of service configs and applies the good
    ones. Bad configs must be skipped, but the report has to say exactly
    what was wrong with each: a missing field, or a field holding a nonsense
    value. Real tools solve this with a family of related error types: the
    checks raise the specific one, and the loop catches the whole family
    with a single handler. Interviewers ask for exactly this design.

    YOU GET: `configs` — a list of dicts, like [{"name": "web", "replicas":
    3}, {"name": "db"}]. The test creates it and hands it to you; you never
    build it yourself. The error classes ConfigError, MissingKeyError and
    BadValueError are already defined above.

    YOU RETURN: a pair (applied, rejected): applied is a list of the names
    of good configs; rejected is a list of (position, error class name)
    pairs.

    ─── exact rules ───
    Validate a list of service configs. Each config should be a dict with
    a "name" (string) and "replicas" (an int, 0 or more).

    For each config, in order:
      - if "name" is missing, that is a MissingKeyError
      - else if "replicas" is missing, that is a MissingKeyError
      - else if replicas is not an int, or is negative, that is a BadValueError
      - otherwise the config is good

    Structure it the way real tools do: write the checks so they RAISE the
    specific exception, then wrap each config in try/except ConfigError — the
    base class catches both subtypes. Record type(err).__name__ for rejects.

    Return a pair (applied, rejected):
      applied  — list of names of good configs, in input order
      rejected — list of (index, exception class name) tuples, in input order

        [{"name": "web", "replicas": 3}, {"name": "db"}, {"name": "gw", "replicas": -1}]
        ->  (["web"], [(1, "MissingKeyError"), (2, "BadValueError")])

    Why a hierarchy: the loop only needs "this config is bad, skip it", so it
    catches ConfigError. The message still says exactly what was wrong. That
    is the whole pitch for custom exception classes in an interview.
    """
    raise NotImplementedError


HINTS = [
    ("Raise the most specific class you can; catch the most general one the "
    "caller can handle. Here the checks raise MissingKeyError or BadValueError, "
    "and the loop catches ConfigError — one except clause covers both, and "
    "plain bugs like TypeError still crash loudly, which you want."),
    ("Inside a for-loop over enumerate(configs): a try block that checks "
    "'name' then 'replicas' with `in`, raising MissingKeyError(key), then "
    "checks isinstance(value, int) and value >= 0, raising BadValueError. "
    "In `except ConfigError as err`, append (i, type(err).__name__)."),
    ("Different data, same shape:\n"
    "    class ParseError(Exception): pass\n"
    "    class EmptyLine(ParseError): pass\n"
    "\n"
    "    def read(line):\n"
    "        if not line:\n"
    "            raise EmptyLine('blank')\n"
    "        return line.upper()\n"
    "\n"
    "    for line in ['hi', '']:\n"
    "        try:\n"
    "            print(read(line))\n"
    "        except ParseError as err:\n"
    "            print('skipped:', type(err).__name__)\n"
    "    # HI\n"
    "    # skipped: EmptyLine\n"
    "The raiser names the exact problem; the catcher only knows the family."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    names = ["web", "api", "db", "cache", "worker", "queue", "cron"]
    r.shuffle(names)
    configs = []
    for name in names[: r.randint(4, 7)]:
        kind = r.choices(["ok", "missing", "bad"], weights=[3, 1, 1])[0]
        if kind == "ok":
            configs.append({"name": name, "replicas": r.randint(0, 9)})
        elif kind == "missing":
            configs.append(r.choice([{"replicas": r.randint(0, 9)},
                                     {"name": name}]))
        else:
            configs.append({"name": name,
                            "replicas": r.choice(["3", "many", -1, 2.5, None])})
    return configs


def _reference(configs):
    applied, rejected = [], []
    for i, cfg in enumerate(configs):
        try:
            for key in ("name", "replicas"):
                if key not in cfg:
                    raise MissingKeyError(key)
            if not isinstance(cfg["replicas"], int) or cfg["replicas"] < 0:
                raise BadValueError(cfg["replicas"])
            applied.append(cfg["name"])
        except ConfigError as err:
            rejected.append((i, type(err).__name__))
    return applied, rejected


def test_solve():
    r = rng()
    for _ in range(4):
        configs = _gen(r)
        assert solve([dict(c) for c in configs]) == _reference(configs)
