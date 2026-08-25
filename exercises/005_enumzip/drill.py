def solve(hosts, ips):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    pool = ["web", "db", "cache", "auth", "queue", "cron", "proxy"]
    hosts = r.sample(pool, r.randint(3, 6))
    ips = [f"10.0.{r.randint(0, 9)}.{r.randint(1, 99)}" for _ in hosts]
    return hosts, ips


def _reference(hosts, ips):
    return [f"{i}. {h} {ip}"
            for i, (h, ip) in enumerate(zip(hosts, ips), start=1)]


def test_solve():
    r = rng()
    for _ in range(4):
        hosts, ips = _gen(r)
        assert solve(list(hosts), list(ips)) == _reference(hosts, ips)
