---
title: Link header pagination — follow rel=next with requests
difficulty: medium
tier: packages
minutes: 25
prereqs: [45, 46]
tags: [http, requests]
---
# Link header pagination — follow rel=next with requests

*GitHub-shaped APIs hide the next page in a header, and requests already parsed it.*

> [!NOTE]
> Topic 52 on the checklist is FastAPI. That needs a running server and packages we do not have offline, so this slot tasks real-API pagination instead — the same loop as topic 49, but against actual requests/Response objects rather than a fake.

## Why
A manager wants every open issue in the team's repo on a GitHub-style server, to build a backlog report. The server hands back issues a few at a time, and it tells you where the next batch lives not in the data but in a response header called `Link`: a line listing web addresses labelled next, prev, first and last. You must follow the "next" address until there is none, send the token and a time limit with every request, and never guess at addresses yourself, because the server only answers addresses it handed out.

## You get
`first_url` — a string: the web address of the first page, like `"https://api.github.test/repos/sre/runbooks/issues?page=1"`.

`token` — a string secret that proves who you are.

The test points the requests library at a fake server with made-up pages and inspects each request you made; nothing real is contacted.

## You return
one flat list of every issue dict from every page, in the order received, like `[{"number": 412, "title": "flaky test"}, ...]`.

## Rules
Collect every item the API will give you, across all pages.

GET `first_url` with the header `Authorization: Bearer <token>` and a `timeout=`, call `raise_for_status()`, and keep going until the server stops offering a next page.

Each response body is a JSON array of objects:

```python
[{"number": 412, "title": "flaky test"},
 {"number": 415, "title": "rotate certs"}]
```

The pointer to the next page is not in the body. It is in the `Link` header, GitHub style:

```http
Link: <https://api.example.com/...?page=2&per_page=2>; rel="next",
      <https://api.example.com/...?page=4&per_page=2>; rel="last"
```

requests parses that for you into `response.links`, a dict keyed by rel:

```python
{"next": {"url": "https://...page=2&per_page=2", "rel": "next"},
 "last": {"url": "https://...page=4&per_page=2", "rel": "last"}}
```

Return one flat list of every item dict, in the order the pages handed them over:

```python
# page 1  ->  [{"number": 412, "title": "flaky test"}]
# page 2  ->  [{"number": 415, "title": "rotate certs"}]
solve(first_url, token)
# -> [{"number": 412, "title": "flaky test"},
#     {"number": 415, "title": "rotate certs"}]
```

Three ways this goes wrong:

- "links is empty" is not the stop signal. The last page still advertises first and prev; what it lacks is next. Ask for the `"next"` key specifically.
- Do not build page urls yourself. Send back the url the server gave you, whole, query string and all. Page 2 is not always just `page=2` — servers change the page size or hand you a cursor, and this API only answers urls it has issued.
- Every request needs the token and the timeout, not just the first one.

A one-page response has no `Link` header at all. That must work too, with the same loop.

## Hints
### Hint 1
You cannot know the page count up front, so this is a while loop, and the thing that survives each turn is the url to fetch next. Two details are specific to HTTP: the pointer lives in a response header rather than in the JSON, and requests has already turned that header into a small dict for you, so there is no parsing to write. The stop condition is the absence of one particular rel, not the absence of links.
### Hint 2
Keep a url variable starting at first_url and an items list outside the loop. Inside: requests.get(url, headers=..., timeout=...), raise_for_status(), items.extend(r.json()) — extend, since the body is already a list — then look at r.links. r.links.get('next') gives you either None or a dict with a 'url' key, which is exactly what decides whether the loop runs again. `while url:` reads well once url becomes None at the end.
### Hint 3
Different data — walking an audit log the same way:

```python
url = 'https://audit.example.com/events?since=monday'
rows = []
while url:
    r = requests.get(url, headers={'X-Api-Key': 'k-9'}, timeout=10)
    r.raise_for_status()
    rows.extend(r.json())
    print(r.links)   # {'next': {'url': '...&cursor=e4f', 'rel': 'next'},
                     #  'first': {'url': '...', 'rel': 'first'}}
    nxt = r.links.get('next')
    url = nxt['url'] if nxt else None
print(len(rows))     # 57
```

Same three beats as yours: fetch, accumulate, ask the response where to go next.
