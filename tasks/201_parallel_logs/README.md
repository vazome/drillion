---
title: ThreadPoolExecutor — summarise log chunks concurrently
difficulty: medium
tier: advanced
minutes: 22
prereqs: [97, 101]
tags: [log-analysis, threadpoolexecutor]
---
# ThreadPoolExecutor — summarise log chunks concurrently

*Fan independent files across workers, then merge their small summaries.*

## Read first
- [ThreadPoolExecutor](https://devdocs.io/python~3.14/library/concurrent.futures#threadpoolexecutor) — map independent blocking work over threads
- [Counter](https://devdocs.io/python~3.14/library/collections#collections.Counter) — merge counts from multiple chunks

## Why
Archived logs arrive as independent chunks and parsing each line blocks briefly on decompression. Processing chunks concurrently shortens the wait; combining summaries afterward avoids shared mutable counters between workers.

## You get
`chunks`, a list of line lists; `parse(line)`, a blocking callable returning `(level, duration)`; and `max_workers`.

## You return
A dictionary with:

- `levels`: an alphabetically keyed dictionary of total counts per level;
- `slowest`: the largest duration, or `0` when every chunk is empty.

## Rules
Define a worker that parses one whole chunk into a `Counter` and its maximum duration. Use `ThreadPoolExecutor(max_workers=max_workers)` and `pool.map` to run that worker over chunks. Merge the returned summaries on the caller thread. Do not update shared totals inside workers.

## Hints
### Hint 1
Make workers return data. The main thread can merge those results without a lock.
### Hint 2
For one chunk, build `parsed = [parse(line) for line in lines]`, then return its level `Counter` and maximum duration with `default=0`.
### Hint 3
Inside the executor's `with` block, collect `pool.map(summarize, chunks)`. Update one total `Counter`, keep the largest duration, and sort the counter's items when turning it into a dictionary.
