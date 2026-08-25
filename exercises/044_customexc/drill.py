class ConfigError(Exception):
    """Base class: anything wrong with a config. Given — do not edit."""


class MissingKeyError(ConfigError):
    """A required key is absent."""


class BadValueError(ConfigError):
    """A key is present but its value is unusable."""


def solve(configs):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


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
