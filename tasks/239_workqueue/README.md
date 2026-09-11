---
title: queue.Queue — a bounded hand-off between the thread making work and the threads doing it
difficulty: hard
tier: advanced
minutes: 25
prereqs: [88]
tags: [concurrency, stdlib-ops]
---
# queue.Queue — a bounded hand-off between the thread making work and the threads doing it

*A queue with a `maxsize` is a back-pressure valve, and `task_done` plus `join` is how the producer finds out the work is finished without watching a clock.*

## Read first
- [`queue.Queue`](https://devdocs.io/python~3.14/library/queue#queue.Queue) — `maxsize`, and what `put` does when the queue is full
- [`Queue.task_done`](https://devdocs.io/python~3.14/library/queue#queue.Queue.task_done) and [`Queue.join`](https://devdocs.io/python~3.14/library/queue#queue.Queue.join) — the counter that says how much work is still outstanding
- [`threading.Thread`](https://devdocs.io/python~3.14/library/threading#threading.Thread) — `target`, `daemon` and `start`

## Why
A batch job has forty thousand records to hash and four workers to hash them with. Reading the records is fast and hashing them is not, so a producer that hands work over as fast as it can read holds the entire batch in memory while the workers plod through the front of it — fine on the test file, an out-of-memory kill on the real one. A queue with a `maxsize` fixes that by making `put` wait: the reader runs exactly as far ahead as the workers let it, and the size of the batch stops mattering. The other half is knowing when to stop. Sleeping for a guessed number of seconds is either wrong or slow, and usually both, and a queue already counts the work nobody has finished yet.

## You get
- `jobs`, a list of distinct ints. There are always more of them than `capacity`.
- `capacity`, the most items the queue may hold at once.
- `workers`, how many worker threads to run. Always at least two.

`checksum(job)` is given to you above `solve`. It is the slow work, and it records which thread called it.

## You return
a dict mapping each job to its `checksum(job)`, with an entry for every job in `jobs`.

## Rules
- The work queue is bounded: `queue.Queue(maxsize=capacity)`, and `capacity` is smaller than `len(jobs)`. That means the thread doing the putting will block partway through, so the workers have to be running **before** you start putting — a producer that fills the whole queue first never gets to start them.
- Run exactly `workers` threads, and let them do the work. The grader can see which threads called `checksum`: it counts them, and a solution that hashes anything on the main thread or starts more threads than it was asked for fails on that, however correct the numbers are.
- Each worker calls `task_done()` once per item it took, and the main thread waits with `join()`. No `sleep`, no polling, no guessing.
- Do not decide a worker is finished because the queue looks empty. `empty()` is true every time the workers are briefly faster than the producer, which is most of the time.
- Collect the results somewhere thread-safe. A second `Queue` is the simplest answer and needs no lock.

```python
solve([3, 4, 5, 6], capacity=2, workers=2)
# -> {3: ..., 4: ..., 5: ..., 6: ...}   the same four checksums, whatever order they were computed in
```

> [!WARNING]
> `task_done()` inside a worker that also raises means `join()` never returns and the run hangs rather than fails. Put it where it happens whatever the item turns out to be.

> [!NOTE]
> Daemon threads are the reason no shutdown signal is needed here: the workers loop on `get()` forever, and once `join()` says every item has been accounted for, the process is free to leave them blocked and exit. Send each result before calling `task_done` for that item, or `join()` can return a moment before the last result has been filed.

## Hints
### Hint 1
Order of operations in `solve`: make both queues, start the workers, put the jobs, `join`, drain the results. Nothing else.
### Hint 2
A worker is `while True: job = work.get()` — do the work, put the result on the other queue, then `work.task_done()`. The infinite loop is not a leak: `threading.Thread(target=..., daemon=True)` means it does not hold the interpreter open.
### Hint 3
The shape, without the results:

```python
import queue
import threading

work = queue.Queue(maxsize=2)
done = queue.Queue()


def worker():
    while True:
        item = work.get()
        done.put(item * item)
        work.task_done()


for _ in range(3):
    threading.Thread(target=worker, daemon=True).start()

for item in range(10):
    work.put(item)          # blocks at two outstanding items until a worker takes one

work.join()                 # returns when task_done has been called ten times
squares = []
while not done.empty():      # safe here and nowhere else: every worker has finished by now
    squares.append(done.get())
```
