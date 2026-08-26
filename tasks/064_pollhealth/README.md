---
title: retry loops — poll until healthy, back off, exit code
difficulty: hard
tier: core
minutes: 30
prereqs: [43]
tags: [retry-loops]
---
# retry loops — poll until healthy, back off, exit code

*Whole-task task: wait for the deploy to come up, or fail the pipeline.*

Combines topics 46 (deadlines), 45 (backoff), 39 (exit codes).

## Why
A deploy pipeline has just pushed a new version of a service. Before the pipeline moves to the next stage it has to wait until the service says it is healthy. Waiting forever is not allowed, so there is a time limit; checking every millisecond is wasteful, so the gaps between checks grow. If the service never comes up, the pipeline has to stop with a failure code so nobody ships on top of a broken release.

## You get
`check` — a function you call with no arguments; it answers "is the service up?" with `True` or `False`. The test hands you a fake one that says no a few times and then yes; nothing real is contacted.

`now` — a function with no arguments that returns the current time as a number of seconds, like `1234.0`.

`sleep` — a function you call with a number of seconds to wait. The test hands you a fake clock: `sleep` only moves the fake time forward, so nothing really waits. Do not use Python's real time module here.

`timeout` — total seconds you are allowed to keep trying, like `10`.

`interval` — seconds to wait after the first failed check, like `1`.

`max_interval` — the longest gap you are ever allowed to wait, like `4`.

## You return
a dictionary with three keys: `"exit_code"` (0 for healthy, 1 for gave up), `"attempts"` (how many times you called check) and `"elapsed"` (how many seconds of fake time passed).

## Rules
A deploy just went out. Wait for it to report healthy, or give up.

`check()` returns something truthy when the service is up. `now()` and `sleep()` are the clock, handed in so the test can replay hours in no time.

> [!WARNING]
> Never import `time` here. The clock is the one that was handed to you.

Rules, exactly:

- Read the clock once at the top: `start = now()`, and the deadline is `start + timeout`.
- While `now()` is before the deadline: call `check()`. Truthy means done. Otherwise `sleep(wait)`, then double wait, capped at `max_interval`. The first wait is `interval`.
- Return a dict either way:

```python
{"exit_code": 0, "attempts": 3, "elapsed": 3.0}   # healthy
{"exit_code": 1, "attempts": 4, "elapsed": 11.0}  # gave up
```

`exit_code` is 0 for healthy and 1 for the timeout. `attempts` counts `check()` calls. `elapsed` is `now() - start` at the moment you return.

Worked example, `timeout=10`, `interval=1`, `max_interval=4`, check false then false then true:

```text
t=start+0   attempt 1, false, sleep 1  (wait becomes 2)
t=start+1   attempt 2, false, sleep 2  (wait becomes 4)
t=start+3   attempt 3, true
->  {"exit_code": 0, "attempts": 3, "elapsed": 3}
```

Returning the code instead of calling `sys.exit` is what makes this testable; the real script does `sys.exit(result["exit_code"])` at the very bottom, and a non-zero code is what stops the pipeline.

> [!TIP]
> Say that part out loud, it is half of what the question is asking.

## Hints
### Hint 1
Three separate ideas, and mixing them is what makes this hard: a deadline read once at the top, a wait that grows between polls, and an exit code carried out in the return value instead of thrown at the process. Sketch where each of the three lives before you write a line.
### Hint 2
start = now(); deadline = start + timeout; wait = interval; attempts = 0. Loop `while now() < deadline`, bump attempts, call check(), return the success dict on truthy. Otherwise sleep(wait) and then wait = min(wait * 2, max_interval). The code after the loop only runs when the clock ran out, so build the exit_code 1 dict there. Both branches compute elapsed as now() - start.
### Hint 3
Different data — a wait that doubles into a ceiling:

```python
wait, waits = 2, []
for _ in range(5):
    waits.append(wait)
    wait = min(wait * 2, 10)
print(waits)     # [2, 4, 8, 10, 10]
```

The cap matters: without it a long timeout ends with one enormous sleep and you notice the service came up four minutes ago.
