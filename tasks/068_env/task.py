TRUTHY = {"1", "true", "yes", "on"}      # given — do not edit


def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import os

from _lib import rng

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
