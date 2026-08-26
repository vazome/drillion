---
title: take-home Task 2 — rerank the candidate pool
difficulty: medium
tier: core
track: rsample
minutes: 20
prereqs: [8, 21, 27]
tags: [sets, sorted]
---
# take-home Task 2 — rerank the candidate pool

*Take-home Task 2 — retrieve wide, then rerank: fraction-of-query-words score, stable top-k.*

## Why
Vector search returned the 5 geometrically nearest chunks, and they were often not the 5 best answers — two chunks can sit close in embedding space while only one actually contains the words the user typed. The fix was two stages: ask the database for 20 (cheap, wide, recall) and re-score those 20 against the query with a second function (narrow, precision), keeping the top 5. Your submission scored by raw count of overlapping words; here you use the FRACTION of the query's words found, which is the same idea but comparable across queries and bounded 0..1 — the improvement you would name in the interview.

## You get
- `query` — the user's text, e.g. `"Storage best-practices"`
- `rows` — the candidate pool in vector-distance order: a list of dicts like `{"id": 7, "content": "storage configuration: ..."}`
- `k` — how many to keep, e.g. `5`

## You return
a list of the top `k` rows (same dicts, unchanged), best score first; ties keep their incoming (vector) order.

## Rules
- Tokenise both sides the same way: lowercase, remove everything that is not a letter, digit, underscore or whitespace, split on whitespace, and use a SET of words (repeats do not count).
- score = (number of query words present in the chunk) / (number of distinct query words). An empty query scores 0.0 for every chunk.
- Sort by score descending with a stable sort, take the first k. If fewer than k rows exist, return them all.

```python
query = "storage best practices"
rows = [{"id": 1, "content": "billing setup"},
        {"id": 2, "content": "storage best practices guide"},
        {"id": 3, "content": "storage migration"}]
solve(query, rows, k=2)
# -> [row 2 (score 1.0), row 3 (score 1/3)]
```

## Read first
- [Rerankers](https://www.pinecone.io/learn/series/rag/rerankers/) — read the first half: why a cheap wide first stage + an expensive narrow second stage beats either alone
- [Precision and recall](https://en.wikipedia.org/wiki/Precision_and_recall) — just the intro: recall = "did we fetch all the relevant ones", precision = "is what we show actually relevant"
- [Sorting HOW TO](https://docs.python.org/3/howto/sorting.html) — `key=`, `reverse=True`, and 'Sort Stability': equal scores keep their incoming order, which is how ties stay in vector order
- [set](https://docs.python.org/3/library/stdtypes.html#set) — `&` gives the words in both sets

> [!NOTE]
> **Take-home:** Task 2 + the "fraction, not count" upgrade

## Hints
### Hint 1
Write `_tokens(text)` first: `set(re.sub(r'[^\w\s]', '', text.lower()).split())`. Then score = `len(q & c) / len(q)` with a guard for an empty q. Then `sorted(rows, key=lambda r: score(...), reverse=True)[:k]`.
### Hint 2
Why `sorted(..., reverse=True)` keeps ties in order: Python's sort is stable, and `reverse=True` still preserves the original order among equal keys (it is not the same as sorting then reversing). That is why the 'all scores equal' test in your take-home came back in vector order.
### Hint 3
**Say it in the interview:**

> Stage one is recall-oriented: vector distance is cheap and fetches 20 plausible chunks. Stage two is precision-oriented: a per-chunk score against the actual query text reorders them and keeps 5. The cost is 20 cheap scoring calls per request, paid to fix cases where embedding closeness and relevance disagree. I used raw overlap count; a fraction would be bounded and comparable across query lengths.
