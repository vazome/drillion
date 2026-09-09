from collections.abc import Callable


def solve(chunks: list[list[str]], parse: Callable[[str], tuple[str, float]], max_workers: int):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import threading
import time

from _lib import rng


def _reference(chunks, parse, max_workers):
    from collections import Counter
    from concurrent.futures import ThreadPoolExecutor

    def summarize(lines):
        parsed = [parse(line) for line in lines]
        return Counter(level for level, _ in parsed), max((duration for _, duration in parsed), default=0)

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        summaries = list(pool.map(summarize, chunks))
    levels = Counter()
    slowest = 0
    for counts, duration in summaries:
        levels.update(counts)
        slowest = max(slowest, duration)
    return {"levels": dict(sorted(levels.items())), "slowest": slowest}


def _parser(state):
    lock = threading.Lock()

    def parse(line):
        with lock:
            state["active"] += 1
            state["peak"] = max(state["peak"], state["active"])
        time.sleep(0.003)
        level, duration = line.split()
        with lock:
            state["active"] -= 1
        return level, float(duration)

    return parse


def test_solve():
    chunks = [["INFO 0.1", "ERROR 1.2"], ["WARN 0.4"], ["ERROR 2.5", "INFO 0.2"]]
    state = {"active": 0, "peak": 0}
    assert solve(chunks, _parser(state), 3) == {
        "levels": {"ERROR": 2, "INFO": 2, "WARN": 1}, "slowest": 2.5}
    assert state["peak"] > 1, "chunks must be processed by more than one worker"

    r = rng()
    for _ in range(4):
        chunks = [[f"{r.choice(['INFO', 'WARN', 'ERROR'])} {r.randint(1, 90) / 10}"
                   for _ in range(r.randint(1, 4))]
                  for _ in range(r.randint(2, 5))]
        mine_state = {"active": 0, "peak": 0}
        their_state = {"active": 0, "peak": 0}
        workers = r.randint(2, len(chunks))
        assert solve(chunks, _parser(mine_state), workers) == _reference(
            chunks, _parser(their_state), workers)

    empty_state = {"active": 0, "peak": 0}
    assert solve([[], []], _parser(empty_state), 2) == {"levels": {}, "slowest": 0}
    assert empty_state["peak"] == 0
