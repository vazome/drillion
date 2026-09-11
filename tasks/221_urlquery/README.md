---
title: urllib.parse — set one query parameter without disturbing the rest of the URL
difficulty: medium
tier: core
minutes: 18
prereqs: [24]
tags: [stdlib-ops, strings]
---
# urllib.parse — set one query parameter without disturbing the rest of the URL

*A URL is a structure with five parts, and `urllib.parse` is the pair of functions that takes it apart and puts it back together again.*

## Read first
- [`urllib.parse`](https://devdocs.io/python~3.14/library/urllib.parse) — the module, and which function returns which parts
- [`urlsplit`](https://devdocs.io/python~3.14/library/urllib.parse#urllib.parse.urlsplit) and [`urlunsplit`](https://devdocs.io/python~3.14/library/urllib.parse#urllib.parse.urlunsplit) — apart, and back together
- [`parse_qsl`](https://devdocs.io/python~3.14/library/urllib.parse#urllib.parse.parse_qsl) and [`urlencode`](https://devdocs.io/python~3.14/library/urllib.parse#urllib.parse.urlencode) — the query string as a list of pairs

## Why
A crawler is walking a paginated listing and has to ask for the next page. The link it was handed already carries a search term, three facet filters — two of which use the same parameter name twice — and an anchor that scrolls the browser to the results. All of that has to survive; only `page` changes. Sticking `&page=2` on the end of the string works right up until the URL has a `#results` on it, at which point the crawler asks the server for a page named `2#results` and gets a listing that never advances.

## You get
`url` — an absolute URL string. It may or may not already carry a query string, and may or may not end in a fragment.

`key` — the query parameter name to set.

`value` — the string it should be set to.

## You return
the whole URL again as a string, with that one parameter set.

## Rules
- Every other parameter keeps its name, its value and its position, including a name that appears more than once.
- If `key` is already in the query, the first place it appears becomes `key=value` and any later copies of it are dropped.
- If `key` is not in the query yet, it goes on the end.
- Scheme, host, path and fragment come back untouched.
- Re-encode the query with `urlencode`, so the answer is the one `urlencode` would produce for that list of pairs.

```python
solve("https://ex.com/search?tag=a&q=old&tag=b#top", "q", "new")
# -> "https://ex.com/search?tag=a&q=new&tag=b#top"

solve("https://ex.com/search", "page", "2")
# -> "https://ex.com/search?page=2"
```

> [!WARNING]
> `parse_qs` gives you a dictionary, and a dictionary cannot hold `tag` twice. Feed that dictionary back to `urlencode` and the repeated parameter comes out as the `repr` of a Python list — `tag=%5B%27a%27%2C+%27b%27%5D` — which is not a thing any server will understand. `parse_qsl` returns a list of pairs and keeps every one of them.

> [!NOTE]
> `urlsplit` returns a named tuple, and named tuples have `_replace`: `parts._replace(query=...)` gives you a new one with everything else carried over.

## Hints
### Hint 1
Four calls, in order: `urlsplit` to take it apart, `parse_qsl` on `parts.query`, your edit, then `urlencode` and `urlunsplit` to put it back.
### Hint 2
Walk the pairs and build a new list. A pair whose name is not `key` is copied straight across; the first one that matches becomes `(key, value)`; a later match is skipped. A flag tells you which case you are in and, at the end, whether to append.
### Hint 3
`parse_qsl(parts.query, keep_blank_values=True)` keeps `?debug=` rather than silently dropping it, which matters when the parameter you are not touching is a blank one.

```python
parts = urlsplit(url)
pairs = parse_qsl(parts.query, keep_blank_values=True)
...
return urlunsplit(parts._replace(query=urlencode(pairs)))
```
