---
title: runnables — build a chain with |
difficulty: medium
tier: packages
minutes: 15
prereqs: [17]
tags: [llm, langchain]
---
# runnables — build a chain with |

*LCEL: `|` glues small steps into one thing you can call.*

## Read first
- [LangChain: Runnable interface](https://python.langchain.com/docs/concepts/runnables/) — `invoke`, `batch`, `stream` — the one interface everything implements

## Why
LangChain is a library for wiring steps together around an AI model, and its core idea is that small steps get joined into one pipeline with a single operator. Teams use it to build things like "read a metric line, decide whether it is slow, write the report line". Each step is small and can be swapped on its own, and the finished pipeline can handle one item or a whole list with no extra code. Interviewers ask for this to see that you understand the joining idea, not just one big function.

## You get
nothing — you build the thing from scratch.

## You return
the pipeline itself (three joined steps), not a result. The test will feed it lines like `"svc=api latency=250"` and expect `"api 250ms SLOW"` back, and it checks that the chain really is three separate steps.

## Rules
A "chain" in LangChain is small steps joined by the `|` operator.

Every step is a Runnable, which just means it has the same handful of methods: `.invoke(one_input)` and `.batch(list_of_inputs)`. Join two with `|` and you get another Runnable, so the whole pipeline has those methods too and you never wrote a loop.

Return a chain of THREE `RunnableLambda` steps that turns one raw metric line into one report line.

```python
chain = solve()
chain.invoke("svc=api latency=250")    # -> "api 250ms SLOW"
chain.invoke("svc=auth latency=90")    # -> "auth 90ms ok"
```

The three steps, in order:

1. **parse** — a line is always two `key=value` pairs in that order, and latency is a whole number

   ```python
   parse("svc=api latency=250")   # -> {"svc": "api", "latency": 250}
   ```

2. **transform** — add a `"slow"` key: `True` when latency is over 200, else `False` (exactly 200 is not slow)

3. **format** — `"<svc> <latency>ms SLOW"` when slow, `"<svc> <latency>ms ok"` otherwise

Wrap each function in `RunnableLambda` and join them with `|`. Return the chain itself, not a result.

> [!WARNING]
> The test calls `.invoke(line)` on it, calls `.batch(lines)`, and checks it really is three pieces joined with `|` — one big `RunnableLambda` doing all three jobs is the thing this tasks against.

## Hints
### Hint 1
A chain is not a special object you configure. It is three ordinary functions with `|` between them. The reason to bother splitting them up: once joined, the pipeline has the same interface as each piece, so .invoke for one item and .batch for a list both come for free, and you can swap step 2 without touching 1 or 3. One function doing everything gives up all of that.
### Hint 2
Write the three plain functions first — parse, transform, format — each taking one argument and returning one value, and check them by hand. Then wrap each in RunnableLambda(...) and join with |. For parse: line.split() gives you the two pairs, then split each on '=', and int() the latency so it compares as a number.
### Hint 3
Different data — a two-step chain that cleans, then labels:

```python
from langchain_core.runnables import RunnableLambda
clean = RunnableLambda(lambda s: s.strip().lower())
label = RunnableLambda(lambda s: f'user said: {s}')
chain = clean | label
print(chain.invoke('  HELLO  '))       # user said: hello
print(chain.batch(['  A ', ' B ']))    # ['user said: a', 'user said: b']
```

Yours is the same shape with three steps, and a dict rather than a string travelling between them.
