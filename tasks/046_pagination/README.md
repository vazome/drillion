---
title: pagination — follow the cursor until it runs out
difficulty: medium
tier: core
minutes: 12
prereqs: [21]
tags: [http]
---
# pagination — follow the cursor until it runs out

*Every list API caps the page size, so "get all of them" is always a loop.*

## Read first
- [Requests: quickstart](https://requests.readthedocs.io/en/latest/user/quickstart/) — the request loop you are wrapping

## Why
An ops engineer needs a list of every pod in a cluster for a capacity report. The cluster's API never hands back the whole list at once: each answer holds a handful of items plus a bookmark (called a cursor) that you send back to get the next batch. Miss a batch and the report silently under-counts; keep asking after the last batch and the API refuses. The task: fetch batch after batch until the API says there are no more, and glue all the items into one list.

## You get
`fetch_page` — a function that takes a cursor (`None` for the first call) and returns a dict like `{"items": ["pod-4", "pod-9"], "next": "cur-3f1a"}` — the shape is written out as `Page` above `solve`, so the editor knows it — where `"next"` is the cursor for the following batch, or `None` when there are no more. The test hands in a stand-in over made-up batches, counts how many times you call it, and blows up if you call it too often; no real API is contacted.

## You return
one flat list of every item from every batch, in the order they arrived, like `["pod-4", "pod-9", "pod-2"]`.

## Rules
Collect every item the API will give you, across all pages.

`fetch_page(cursor)` is one API call. Pass `None` to get the first page. It answers with a dict:

```python
{"items": ["pod-4", "pod-9"], "next": "cur-3f1a"}
```

`"next"` is the cursor for the following page, or `None` when there are no more pages. Return one flat list of all items, in the order the pages handed them over.

```python
fetch_page(None)   # -> {"items": ["a", "b"], "next": "c1"}
fetch_page("c1")   # -> {"items": [],         "next": "c2"}
fetch_page("c2")   # -> {"items": ["c"],      "next": None}

solve(fetch_page)  # -> ["a", "b", "c"]
```

- Call `fetch_page` exactly once per page, no more. The fake blows up if you keep calling after the cursor is spent.
- Do not stop on an empty items list. Emptiness is not the end signal; `"next": None` is. A page can be empty and still point at a page that is not.
- Some responses have one page and nothing else. That still works with the same loop.

## Hints
### Hint 1
You cannot know how many pages there are before you start, so a `for` over a range is out — this is a while loop. Two things have to survive from one turn of the loop to the next: the cursor you will send on the next call, and the list you are accumulating into. The server owns the stop condition, not you.
### Hint 2
cursor = None and items = [] before the loop. Then `while True:` call fetch_page(cursor), items.extend(page['items']) — extend, not append, or you get a list of lists — then cursor = page['next'] and break when it is None. An alternative shape is `while cursor is not None:` with the first call pulled out above it; the break version avoids that duplicate.
### Hint 3
Different data — walking a chain of jobs where each one names the next:

```python
chain = {None: ('a', 1), 1: ('b', 2), 2: ('c', None)}
out, key = [], None
while True:
    value, key = chain[key]
    out.append(value)
    if key is None:
        break
print(out)      # ['a', 'b', 'c']
```

Identical shape: each response carries both the data and the pointer you need for the next call.
