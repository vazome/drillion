from collections.abc import Callable


def solve(urls: list[str], get: Callable[..., int], timeout: float,
          max_workers: int):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    hosts = r.sample(["alpha", "bravo", "charlie", "delta", "echo", "foxtrot",
                      "golf", "hotel"], r.randint(4, 8))
    urls = [f"http://{h}.svc.local/health" for h in hosts]
    timeout = r.choice([0.5, 1.0, 2.0, 5.0])
    plan = {}
    for url in urls:
        roll = r.random()
        if roll < 0.55:
            plan[url] = ("status", r.choice([200, 200, 204, 299]))
        elif roll < 0.75:
            plan[url] = ("status", r.choice([301, 404, 429, 500, 503]))
        elif roll < 0.9:
            plan[url] = ("slow", r.choice([0.5, 1.0, 2.0, 5.0, 10.0]))
        else:
            plan[url] = ("dead", None)

    def get(url, timeout):
        """Fake client. No sockets, no sleeping, same failure modes."""
        kind, value = plan[url]
        if kind == "dead":
            raise ConnectionError(f"no route to host: {url}")
        if kind == "slow":
            if value > timeout:
                raise TimeoutError(f"{url} did not answer within {timeout}s")
            return 200
        return value

    return urls, get, timeout, r.randint(2, 6)


def _reference(urls, get, timeout, max_workers):
    from concurrent.futures import ThreadPoolExecutor

    def one(url):
        try:
            status = get(url, timeout=timeout)
        except Exception:  # noqa: BLE001 — any failure is 'error'
            return url, "error"
        return url, "healthy" if 200 <= status < 300 else "unhealthy"

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        return dict(pool.map(one, urls))


def test_solve():
    r = rng()
    for _ in range(4):
        urls, get, timeout, max_workers = _gen(r)
        assert (solve(list(urls), get, timeout, max_workers)
                == _reference(urls, get, timeout, max_workers))
