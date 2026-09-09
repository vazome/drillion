def solve(config: dict, overrides: dict):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _reference(config, overrides):
    from copy import deepcopy

    result = deepcopy(config)
    service = result["service"]
    service["replicas"] = overrides.get("replicas", service["replicas"])
    service["owner"] = overrides.get("owner", service.get("owner", "unassigned"))
    service["labels"].extend(overrides.get("labels", []))
    return result


def _gen(r):
    config = {"service": {
        "replicas": r.randint(1, 5),
        "labels": r.sample(["prod", "eu", "api", "critical"], r.randint(0, 2)),
    }}
    if r.random() < 0.5:
        config["service"]["owner"] = r.choice(["core", "infra"])
    overrides = {}
    if r.random() < 0.6:
        overrides["replicas"] = r.randint(0, 8)
    if r.random() < 0.5:
        overrides["owner"] = r.choice(["data", "web"])
    if r.random() < 0.7:
        overrides["labels"] = r.sample(["canary", "urgent"], r.randint(0, 2))
    return config, overrides


def test_solve():
    config = {"service": {"replicas": 2, "labels": ["prod"]}}
    got = solve(config, {"replicas": 0, "labels": ["canary"]})
    assert got == {"service": {"replicas": 0, "owner": "unassigned",
                               "labels": ["prod", "canary"]}}
    assert config == {"service": {"replicas": 2, "labels": ["prod"]}}
    got["service"]["labels"].append("changed")
    assert config["service"]["labels"] == ["prod"], "the nested list must be copied deeply"

    r = rng()
    for _ in range(6):
        config, overrides = _gen(r)
        before = {"service": {key: list(value) if isinstance(value, list) else value
                              for key, value in config["service"].items()}}
        assert solve(config, overrides) == _reference(config, overrides)
        assert config == before
