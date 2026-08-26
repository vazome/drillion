---
title: ThreadPoolExecutor — CSV rows fanned out over a thread pool
difficulty: medium
tier: core
minutes: 30
prereqs: [30]
tags: [threadpoolexecutor]
---
# ThreadPoolExecutor — CSV rows fanned out over a thread pool

*Whole-task task: a batch of hosts, a thread pool, and the order kept.*

Combines topics 32 (csv), 54 (ThreadPoolExecutor), 43 (except).

## Why
An inventory file lists every host in a fleet, and the ops team needs to run one slow network call against each of them, say to fetch its CPU load. Done one at a time, two hundred hosts at two seconds each is almost seven minutes. Done at the same time, it is seconds. The report must still come back in the file's order so it lines up with the inventory, and one unreachable host must not stop the rest.

## You get
`text` — the whole inventory file as one string, in CSV form with a header line, like `"host,cpu,zone"` on the first line and `"web-1,500,a"` on the next.

`work` — a function you call with one row (a dictionary like `{"host": "web-1", "cpu": "500", "zone": "a"}`). It takes a moment, then returns a value or raises an error. The test hands you a fake that pretends to be slow and pretends some hosts are down; nothing real is contacted.

`max_workers` — a whole number, like `4`: how many calls may run at the same time.

## You return
a list with one dictionary per row, in the same order as the file. Each has `"host"`, `"status"` (`"ok"` or `"error"`) and `"result"` (the value work returned, or the error message as text).

## Rules
An inventory file lists hosts. Run one slow call per host, in parallel.

`text` is CSV with a header. `work` is the function you were handed: `work(row)` takes one row as a dict and returns a value, or raises.

```text
host,cpu,zone
web-1,500,a
web-2,250,b
```

```python
solve(text, work, 4)
# -> [{"host": "web-1", "status": "ok",    "result": 1000},
#     {"host": "web-2", "status": "error", "result": "unreachable: web-2"}]
```

Rules:

- Parse with the `csv` module and `io.StringIO`. No real files.
- Run every row through a `ThreadPoolExecutor` with `max_workers` threads. Each `work()` call blocks for a while, the way a real API call does, so serial code costs the sum of them.
- If `work` raises, that row gets status `"error"` and result `str(exc)`. One dead host must not sink the batch.

> [!WARNING]
> Results come back in the SAME order as the rows in the file, no matter what order the calls finish in. The generator here is rigged so the first row finishes last.

> [!TIP]
> Fan-out with ordered results is the standard "make it faster" follow-up in a screen. Narrate why the order survives while you write it.

## Hints
### Hint 1
Two halves, and they do not interleave: parse the whole file into rows first, then fan the rows out. Once you are inside the pool the trap is collecting results as they land — the fastest host is not the first row, and as_completed hands you whatever finished, not what you asked for first.
### Hint 2
list(csv.DictReader(io.StringIO(text))) gets the rows. Write a small function that takes one row, wraps work(row) in try/except Exception, and returns the dict either way — put the try around the one call that can fail, not around the whole loop. Then `with ThreadPoolExecutor(max_workers=max_workers) as pool:` and list(pool.map(fn, rows)). map yields in input order, and leaving the with block waits for every thread.
### Hint 3
Different data, slowest first so the order is visibly not the finish order:

```python
import time
from concurrent.futures import ThreadPoolExecutor
def slow(n):
    time.sleep(0.05 - n * 0.01)
    return n * n
with ThreadPoolExecutor(max_workers=4) as pool:
    print(list(pool.map(slow, [1, 2, 3, 4])))   # [1, 4, 9, 16]
```

4 finished first and still came out last. That is the whole reason to reach for map here.
