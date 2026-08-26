def solve(cfg):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    servers = [f"web-{r.randint(1, 8)}" for _ in range(r.randint(1, 3))]
    servers.append(f"db-{r.randint(1, 4)}")
    ports = r.sample([80, 443, 5432, 6379, 8080, 9090], r.randint(2, 4))
    return {"servers": servers, "ports": ports}


def _reference(cfg):
    import copy
    shallow = cfg.copy()                  # new outer dict, SAME inner lists
    deep = copy.deepcopy(cfg)             # fully independent clone
    shallow["servers"].append("web-9")    # leaks into cfg: the list is shared
    shallow["region"] = "eu"              # does not: top level is separate
    deep["ports"].append(9999)            # touches nothing else
    return cfg, shallow, deep


def test_solve():
    import copy
    r = rng()
    for _ in range(4):
        cfg = _gen(r)
        assert solve(copy.deepcopy(cfg)) == _reference(copy.deepcopy(cfg))
