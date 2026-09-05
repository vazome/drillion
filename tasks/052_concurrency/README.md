---
title: threads vs processes vs async — pick one, say why
difficulty: easy
tier: advanced
track: rsample
minutes: 8
prereqs: []
tags: [concurrency]
---
# threads vs processes vs async — pick one, say why

*Reaching for threads on CPU work is the wrong answer that ends a phone screen.*

## Read first
- [Speed up your Python program with concurrency](https://realpython.com/python-concurrency/) — threads vs processes vs asyncio, when each wins
- [Concurrent execution — the stdlib index](https://devdocs.io/python~3.14/library/concurrency) — the modules themselves: threading, multiprocessing, concurrent.futures, asyncio

## Why
A colleague brings you a list of jobs they want to speed up: resize 8 images, call 40 APIs, poll 5000 sensors. Python has three ways to do several things at once, and picking the wrong one makes a job no faster or even slower. The team wants one simple rule written down so everyone picks consistently: heavy calculation gets separate processes, a modest number of network waits gets threads, a huge number of waits gets async. Interviewers ask for this rule and the reasons behind it.

## You get
`workloads` — a list of dicts, each like `{"kind": "io", "count": 40}`, where kind is `"io"` (waiting on network or disk) or `"cpu"` (calculating) and count is how many things there are to do. The test creates it and hands it to you.

## You return
a list of strings, one per workload, in the same order; each is `"threads"`, `"processes"` or `"async"`.

## Rules
Pick the right concurrency tool for each workload.

Each workload is a dict:

```python
{"kind": "io", "count": 40}     # 40 things to do, all waiting on I/O
{"kind": "cpu", "count": 8}     # 8 things to do, all number crunching
```

Return a list of labels, one per workload, in input order. Each label is `"threads"`, `"processes"` or `"async"`. The rule:

| Workload | Label |
| --- | --- |
| `kind == "cpu"` | `"processes"` |
| `kind == "io"` and `count < 100` | `"threads"` |
| `kind == "io"` and `count >= 100` | `"async"` |

```python
solve([{"kind": "cpu", "count": 8},
       {"kind": "io", "count": 12},
       {"kind": "io", "count": 5000}])
# -> ["processes", "threads", "async"]
```

The reasoning behind the rule, which is the part you actually get asked for:

CPU work goes to processes because the GIL lets only one thread run Python bytecode at a time. Ten threads doing arithmetic finish no sooner than one. Separate processes each get their own interpreter and their own lock, so they genuinely run at once — you pay for it in startup time and in having to pickle whatever you send across.

I/O work suits threads because a thread blocked on a socket holds the GIL for none of that time. Everything you already have works unchanged: requests, boto3, psycopg, all of it.

Past a hundred or so concurrent operations, threads stop being cheap — each one is a real OS thread with its own stack, and the scheduler starts costing more than the work. An event loop runs thousands of waits on one thread. The catch is that every library in the path has to be async-aware; one blocking call inside a coroutine freezes the whole loop, which is why "just use async" is not automatically the right answer.

## Hints
### Hint 1
One fact carries most of this: the GIL means only one thread runs Python bytecode at a time, so threads buy you nothing while computing and everything while waiting. That settles the cpu case on its own. The count only enters the picture on the waiting side, where the question is how many threads is too many.
### Hint 2
One pass over the list, one label appended per workload. Check the kind first — cpu has a single answer whatever the count is. Then one >= 100 test splits the io case in two. Mind the boundary the spec states: exactly 100 is async, not threads.
### Hint 3
Different data — same two-level decision, sizing disk jobs:

```python
jobs = [{'size': 5}, {'size': 40}, {'size': 40000}]
out = []
for j in jobs:
    if j['size'] < 10:
        out.append('small')
    elif j['size'] < 1000:
        out.append('medium')
    else:
        out.append('large')
print(out)       # ['small', 'medium', 'large']
```

Yours branches on two fields rather than one: kind first, then count inside the io branch.
