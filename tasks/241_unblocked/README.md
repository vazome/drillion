---
title: graphlib.TopologicalSorter — what each finished job unblocks, as the completions arrive
difficulty: medium
tier: advanced
minutes: 20
prereqs: [103, 193]
tags: [topological-sort, stdlib-ops]
---
# graphlib.TopologicalSorter — what each finished job unblocks, as the completions arrive

*`prepare`, `get_ready` and `done` are a running conversation with the graph rather than one sorted list, which is what a scheduler actually needs.*

## Read first
- [`graphlib.TopologicalSorter`](https://devdocs.io/python~3.14/library/graphlib#graphlib.TopologicalSorter) — the constructor's graph, `prepare`, `get_ready`, `done`, `is_active`
- [`graphlib.CycleError`](https://devdocs.io/python~3.14/library/graphlib#graphlib.CycleError) — what `prepare` raises, and when
- [`static_order`](https://devdocs.io/python~3.14/library/graphlib#graphlib.TopologicalSorter.static_order) — the one-shot version, and why it is not this task

## Why
A pipeline dashboard has one job: as each step finishes, show the steps that just became runnable. That is not the start-up order and it is not the wave layout — both of those are computed once, up front, and are already wrong by the time the second step finishes early and the third one is retried. What the dashboard needs is the answer to "and now?", asked again after every completion, and the answer depends on which *other* steps have finished, not on who the finished step points at. `TopologicalSorter` keeps that state for you: you tell it what finished, it tells you what is newly runnable, and the counting that goes wrong when a step has two things to wait for is not your counting any more.

## You get
- `graph`, a dict mapping each job to the **set of jobs it waits for**. Every name that appears in a set is also a key.
- `completions`, the order the jobs actually finished in — always a legal order for that graph, and always every job exactly once. When the graph has a cycle nothing can finish, and `completions` means nothing.

## You return
a dict with exactly three keys:

| key | value |
|---|---|
| `cycle` | `True` when the graph cannot be scheduled at all, otherwise `False` |
| `initial` | the jobs runnable before anything has finished, sorted; `[]` when there is a cycle |
| `unlocked` | one sorted list per entry in `completions`: the jobs that became runnable **because that job finished**; `[]` when there is a cycle |

## Rules
- A job becomes runnable when the **last** of the jobs it waits for finishes, so it belongs to exactly one entry of `unlocked` — the completion that cleared its final dependency. A job with two dependencies does not appear when the first one finishes.
- `unlocked` has exactly as many entries as `completions`, one for each, in order. An entry is `[]` when that completion cleared nothing, and that is a common case.
- Every list you return is sorted, so two runs over the same graph agree.
- A cycle is detected, not hunted for: report it and hand back two empty lists.

```python
solve({"db": set(), "cache": set(), "api": {"db", "cache"}}, ["db", "cache", "api"])
# -> {'cycle': False, 'initial': ['cache', 'db'], 'unlocked': [[], ['api'], []]}

solve({"a": {"b"}, "b": {"a"}}, [])
# -> {'cycle': True, 'initial': [], 'unlocked': []}
```

`db` finishing unlocks nothing, because `api` is still waiting on `cache`. `cache` finishing unlocks `api`. `api` finishing unlocks nothing, because it is the end.

> [!WARNING]
> Listing everything that depends on the finished job is the wrong answer and it agrees with the right one on every job that has a single dependency. The graphs here contain jobs that wait for two or three, which is the only place the two answers differ.

> [!NOTE]
> `get_ready()` **consumes**: it hands out the jobs that are ready now and never mentions them again, and those are the jobs `done()` will accept later. Calling it twice in a row gives you the new ones the second time, not the same ones again — which is exactly the behaviour this task wants, and a trap if you expected a snapshot.

## Hints
### Hint 1
`static_order()` answers a different question — it is the whole order at once, with no room to say what finished when. The three-method interface is the one that takes completions as they come.
### Hint 2
`prepare()` is where a cycle turns into a `CycleError`, so it goes in a `try`. After it returns, one `get_ready()` is your `initial`, and then the loop is: `done(job)`, `get_ready()`, sort whatever came back.
### Hint 3
The conversation, on a three-job graph:

```python
import graphlib

ts = graphlib.TopologicalSorter({"report": {"extract", "clean"}, "clean": {"extract"}, "extract": set()})
ts.prepare()
ts.get_ready()        # -> ('extract',)
ts.done("extract")
ts.get_ready()        # -> ('clean',) — report is still waiting on clean
ts.done("clean")
ts.get_ready()        # -> ('report',)
ts.is_active()        # -> True: report has been handed out but not reported done
```

`done()` on a job that was never handed out by `get_ready()` is a `ValueError`, which is the library holding you to the order rather than being fussy.
