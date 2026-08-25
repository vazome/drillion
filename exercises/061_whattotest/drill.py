def solve(units):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_STEMS = {
    "logic": ["parse_uptime", "pick_replicas", "threshold_breached", "normalise_tag"],
    "wrapper": ["get_object", "put_metric", "list_pods", "read_secret"],
    "config": ["DEFAULTS", "REGIONS", "TIMEOUT_SECONDS", "LOG_FORMAT"],
    "glue": ["run_rollout", "sync_all", "handle_event", "main"],
}


def _gen(r):
    units = []
    for i in range(r.randint(4, 8)):
        kind = r.choice(["logic", "wrapper", "config", "glue", "glue"])
        branches = 0 if kind == "config" else r.randint(0, 4)
        units.append({"name": f"{r.choice(_STEMS[kind])}_{i}",   # _i keeps names unique
                      "kind": kind, "branches": branches})
    return units


def _reference(units):
    decisions = {}
    for u in units:
        if u["kind"] == "logic":
            decisions[u["name"]] = "test"
        elif u["kind"] == "glue":
            decisions[u["name"]] = "test" if u["branches"] >= 2 else "skip"
        else:
            decisions[u["name"]] = "skip"
    return decisions


def test_solve():
    r = rng()
    for _ in range(4):
        units = _gen(r)
        assert solve(units) == _reference(units)
