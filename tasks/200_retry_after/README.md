---
title: rate limiting — retry after the server tells you to wait
difficulty: medium
tier: core
minutes: 16
prereqs: [100, 109]
tags: [rate-limiting, retry-loops]
---
# rate limiting — retry after the server tells you to wait

*Respect a 429 response without sleeping after the final allowed call.*

## Read first
- [The while statement](https://devdocs.io/python~3.14/reference/compound_stmts#the-while-statement) — repeat with a clear stopping condition
- [dict.get](https://devdocs.io/python~3.14/library/stdtypes#dict.get) — default a missing retry delay

## Why
Rate limits are often enforced by someone else's server. A client must stop hammering it, wait for the requested delay, and still cap the total number of calls.

## You get
`call`, a zero-argument function returning a dictionary with `status` and sometimes `retry_after`; `sleep`, a fake sleeping function; and positive `max_attempts`.

## You return
`{"response": response, "attempts": count}` for the first response whose status is not `429`, or for the final allowed response.

## Rules
Call at most `max_attempts` times. After a `429`, sleep for `response.get("retry_after", 1)` before trying again. Never sleep after the final attempt. Any status other than `429`, including a server error, returns immediately.

## Hints
### Hint 1
The two exit conditions are “not rate limited” and “this was the last attempt.” Check both before sleeping.
### Hint 2
Loop over `range(1, max_attempts + 1)` so the current attempt number is already available for the result.
### Hint 3
Call once at the top of the loop. Return when `status != 429 or attempt == max_attempts`; otherwise call `sleep` with the supplied delay or `1`.
