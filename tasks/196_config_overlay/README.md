---
title: deep copy + dict.get — apply a safe configuration overlay
difficulty: medium
tier: core
minutes: 16
prereqs: [48, 53]
tags: [dict-get, shallow-vs-deep-copy]
---
# deep copy + dict.get — apply a safe configuration overlay

*Preserve nested input while optional override keys replace selected values.*

## Read first
- [copy.deepcopy](https://devdocs.io/python~3.14/library/copy#copy.deepcopy) — recursively copy nested mutable values
- [dict.get](https://devdocs.io/python~3.14/library/stdtypes#dict.get) — use a fallback when a key is absent

## Why
Deployment defaults are reused across environments. Applying one environment's labels to a shallow copy mutates the shared nested list and quietly contaminates the next deployment.

## You get
`config`, containing a nested `service` dictionary with `replicas` and `labels`, and `overrides`, which may contain `replicas`, `owner`, or `labels`.

## You return
A deep-copied configuration with the overlay applied. Neither the original nested dictionary nor its labels list may change.

## Rules
Use `deepcopy(config)`. On the copied `service`:

- replace `replicas` with `overrides.get("replicas", current_replicas)`;
- replace `owner` with its override, existing owner, or `"unassigned"`;
- extend `labels` with `overrides.get("labels", [])`.

An override of `0` is a real replica count.

## Hints
### Hint 1
Copy first and mutate only the copy. A top-level `.copy()` still shares `service` and `labels`.
### Hint 2
Keep a local `service = result["service"]`. Each optional value can then use `overrides.get(key, fallback)`.
### Hint 3
The owner's fallback has two layers: `overrides.get("owner", service.get("owner", "unassigned"))`. Finish by extending the copied labels list.
