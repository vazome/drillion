def solve(text, work, max_workers):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    import time
    names = ["web", "api", "db", "cache", "edge", "batch", "mail", "auth"]
    hosts = [f"{names[i]}-{i + 1}" for i in range(r.randint(3, len(names)))]
    text = "host,cpu,zone\n" + "\n".join(
        f"{h},{r.choice([100, 250, 500, 750])},{r.choice(['a', 'b', 'c'])}"
        for h in hosts)
    down = set(r.sample(hosts, r.randint(0, min(2, len(hosts)))))
    # first row sleeps longest, so finish order is the reverse of file order
    delays = {h: 0.002 * (len(hosts) - i) for i, h in enumerate(hosts)}

    def work(row):
        time.sleep(delays[row["host"]])
        if row["host"] in down:
            raise ConnectionError(f"unreachable: {row['host']}")
        return int(row["cpu"]) * 2

    return text, work, r.randint(2, 6)


def _reference(text, work, max_workers):
    import csv
    import io
    from concurrent.futures import ThreadPoolExecutor

    rows = list(csv.DictReader(io.StringIO(text)))

    def one(row):
        try:
            return {"host": row["host"], "status": "ok", "result": work(row)}
        except Exception as exc:  # noqa: BLE001 — record any failure
            return {"host": row["host"], "status": "error", "result": str(exc)}

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        return list(pool.map(one, rows))


def test_solve():
    r = rng()
    for _ in range(3):
        text, work, max_workers = _gen(r)
        assert solve(text, work, max_workers) == _reference(text, work, max_workers)
