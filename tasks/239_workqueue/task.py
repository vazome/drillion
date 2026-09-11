import queue
import threading
import time

_RAN_ON = set()


def checksum(job):
    """The slow work. Records the thread it ran on so the grader can see the hand-off happened."""
    _RAN_ON.add(threading.current_thread().name)
    time.sleep(0.002)
    return (job * 2654435761) % 1000003


def solve(jobs, capacity, workers):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    capacity, workers = r.randint(1, 3), r.randint(2, 4)
    # more jobs than either bound, so the bounded put really does block partway through
    jobs = r.sample(range(1000), max(capacity, workers) + r.randint(2, 9))
    return jobs, capacity, workers


def _reference(jobs, capacity, workers):
    work, done = queue.Queue(maxsize=capacity), queue.Queue()

    def worker():
        while True:
            job = work.get()
            done.put((job, checksum(job)))
            work.task_done()

    for _ in range(workers):
        threading.Thread(target=worker, daemon=True).start()
    for job in jobs:
        work.put(job)
    work.join()
    out = {}
    while not done.empty():
        job, value = done.get()
        out[job] = value
    return out


def test_solve():
    r = rng()
    for _ in range(5):
        jobs, capacity, workers = _gen(r)
        _RAN_ON.clear()
        got = solve(jobs, capacity, workers)
        ran_on = set(_RAN_ON)
        _RAN_ON.clear()
        want = _reference(jobs, capacity, workers)
        assert got == want, f"for jobs={jobs} capacity={capacity} workers={workers}: got {got}"
        assert len(got) == len(jobs), f"one entry per job: {len(jobs)} jobs, {len(got)} results"
        assert "MainThread" not in ran_on, "the work belongs to the worker threads, not the main one"
        assert 2 <= len(ran_on) <= workers, f"{workers} workers asked for, {len(ran_on)} threads ran the work"
