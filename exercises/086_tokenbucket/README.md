---
title: 'DRILL: token-bucket rate limiter with a fake clock'
minutes: 35
prereqs: []
tags: [whole-task]
practices: [14, 46, 47]
---
# DRILL: token-bucket rate limiter with a fake clock

Whole-task drill: a rate limiter you can reason about, with the clock as data.

Combines topics 14 (classes), 46 (clock handling), 47 (idempotency).

## Why
A public API gets more requests than it can handle, so it must
let a steady stream through and turn the rest away. The standard way is
a "token bucket": the bucket holds a few tokens, each accepted request
spends one, and tokens trickle back in over time. Clients also retry
requests that already went through, and a retry must not be charged
twice, or a flaky network eats a customer's whole allowance.

## You get
`requests` — a list of pairs (time in seconds, request id), in
time order, like [(0, "a"), (0, "b"), (2, "d")].

`capacity` — a whole number, like 2: the most tokens the bucket can
hold.

`rate` — a number, like 1: how many tokens come back per second.

`start` — the time in seconds when the bucket was created full, like 0.
The test builds all four and hands them to you. Time is just numbers
here; nothing really waits.

## You return
a dictionary with "allowed" (a list of True/False, one per
request, in order) and "tokens_left" (how many tokens remain after the
last request, rounded to 6 decimals).

## Rules
Decide which requests the rate limiter lets through.

A token bucket holds at most `capacity` tokens, starts full at time
`start`, and refills at `rate` tokens per second. An accepted request
costs one token.

`requests` is a list of (timestamp, request_id) in non-decreasing time
order. The clock is data here — nothing sleeps, and the test can
replay an hour of traffic instantly.

For each request, in order:
  - Refill first: tokens = min(capacity, tokens + elapsed * rate),
    where elapsed is the time since the request you looked at just
    before this one, or since `start` for the very first.
  - If this request_id was accepted earlier, accept it again and
    charge nothing. A retry of something you already did must not
    cost a second token. That is idempotency, and it is the half of
    this question people forget.
  - Otherwise: tokens >= 1 means spend one and accept, anything less
    means reject.

Return

```
{"allowed": [True, True, False, True, True],
 "tokens_left": 1.0}
```

where allowed has one entry per request, in order, and tokens_left is
what is in the bucket after the last one, rounded to 6 decimals.

Worked example, capacity=2, rate=1, start=0:

```
(0, "a")  bucket full at 2, spend    -> True,  1 left
(0, "b")  spend                      -> True,  0 left
(0, "c")  empty                      -> False, 0 left
(0, "a")  already accepted, free     -> True,  0 left
(2, "d")  2 seconds refilled 2       -> True,  1 left
```

Rate limiters come up in every systems screen. Say the three pieces of
state out loud before you write any of them.

## Hints
### Hint 1
Three pieces of state and nothing else: how many tokens are in the bucket, when you last looked at the clock, and which request ids you have already accepted. Everything else is one pass down the list. The classic bug is refilling with the wrong elapsed — it is the gap since the previous request, not the time since the bucket was created.
### Hint 2
tokens = float(capacity), last = start, seen = set(). Per request: refill with min(capacity, tokens + (ts - last) * rate), then set last = ts before you decide anything, or the next refill double-counts. Check `rid in seen` first, the tokens >= 1 branch second. The version an interviewer wants to see is a small class: __init__(self, capacity, rate, start) holding that state and an allow(self, ts, rid) method returning a bool, with tokens_left as a @property. Then solve is a loop four lines long.
### Hint 3
Different data — refill and cap in isolation, capacity 3, rate 0.5, one token spent each time:

```python
capacity, rate, tokens, last = 3, 0.5, 3.0, 0
for ts in [0, 1, 5]:
    tokens = min(capacity, tokens + (ts - last) * rate)
    last = ts
    tokens -= 1
    print(ts, tokens)
# 0 2.0
# 1 1.5     <- 1 second refilled half a token
# 5 2.0     <- refill wanted 3.5, the cap said 3
```

The cap is what makes it a bucket instead of a counter that grows forever while the service is idle.
