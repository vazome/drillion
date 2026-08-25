"""Whole-task drill: health-check a fleet without waiting on it one host at a time.

Combines topics 43 (except), 46 (timeouts), 54 (ThreadPoolExecutor).
"""

from _lib import rng

META = {"topic": 84, "title": "DRILL: health-check a URL list in parallel",
        "tier": 4, "minutes": 25, "prereqs": [43],
        "practices": [43, 46, 54]}


def solve(urls, get, timeout, max_workers):
    """WHY: A company runs dozens of small services, each with a health
    page. Every few minutes a monitor has to ask all of them "are you
    alive?" and produce one verdict per service. Asked one at a time, a
    single frozen host makes the whole round take minutes; asked all at once
    with a time limit on each, it takes seconds. One dead host must not stop
    the report for the others.

    YOU GET: `urls` — a list of web addresses as strings, like
    ["http://a.svc/health", "http://b.svc/health"].

    `get` — a function that fetches one address: you call it as get(url,
    timeout=...) and it returns a status number like 200, or raises an error
    when the host is down or too slow. The test hands you a fake that only
    pretends; no network is used.

    `timeout` — seconds to allow for one fetch, like 2.0. You must pass it
    to get every time.

    `max_workers` — a whole number, like 4: how many fetches may run at the
    same time.

    YOU RETURN: a dictionary mapping each address to one word: "healthy"
    (status 200 to 299), "unhealthy" (any other status) or "error" (the
    fetch raised).

    ─── exact rules ───
    Check every URL and report one verdict each.

    `get` is the injected HTTP client, standing in for requests.get:
    get(url, timeout=...) returns an integer status code, or raises — dead
    host, bad DNS, TimeoutError when the host is slower than the timeout
    you gave it. Return a dict:

        {"http://a.svc/health": "healthy",     # status 200 to 299
         "http://b.svc/health": "unhealthy",   # any other status
         "http://c.svc/health": "error"}       # get raised something

    Rules:
      - Always pass `timeout` through to get. A health check without one is
        how a single wedged host stalls the entire run, and the fake client
        here will not even let you call it without one.
      - Check the URLs concurrently, ThreadPoolExecutor with max_workers
        threads. Waiting on the network is exactly what threads are for.
      - Any exception at all becomes "error". One dead host must not take
        the batch down with it.

    "Now do 200 of them" is the follow-up you are being set up for. Say
    why threads work here even with the GIL — the work is waiting, not
    computing — out loud while you write it.
    """
    raise NotImplementedError


HINTS = [
    ("Build it inside out. Write the function that handles ONE url first: it "
    "has three outcomes, and two of them come out of the same call — a number "
    "you have to classify, or an exception you have to catch. Only once that "
    "is right do you wrap a pool around it. Deciding where the try goes is "
    "the design step: around the one call that can fail, not around the loop."),
    ("def one(url): try status = get(url, timeout=timeout), except Exception "
    "return (url, 'error'), else return (url, 'healthy' if 200 <= status < 300 "
    "else 'unhealthy'). Returning pairs is deliberate — then "
    "`with ThreadPoolExecutor(max_workers=max_workers) as pool:` and "
    "dict(pool.map(one, urls)) builds the whole result in one line. Leaving "
    "the with block waits for every thread to finish."),
    ("Different data, same wiring:\n"
    "    from concurrent.futures import ThreadPoolExecutor\n"
    "    def parse(x):\n"
    "        try:\n"
    "            return x, int(x)\n"
    "        except ValueError:\n"
    "            return x, None\n"
    "    with ThreadPoolExecutor(max_workers=3) as pool:\n"
    "        print(dict(pool.map(parse, ['1', 'two', '3'])))\n"
    "    # {'1': 1, 'two': None, '3': 3}\n"
    "The per-item function swallows its own failure, so the pool never sees "
    "an exception and the batch always completes."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

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
