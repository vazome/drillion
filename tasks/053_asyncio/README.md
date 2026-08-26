---
title: asyncio — gather, don't queue
difficulty: medium
tier: advanced
track: rsample
minutes: 20
prereqs: [52]
tags: [concurrency, asyncio]
---
# asyncio — gather, don't queue

*asyncio — run many waits at once instead of one after another.*

## Why
A status page must fetch the state of a dozen services before it can render. Each fetch is mostly waiting on the network. If the code waits for service 1 to answer before it even asks service 2, the page takes the sum of all the waits; asking everyone at once and then collecting the answers takes only the slowest single wait. The team's code is written in Python's async style, and you are asked to write the "ask everyone at once, collect the answers in order" helper.

## You get
nothing — you build the thing from scratch. Your `solve()` returns a helper; the test then calls that helper with its own `worker` (an async stand-in that pauses and returns a value) and a list of job ids. No real service is contacted.

## You return
the helper function itself (an async function that takes a worker and a list of jobs), not the result of running it. When the test runs your helper, every job must start before any job finishes, and the results must come back in the same order as the jobs.

## Rules
Return an ASYNC function `fetch_all(worker, jobs)` where:

- `worker` is an async function: `await worker(job)` returns a result
- `jobs` is a list of job ids

`fetch_all` must start ALL jobs concurrently and return their results in the same order as `jobs`.

```python
async def worker(j): ...
await fetch_all(worker, [3, 1, 2])   # -> [r3, r1, r2]
```

> [!WARNING]
> The test fails a version that awaits jobs one at a time in a loop — that is just a slow for-loop wearing async syntax. One asyncio function does "launch all, wait for all, keep order" in a single call.

Return the function itself (not a coroutine): `return fetch_all`.

## Read first
- [Async IO in Python: a complete walkthrough](https://realpython.com/async-io-python/) — THE asyncio walkthrough; read 'Async IO Explained' and 'The asyncio Package' before anything below
- [asyncio.gather](https://docs.python.org/3/library/asyncio-task.html#asyncio.gather) — hand it many awaitables; it runs them concurrently and keeps argument order

> [!NOTE]
> **Take-home:** `loadtest.py`, your concurrency test

## Hints
### Hint 1
`await worker(j)` inside a plain for-loop finishes job 1 completely before job 2 even starts — sequential, exactly what async exists to avoid. You need to hand ALL the coroutines to the event loop at once.
### Hint 2
Build the list of coroutine objects first — calling worker(j) WITHOUT await creates one without running it. Then look up asyncio.gather: it takes many awaitables, runs them concurrently, and returns results in argument order.
### Hint 3
Different data, same shape:

```python
import asyncio
async def shout(word):
    await asyncio.sleep(0.01)
    return word.upper()
async def all_shouts(words):
    return await asyncio.gather(*(shout(w) for w in words))
print(asyncio.run(all_shouts(['hi', 'yo'])))   # ['HI', 'YO']
```

The * unpacks the coroutines into gather's arguments.
