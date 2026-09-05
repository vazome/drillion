---
title: requests.Session — shared headers, reused connection
difficulty: medium
tier: packages
minutes: 15
prereqs: [17, 45]
tags: [http, requests]
---
# requests.Session — shared headers, reused connection

*One Session reuses the connection and carries the auth; ten bare gets do neither.*

## Read first
- [Requests: session objects](https://requests.readthedocs.io/en/latest/user/advanced/#session-objects) — connection reuse and shared headers

## Why
A health-check bot asks an internal status API "how is the api? how is the db? how is the cache?" every minute, one request per service. Every request must carry the same secret token and the same label that names your program (the User-Agent). Done the naive way, each request opens a fresh connection to the server and repeats the headers, which is slow and is exactly where "one call forgot the token" bugs come from. The ask: set up one reusable client with the shared headers configured once, then send all the requests through it.

## You get
`base_url` — a string like `"https://ops.example.com"`.

`token` — a string secret like `"tok-4f"`.

`agent` — a string label like `"deploybot/1.0"` naming your program to the server.

`names` — a list of service names like `["api", "db"]`.

The test points the requests library at a fake server and spies on the client object, so nothing real is contacted; it checks that every request went through the one client you hand back.

## You return
a pair (tuple): first the reusable client object you used (a requests `Session`), then a dict of service name to its status string, like `{"api": "healthy", "db": "degraded"}`.

## Rules
Ask one API about several services, over a single `Session`.

Build a `requests.Session`, set the two headers every call needs on the `Session` itself, then GET one url per name, in the order given:

```python
f"{base_url}/services/{name}"
```

The two shared headers:

| Header | Value |
| --- | --- |
| `Authorization` | `Bearer <token>` |
| `User-Agent` | `<agent>` |

Each response is JSON like `{"name": "api", "status": "healthy"}`. Call `raise_for_status()`, then keep the `"status"` field.

Return a 2-tuple: the `Session` you used, then a dict of name to status.

```python
solve("https://ops.example.com", "tok-4f", "deploybot/1.0", ["api", "db"])
# -> (<the Session object>, {"api": "healthy", "db": "degraded"})
```

> [!WARNING]
> The session goes back with the answer because the test checks it: that its `.headers` carry both values, and that every request recorded on the wire came from that exact object. Building a `Session` and then calling `requests.get` anyway is the mistake this task exists to catch.

- Still pass `timeout=` on every call. A `Session` shares headers, cookies and a connection pool — it has no default timeout, and setting one on the object does nothing.

Why bother. Bare `requests.get` builds a Session, opens a TCP connection, does the TLS handshake, sends one request, and throws all of it away. Ten services is ten handshakes. A Session keeps a pool of open connections and reuses them, so calls two through ten are cheap. The other half is auth: set on the Session, the header exists in one place instead of at every call site, which is where "one endpoint forgot the token" comes from.

## Hints
### Hint 1
A Session is a client you keep, not a call you make. Two things live on it: state that should apply to every request (headers, cookies, auth) and the connection pool underneath. requests.get is a one-shot wrapper that builds one, uses it once, and drops it — which is why it cannot reuse a connection and cannot remember your token. Note what does NOT live on the session: anything about an individual call, timeout included.
### Hint 2
s = requests.Session(), then s.headers.update({...}) with both header names. After that s.get(url, timeout=...) behaves like requests.get but merges the session headers in for you. Loop over names, build the url with an f-string, raise_for_status, and collect r.json()['status'] into a dict. Return (s, that_dict) — a plain tuple, session first.
### Hint 3
Different data — one session against a paste service:

```python
s = requests.Session()
s.headers.update({'X-Api-Key': 'k-99', 'User-Agent': 'linter/2.1'})
out = {}
for pid in ['a1', 'b2']:
    r = s.get(f'https://paste.example.com/api/{pid}', timeout=5)
    r.raise_for_status()
    out[pid] = r.json()['lang']
print(out)                  # {'a1': 'python', 'b2': 'go'}
print(s.headers['X-Api-Key'])   # k-99, still set for the next call
```

Same shape as yours: configure once above the loop, then the loop only does the part that changes.
