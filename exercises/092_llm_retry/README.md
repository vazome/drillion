---
title: LLM retry — back off on rate limits, fail fast on bad requests
minutes: 20
prereqs: [45]
tags: [llm, langchain]
---
# LLM retry — back off on rate limits, fail fast on bad requests

*Retry the failures that clear on their own — and only those.*

## Why
LangChain is a library for wiring steps together around an AI
model. Calls to a paid AI service fail in two ways. "Too many requests,
slow down" clears by itself if you wait a bit and try again. "Your
request is malformed" will never clear, and retrying it only wastes
money, adds load and delays the error message someone needs to read. A
script that treats both the same way is a common and expensive bug.

## You get
`model` — a stand-in AI model. model.invoke(prompt) returns an
answer string, or raises one of two errors defined at the top of this
file: RateLimited (wait and try again) or BadRequest (give up). The
test's fake follows a script of outcomes; no real AI is called.

`prompt` — the question, as a string.

`sleep` — a function you call with a number of seconds to wait. The test
hands you a fake that only writes the number down, so nothing really
waits.

`max_attempts` — a whole number, like 3: the most calls you may make.

`base` — a number, like 0.5: the first wait in seconds; each later wait
is double the one before.

## You return
the answer string from the model. If the tries run out, or
the request is bad, or the model raises something you were not told
about, let that error escape instead of returning anything.

## Rules
Model APIs fail in two very different ways, and telling them apart is
the whole job. A rate limit clears on its own, so waiting helps. A
malformed request does not, so retrying it burns your budget, multiplies
the load, and delays the error message someone actually needs to read.

Call `model.invoke(prompt)` and return what it returns. Rules:

  - at most `max_attempts` calls, ever
  - RateLimited, attempts remaining: wait, then try again. For failure
    number i (0-based, so the first failure is i=0) wait exactly

```
    base * (2 ** i)

by calling sleep(that number). Never time.sleep
```

  - RateLimited on the last allowed attempt: re-raise it
  - BadRequest: give up immediately. Re-raise it, do not sleep, do not
    call the model again
  - anything else the model raises is not yours to handle — let it out
    untouched, on the first sight of it

```
base=0.5, model raises RateLimited twice then returns "ok"
->  sleeps 0.5, then 1.0, calls the model 3 times, returns "ok"
```

RateLimited and BadRequest are defined at the top of this file, so you can
name them directly in an except clause. `sleep` is a parameter rather than
an import so the test can pass a fake that only records the delay — that
is why this test finishes instantly instead of waiting minutes, and
"inject the clock so tests control time" is worth saying out loud in an
interview.

## Hints
### Hint 1
Backoff is the easy half. The half that matters is that not every exception deserves a retry, so a bare `except Exception` is already the wrong answer — it turns one bad prompt into max_attempts identical bad prompts, and hides the real error behind the last one. Decide per exception type: wait and retry, or get out of the way.
### Hint 2
Loop `for attempt in range(max_attempts)` and try to return model.invoke(prompt) inside it. You need two except clauses on that try. `except BadRequest: raise` re-raises straight away. `except RateLimited:` checks whether attempt is the last one (bare `raise` if so) and otherwise calls sleep(base * 2 ** attempt) before going round again. Any other exception is caught by neither clause, which is exactly what you want.
### Hint 3
Different data — two kinds of failure from a file read, 3 tries:

```python
for attempt in range(3):
    try:
        data = open('/tmp/report').read()
        break
    except IsADirectoryError:
        raise                      # never going to become a file
    except BlockingIOError:
        if attempt == 2:
            raise                  # out of tries, give up honestly
        time.sleep(0.1 * 2 ** attempt)   # 0.1, then 0.2
```

Note the two clauses do opposite things, and that the last retry re-raises rather than returning None. Yours returns instead of breaking, and calls the injected sleep.
