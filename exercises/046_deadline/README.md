---
title: deadlines — poll until ready or time out
minutes: 15
prereqs: [43]
tags: [errors]
---
# deadlines — poll until ready or time out

*Any call that can block needs a deadline — waiting forever is an outage.*

## Why
A deploy script has just asked the cloud to start a new database.
The database takes an unknown time to come up: usually a minute,
sometimes five, occasionally never (a quota problem, a typo in the
config). The next step cannot run until it is ready, so the script must
keep looking, pause between looks, and stop with a clear error once a
time budget is used up. A script that waits forever blocks the whole
pipeline and nobody notices until morning.

## You get
`check` — a function with no arguments that answers "is it
ready yet?" with something true or false. The test hands in a stand-in
that says no a few times and then yes (or never says yes).
`now` — a function with no arguments that returns the current time as a
number of seconds. The test hands in a fake clock that starts at 0.
`sleep` — a function you call with a number of seconds. The test's fake
just moves the fake clock forward by that much; no real waiting.
`timeout` — a number like 10: the total seconds you may keep looking.
`interval` — a number like 4: how many seconds to pause between looks.

## You return
a whole number: how many times you called `check` before it
said yes. If the time budget runs out first, do not return anything:
raise the built-in TimeoutError instead.

## Rules
Wait for a resource to become ready, but never wait forever.

Rules, exactly:
  - Compute the deadline once, up front: deadline = now() + timeout.
  - While now() < deadline: call check(). If it returns something truthy,
    return the number of times check was called. Otherwise sleep(interval)
    and loop.
  - If the loop ends without success, raise TimeoutError (the built-in).

```
timeout=10, interval=4, check ready on the 2nd call
->  check at t=0 (no), sleep to t=4, check at t=4 (yes) -> return 2

timeout=10, interval=4, never ready
->  checks at t=0, 4, 8, clock reaches 12 -> raise TimeoutError
```

Real code would use time.monotonic() and time.sleep(). Here they arrive
as parameters, so the test hands in a fake clock where sleep(4) just adds
4 to a number. No real waiting, and the test can assert exactly when you
gave up. Injecting the clock is what makes timeout code testable — say
that in an interview and you sound like you have been paged before.

## Hints
### Hint 1
Two mistakes to avoid: recomputing the deadline inside the loop (it drifts forever) and checking the clock before the first check() (you always get at least one look). Pin down when the clock is read and when you poll.
### Hint 2
One variable for the deadline before the loop, one counter for polls. `while now() < deadline:` then check(), return the counter on truthy, else sleep(interval). After the while, raise TimeoutError — code below a while only runs when its condition went false.
### Hint 3
Different data — waiting for a fake queue to drain, budget 6, step 2:

```python
t = [0]
queue = [3, 1, 0]          # lengths we will see
stop_at = t[0] + 6
looks = 0
while t[0] < stop_at:
    looks += 1
    if queue[looks - 1] == 0:
        print('drained after', looks, 'looks')
        break
    t[0] += 2
else:
    print('gave up')
# drained after 3 looks
```

Yours returns instead of printing, and raises TimeoutError on the give-up path.
