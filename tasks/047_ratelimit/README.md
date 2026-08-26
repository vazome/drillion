---
title: rate limits — honour 429 and Retry-After
difficulty: medium
tier: core
minutes: 15
prereqs: [42]
tags: [http]
---
# rate limits — honour 429 and Retry-After

*A 429 is the server asking you to slow down; ignoring it is how you get an IP ban.*

## Why
A cleanup script calls a vendor's API hundreds of times in a row. The vendor caps how many calls per minute you may make; go over and it answers with status 429, which means "too many requests, come back in N seconds", instead of doing the work. A script that ignores that and keeps firing gets the whole company's API key blocked. The team lead wants a helper that waits exactly as long as the server asks, uses a sensible default when the server names no time, and stops after a fixed number of tries. It must NOT retry other errors: a 500 or a 403 will not get better by waiting.

## You get
`request` — a function with no arguments; each call makes one attempt and returns a dict shaped like a web answer, e.g. `{"status": 429, "headers": {"Retry-After": "3"}}` or `{"status": 200, "headers": {}, "body": {"items": 12}}`. The test hands in a stand-in that replays a scripted list of answers; no real server is contacted.

`sleep` — a function you call with a number of seconds. The test's fake only records the number; no real waiting.

`max_attempts` — a whole number like 3: the most tries allowed.

`default_wait` — a number like 1.0: seconds to wait when the answer carries no `Retry-After` value.

## You return
the `"body"` part of the first answer with status 200. If an attempt returns any status other than 200 or 429, or every attempt is a 429, do not return anything: raise `RuntimeError`.

## Rules
Call `request()` until it succeeds, waiting when told to.

`request()` returns a dict shaped like an HTTP response:

```python
{"status": 200, "headers": {}, "body": {"items": 12}}
{"status": 429, "headers": {"Retry-After": "3"}}
{"status": 500, "headers": {}}
```

In this order, for each of at most `max_attempts` attempts:

| Response | What you do |
| --- | --- |
| status 200 | return `resp["body"]` straight away |
| status is not 429 | raise `RuntimeError`. Do not retry, do not sleep. This task only retries the one status the server asked you to |
| status 429, attempts left | work out the wait and `sleep(wait)` |
| status 429, no attempts left | raise `RuntimeError` |

The wait is `float(resp["headers"]["Retry-After"])` when that header is there, and `default_wait` when it is not. Header values arrive as strings, always — `"3"` is not `3`.

```python
# max_attempts=3, default_wait=1.0
# attempt 1 -> {"status": 429, "headers": {"Retry-After": "2"}}
# attempt 2 -> {"status": 429, "headers": {}}
# attempt 3 -> {"status": 200, "headers": {}, "body": {"items": 12}}
solve(request, sleep, max_attempts=3, default_wait=1.0)
# -> sleep(2.0), sleep(1.0), returns {"items": 12}
```

`sleep` is a parameter, not `time.sleep`, for the same reason as everywhere else: the test hands in a fake that records the delay instead of burning it. Never sleep before the first call, and never after the last failure — a wait nobody is waiting on is just a slower error.

## Hints
### Hint 1
Each response has three possible endings, not two: done, wait and go round again, or give up right now. Sort out which status leads to which before writing the loop. The other easy miss is the header type — it is text off the wire, so it needs converting before sleep sees it.
### Hint 2
for attempt in range(max_attempts): resp = request(), then the status checks in the order the spec lists them. The missing-header case is resp['headers'].get('Retry-After', default_wait) wrapped in float(), which happily takes either a string or the number you defaulted to. The last-attempt test is attempt == max_attempts - 1, the same shape as in the retry task.
### Hint 3
Different data — a queue API that answers with a wait hint:

```python
replies = [{'code': 503, 'hdr': {'Retry-After': '4'}},
           {'code': 200, 'hdr': {}, 'body': 'done'}]
waits = []
for reply in replies:
    if reply['code'] == 200:
        print(reply['body'])      # done
        break
    waits.append(float(reply['hdr'].get('Retry-After', 1)))
print(waits)                      # [4.0]
```

Yours calls request() once per attempt instead of reading a list, and raises RuntimeError on the two paths that are not a 200.
