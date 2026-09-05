---
title: parallel LLM calls — gather with a per-call timeout
difficulty: hard
tier: packages
minutes: 22
prereqs: [36, 53]
tags: [llm, asyncio, langchain]
---
# parallel LLM calls — gather with a per-call timeout

*Fan out N model calls at once, keep the order, cap what each one may cost you.*

## Why
LangChain is a library for wiring steps together around an AI model. A support team wants ten customer tickets summarised by an AI model. Sent one after another, each waits for the previous one to finish; sent all at once they take about as long as the slowest single one. But any single call can hang, so each needs its own time limit, and a call that runs out of time must just be marked as such without spoiling the other answers.

## You get
nothing — you build the thing from scratch. The function you write will later be handed three things: `model` (a stand-in AI model whose `ainvoke` method gives back an answer string), `prompts` (a list of strings) and `timeout` (seconds allowed per call). The test's fake model only pauses briefly and writes down when each call started and ended; no real AI is called.

## You return
an async function named `ask_all`. Return the function itself; do not call it. When the test runs it, it must give back a list of answers in the same order as the prompts, with the text `"TIMEOUT"` in the slot of any call that took too long.

## Rules
Ten prompts answered one after another is ten round trips of sitting still. Every Runnable has an async side — `await model.ainvoke(prompt)` — so all ten can be in flight at once. And since one prompt can hang, each call needs its own time limit rather than one limit for the batch.

Return an ASYNC function `ask_all(model, prompts, timeout)` where:

- `model` is a Runnable; `await model.ainvoke(prompt)` returns a string
- `prompts` is a list of prompt strings
- `timeout` is the seconds allowed for ONE call

`ask_all` must:

- start every call concurrently, not one after another
- return a list of answers in the same order as `prompts`
- put the string `"TIMEOUT"` in the slot of any call that ran longer than `timeout`, and leave the other answers untouched

```python
answers = await ask_all(model, ["a", "b", "c"], 0.03)
# -> ["A", "TIMEOUT", "C"]
```

One slow prompt must not delay the others and must not sink the whole batch.

> [!WARNING]
> The test records when each call starts and finishes, and fails a version that waits for one call to come back before starting the next. Return the function itself, not a coroutine: `return ask_all`.

## Hints
### Hint 1
Two separate problems, and mixing them up is the usual mistake. First: everything must be launched before anything is awaited, or you have a slow for-loop wearing async syntax. Second: the time limit belongs to one call, not to the group — a group-wide limit would kill the answers that already came back, and letting a timeout escape would sink the whole batch. So the per-call handling has to happen inside each call.
### Hint 2
Write a small inner `async def one(prompt)` that wraps a single call: asyncio.wait_for(model.ainvoke(prompt), timeout) gives up after `timeout` seconds by raising TimeoutError, so catch that and return 'TIMEOUT'. Then hand one(p) for every p to asyncio.gather, which runs them all at once and returns results in argument order.
### Hint 3
Different data — three lookups at once, each capped at 20ms:

```python
import asyncio
async def lookup(host):
    await asyncio.sleep(0.05 if host == 'slow' else 0.001)
    return host + '.internal'

async def one(host):
    try:
        return await asyncio.wait_for(lookup(host), 0.02)
    except TimeoutError:
        return 'TIMEOUT'

async def all_of(hosts):
    return await asyncio.gather(*(one(h) for h in hosts))

print(asyncio.run(all_of(['a', 'slow', 'b'])))
# ['a.internal', 'TIMEOUT', 'b.internal']
```

Yours awaits model.ainvoke(prompt) where this awaits lookup(host).
