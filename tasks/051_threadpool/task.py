from collections.abc import Callable


def solve(work: Callable[[str], dict[str, int | str]], items: list[str], workers: int):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import threading
import time
from concurrent.futures import ThreadPoolExecutor

from _lib import rng


def _gen(r):
    kinds = ["api", "web", "db", "cache", "queue", "auth", "cdn"]
    want = r.randint(4, 12)
    seen = set()
    items = []
    while len(items) < want:
        host = f"{r.choice(kinds)}-{r.randint(1, 99):02d}"
        if host not in seen:                 # unique, so a wrong order shows up
            seen.add(host)
            items.append(host)
    return items, r.randint(2, 6)


def _probe():
    """A pure work function, plus a note of whether it ran on the main thread."""
    state = {"main": False}
    lock = threading.Lock()

    def work(host):
        time.sleep(0.002)                    # stands in for a network round trip
        with lock:
            if threading.current_thread() is threading.main_thread():
                state["main"] = True
        return {"host": host, "n": len(host)}

    return work, state


def _reference(work, items, workers):
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(work, items))


def test_solve():
    r = rng()
    for _ in range(3):
        items, workers = _gen(r)

        work, state = _probe()
        got = solve(work, items, workers)
        assert isinstance(got, list), "return a list, not the iterator map gives you"
        assert got == [{"host": h, "n": len(h)} for h in items]
        assert state["main"] is False, "work ran on the main thread — it never reached a pool"

        other, _ = _probe()
        assert got == _reference(other, items, workers)
