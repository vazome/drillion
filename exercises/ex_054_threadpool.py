"""200 API calls at 200ms each is 40 seconds one at a time, or under a second in a pool."""

import threading
import time
from concurrent.futures import ThreadPoolExecutor

from _lib import rng

META = {"topic": 54, "title": "ThreadPoolExecutor — fan out, keep the order",
        "tier": 3, "minutes": 12, "prereqs": []}


def solve(work, items, workers):
    """WHY: A morning report needs to ask 200 hosts for their status. Each ask
    is mostly waiting on the network, about 200ms; done one after another
    that is 40 seconds, done a few at once it is under a second. But the
    report must list the rows in the same order as the host list, and you
    must not fire all 200 at once because the network team set a limit. The
    ask: run the checks a fixed number at a time and hand back the answers
    in the original order.

    YOU GET: `work` — a function that takes one item and returns a result.
    The test hands in a stand-in that pauses briefly and notes which thread
    it ran on; nothing real is contacted.
    `items` — a list of items, like ["api-01", "db-07"].
    `workers` — a whole number like 3: how many may run at the same time.

    YOU RETURN: a real list of results, one per item, in the same order as
    `items`.

    ─── exact rules ───
    Run work(item) for every item, at most `workers` at a time.

    Return a list of the results in the SAME ORDER as items, no matter
    which call finished first.

        work = len, items = ["ab", "c", "defg"], workers = 2
        ->  [2, 1, 4]

    Rules:
      - Use a ThreadPoolExecutor with max_workers=workers. The test
        checks that work never ran on the main thread, so a list
        comprehension gets the values right and still fails.
      - Return a real list. executor.map hands back a lazy iterator,
        and it has to be drained before the pool shuts down.
      - work is pure and safe to call from several threads at once.

    map vs as_completed, since this is the follow-up question:
    executor.map keeps input order for free and is the right default
    when you want all the answers. as_completed yields each future the
    moment it finishes, which is what you want for a progress bar, for
    bailing out on the first failure, or when one slow call should not
    hold up the other 199 — but then the order is arrival order, so you
    carry the index yourself (usually a {future: item} dict) if you
    need to line results back up.
    """
    raise NotImplementedError


HINTS = [
    ("The pool is a context manager, and leaving the `with` block waits for "
    "everything to finish — that is the join you would otherwise write by "
    "hand. Settle one question before you write anything: do you need the "
    "results in input order, or as soon as each one lands. That choice picks "
    "the API for you."),
    ("from concurrent.futures import ThreadPoolExecutor. Then `with "
    "ThreadPoolExecutor(max_workers=workers) as pool:` and pool.map(work, "
    "items) — same argument order as the builtin map, results in input "
    "order. It is lazy, so wrap it in list() while you are still inside the "
    "with block."),
    ("Different data — squaring numbers, both ways:\n"
    "    from concurrent.futures import ThreadPoolExecutor, as_completed\n"
    "    def sq(n):\n"
    "        return n * n\n"
    "\n"
    "    with ThreadPoolExecutor(max_workers=3) as pool:\n"
    "        print(list(pool.map(sq, [1, 2, 3])))       # [1, 4, 9], always\n"
    "\n"
    "    with ThreadPoolExecutor(max_workers=3) as pool:\n"
    "        futures = [pool.submit(sq, n) for n in [1, 2, 3]]\n"
    "        print(sorted(f.result() for f in as_completed(futures)))\n"
    "        # [1, 4, 9] only because of the sorted() — arrival order is not\n"
    "        # promised\n"
    "map is the short road when input order is what you want."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

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
