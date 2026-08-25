---
title: LCEL — a dict of runnables fans one input out
minutes: 20
prereqs: [88]
tags: [llm, langchain]
---
# LCEL — a dict of runnables fans one input out

*The dict-of-runnables shape: one input fans out into several named fields.*

## Why
LangChain is a library for wiring steps together around an AI model. A common pattern at companies is "answer a question using our own documents": the question goes in, related documents are looked up, and both the question and the documents are handed to a template that writes the final text. So one input has to reach several steps at once, and their results have to be collected under names. This exercise builds exactly that fan-out.

## You get
`retrieve` — a function: give it a question string and it returns a list of matching document strings. The test hands you a fake that searches a tiny in-memory list; nothing real is contacted.

`render` — a function: give it a dictionary of named fields and it returns the final string. The test's fake writes down every dictionary it receives so the test can check the field names.

## You return
the chain itself, not a result. When the test calls it with a question, it must call `render` with a dictionary holding exactly the keys `"question"`, `"context"` and `"n_docs"`, and give back whatever `render` returned.

## Rules
This is the shape that makes real LangChain code unreadable at first:

```python
{"context": ..., "question": RunnablePassthrough()} | render
```

A plain dict on the left of `|` becomes a step of its own. It runs every value on the SAME input and returns a dict of the results under those key names. So one question goes in and a dict with several filled-in fields comes out, ready for the next step. `RunnablePassthrough()` is the do-nothing step: it hands its input straight through unchanged, which is how the original question survives next to the looked-up context.

You are given two functions:

```python
retrieve(question)  # -> list of matching document strings
render(fields)      # -> the final string, built from a dict
```

Return a chain that takes ONE question string and returns `render`'s output, where `render` is handed a dict with exactly these three keys:

| key | what goes in it |
| --- | --- |
| `"question"` | the question, unchanged |
| `"context"` | `retrieve`'s documents joined into one string, a newline between each pair (empty string when there are none) |
| `"n_docs"` | how many documents `retrieve` returned |

Worked example, with `retrieve("restart")` returning `["pod docs", "node docs"]`:

```python
chain = solve(retrieve, render)
chain.invoke("restart")     # hands render
# {"question": "restart",
#  "context":  "pod docs\nnode docs",
#  "n_docs":   2}
```

Note that `"context"` and `"n_docs"` both start from `retrieve`. A dict value is allowed to be a small chain of its own, so `RunnableLambda(retrieve)` piped into something else is a legal value — the same input reaches both branches.

> [!WARNING]
> The test inspects the dict `render` actually received, so the key names and their contents both have to be right. The chain must also work under `.batch(list_of_questions)`.

## Hints
### Hint 1
The confusing part is that the dict is not data being passed along — the dict IS the step, and its values are steps too. Whatever went into the dict step goes into every one of its values, and the outputs get reassembled under the same keys. Sketch it on paper: one arrow in, three arrows out, three results back into one dict, then one arrow onward.
### Hint 2
Build the dict literal first: keys 'question', 'context', 'n_docs'. Use RunnablePassthrough() for 'question'. For 'context' you need retrieve then a join, which is RunnableLambda(retrieve) | RunnableLambda(...) — a chain nested inside a dict value. 'n_docs' is retrieve then len. Then pipe the whole dict into RunnableLambda(render) and return that.
### Hint 3
Different data — one word fanned into three fields:

```python
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
show = RunnableLambda(lambda f: f"{f['word']}/{f['upper']}/{f['size']}")
chain = {
    'word': RunnablePassthrough(),
    'upper': RunnableLambda(str.upper),
    'size': RunnableLambda(list) | RunnableLambda(len),
} | show
print(chain.invoke('pod'))    # pod/POD/3
```

Notice 'size' is two steps stacked inside one dict value, and every value saw the same 'pod'.
