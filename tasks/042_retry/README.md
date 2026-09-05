---
title: retry — exponential backoff with jitter, by hand
difficulty: medium
tier: core
minutes: 20
prereqs: [36]
tags: [errors]
---
# retry — exponential backoff with jitter, by hand

*Retry with backoff and jitter — the standard whiteboard ask for SRE screens.*

## Why
You run a nightly job that pushes metrics to a monitoring vendor's API. Their service sometimes refuses a request for a second or two (a restart, a network blip) and is then fine again. If your job gives up on the first failure, the on-call engineer gets paged at 3am for nothing; if it retries instantly and forever, it hammers a struggling service and makes the outage worse. The team lead asks for one helper every script can use: try again, wait a bit longer each time, add a little randomness so a thousand clients do not all retry in the same second, and give up after a fixed number of tries.

## You get
`call` — a function that takes no arguments. Calling it either returns a result or fails with an error. The test hands in a stand-in that fails a set number of times and then succeeds (or never succeeds); nothing real is contacted.

`sleep` — a function you call with a number of seconds to wait. The test hands in a fake that only writes the number down; no real waiting.

`rand` — a function with no arguments that returns a number between 0 and 1. The test hands in a fake with known values so the result is predictable.

`max_attempts` — a whole number like 4: the most times you may try.

`base` — a number like 1.0: the starting wait, in seconds.

## You return
whatever `call()` returned the first time it worked. If every attempt fails, return nothing: let the last error escape so the caller sees it.

## Rules
Call `call()` until it succeeds, backing off between failures.

- Try `call()` at most `max_attempts` times. On success, return its value immediately.
- If `call()` raises any `Exception` and attempts remain, wait and retry. For failure number `i` (0-based: first failure is `i=0`):

  ```python
  delay = base * (2 ** i) * (1 + rand())
  ```

  Wait by calling `sleep(delay)` — never `time.sleep`.
- If the last allowed attempt fails, re-raise that exception (a bare `raise` inside the except block).

`rand()` returns a float in `[0, 1)`, so each delay lands somewhere between `base * 2**i` and `base * 2**(i+1)`. That randomness is the jitter: it stops a thousand retrying clients from hammering the server in lockstep.

```python
# base=1, rand() returns 0.5 then 0.25, call fails twice then returns 7
solve(call, sleep, rand, max_attempts=4, base=1)
# -> sleeps 1.5, then 2.5, calls 3 times, returns 7
```

Why `sleep` and `rand` are parameters instead of imports: the test passes a fake sleep that just records the delay, and a fake rand with known values. No real waiting, fully deterministic. This is dependency injection, and "inject the clock so tests control time" is itself an interview answer worth saying out loud.

## Hints
### Hint 1
Three moving parts: a loop over attempt numbers, a try/except around one call, and the decision inside except — is this the last attempt (give up, re-raise) or not (sleep, go around again). Get that skeleton before any delay math.
### Hint 2
for attempt in range(max_attempts): try to return call(); except Exception: if attempt == max_attempts - 1, a bare `raise` re-raises the current exception; otherwise sleep(base * 2 ** attempt * (1 + rand())). Returning from inside try exits the loop on success.
### Hint 3
Different data — retrying a flaky lookup, 2 failures allowed:

```python
def lookup():
    raise OSError('dns')

waits = []
for attempt in range(2):
    try:
        result = lookup()
        break
    except OSError:
        if attempt == 1:
            raise
        waits.append(0.5 * 2 ** attempt)
# waits == [0.5], then the second failure re-raises OSError
```

Yours returns instead of break, and multiplies in (1 + rand()) for jitter.
