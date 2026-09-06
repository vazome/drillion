---
title: concurrency — health-check a URL list in parallel
difficulty: medium
tier: advanced
minutes: 25
prereqs: [73]
tags: [concurrency]
---
# concurrency — health-check a URL list in parallel

*Whole-task task: health-check a fleet without waiting on it one host at a time.*

Combines topics 43 (except), 46 (timeouts), 54 (ThreadPoolExecutor).

## Read first
- [ThreadPoolExecutor](https://devdocs.io/python~3.14/library/concurrent.futures#threadpoolexecutor) — concurrent checks, and one slow host not stalling the rest

## Why
A company runs dozens of small services, each with a health page. Every few minutes a monitor has to ask all of them "are you alive?" and produce one verdict per service. Asked one at a time, a single frozen host makes the whole round take minutes; asked all at once with a time limit on each, it takes seconds. One dead host must not stop the report for the others.

## You get
`urls` — a list of web addresses as strings, like `["http://a.svc/health", "http://b.svc/health"]`.

`get` — a function that fetches one address: you call it as `get(url, timeout=...)` and it returns a status number like `200`, or raises an error when the host is down or too slow. The test hands you a fake that only pretends; no network is used.

`timeout` — seconds to allow for one fetch, like `2.0`. You must pass it to `get` every time.

`max_workers` — a whole number, like `4`: how many fetches may run at the same time.

## You return
a dictionary mapping each address to one word: `"healthy"` (status 200 to 299), `"unhealthy"` (any other status) or `"error"` (the fetch raised).

## Rules
Check every URL and report one verdict each.

`get` is the injected HTTP client, standing in for `requests.get`: `get(url, timeout=...)` returns an integer status code, or raises — dead host, bad DNS, `TimeoutError` when the host is slower than the timeout you gave it. Return a dict:

```python
solve(urls, get, timeout, max_workers)
# -> {"http://a.svc/health": "healthy",     # status 200 to 299
#     "http://b.svc/health": "unhealthy",   # any other status
#     "http://c.svc/health": "error"}       # get raised something
```

| verdict | when you report it |
| --- | --- |
| `"healthy"` | `get` returned a status from 200 to 299 |
| `"unhealthy"` | `get` returned any other status |
| `"error"` | `get` raised anything at all |

Rules:

- Check the URLs concurrently, `ThreadPoolExecutor` with `max_workers` threads. Waiting on the network is exactly what threads are for.
- Any exception at all becomes `"error"`. One dead host must not take the batch down with it.

> [!WARNING]
> Always pass `timeout` through to `get`. A health check without one is how a single wedged host stalls the entire run, and the fake client here will not even let you call it without one.

> [!TIP]
> "Now do 200 of them" is the follow-up you are being set up for. Say why threads work here even with the GIL — the work is waiting, not computing — out loud while you write it.

## Hints
### Hint 1
Build it inside out. Write the function that handles ONE url first: it has three outcomes, and two of them come out of the same call — a number you have to classify, or an exception you have to catch. Only once that is right do you wrap a pool around it. Deciding where the try goes is the design step: around the one call that can fail, not around the loop.
### Hint 2
def one(url): try status = get(url, timeout=timeout), except Exception return (url, 'error'), else return (url, 'healthy' if 200 <= status < 300 else 'unhealthy'). Returning pairs is deliberate — then `with ThreadPoolExecutor(max_workers=max_workers) as pool:` and dict(pool.map(one, urls)) builds the whole result in one line. Leaving the with block waits for every thread to finish.
### Hint 3
Different data, same wiring:

```python
from concurrent.futures import ThreadPoolExecutor
def parse(x):
    try:
        return x, int(x)
    except ValueError:
        return x, None
with ThreadPoolExecutor(max_workers=3) as pool:
    print(dict(pool.map(parse, ['1', 'two', '3'])))
# {'1': 1, 'two': None, '3': 3}
```

The per-item function swallows its own failure, so the pool never sees an exception and the batch always completes.
