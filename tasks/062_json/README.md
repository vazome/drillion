---
title: json — loads, safe nested gets, dumps
difficulty: medium
tier: core
minutes: 15
prereqs: [48]
tags: [files-text]
---
# json — loads, safe nested gets, dumps

*APIs answer in JSON; the nested-missing-key crash is the classic screen-share failure.*

## Read first
- [json](https://devdocs.io/python~3.14/library/json) — `loads`/`dumps`, and why `sort_keys` and `default=` matter for stable output

## Why
A cluster API answers with the state of every node as JSON text. Not every node reports CPU load, and not every cluster carries a region tag. The platform team's dashboard script keeps crashing because it assumes those fields are always present. You are asked to write a version that produces a short summary (region plus CPU per node) and never crashes when a field is simply absent.

## You get
`text` — a string of JSON, the raw text an HTTP API answered with, shaped like the example in the rules below. The test creates it and hands it to you; you never build it yourself.

## You return
a string — the summary written back out as JSON text with two-space indent and sorted keys, exactly as shown in the rules below.

## Rules
`text` is the JSON string a cluster API returned. Its shape, pretty-printed:

```json
{"cluster": {
    "name": "prod-2",
    "nodes": [
        {"name": "node-7-0",
         "status": {"phase": "Ready",
                    "load": {"cpu": 0.42, "mem": 0.61}}},
        {"name": "node-3-1",
         "status": {"phase": "NotReady"}}],
    "meta": {"region": "eu-central-1"}}}
```

Guaranteed present: `"cluster"`, `"nodes"`, and each node's `"name"`, `"status"` and `"status"` → `"phase"`. Optional: `"meta"` (and `"region"` inside it), `"load"` (and `"cpu"` inside it).

> [!WARNING]
> Indexing an optional key that is absent must not crash your code.

Return the STRING `json.dumps(summary, indent=2, sort_keys=True)` where

```python
summary = {"region": "eu-central-1",            # or "unknown" if absent
           "cpu_by_node": {"node-7-0": 0.42,
                           "node-3-1": None}}   # None when cpu missing
```

For the example above that string prints as:

```json
{
  "cpu_by_node": {
    "node-3-1": null,
    "node-7-0": 0.42
  },
  "region": "eu-central-1"
}
```

## Hints
### Hint 1
`json.loads` hands you plain dicts and lists — after that it is not a JSON problem, it is a dict problem. The crash comes from square-bracketing a key that is not there. Only the hops the schema marks optional need a lookup with a default; the guaranteed ones can stay as plain indexing.
### Hint 2
`data['cluster']['nodes']` is safe — the spec guarantees those. For the optional hops, chain `dict.get` with an empty-dict default: `get('meta', {})` then `get('region', 'unknown')`. Note that `.get` with no default returns `None`, which is exactly what the cpu column wants. Finish with `json.dumps` plus its `indent` and `sort_keys` keyword arguments.
### Hint 3
Different data, same pattern:

```python
import json
cfg = {'svc': {'limits': {'mem': '1Gi'}}}
cpu = cfg['svc'].get('limits', {}).get('cpu', 'unset')
print(cpu)                                        # unset
print(json.dumps({'b': 1, 'a': 2}, sort_keys=True))  # {"a": 2, "b": 1}
```

Chained `.get` with `{}` defaults never raises; the `dumps` arguments control the exact text you return.
