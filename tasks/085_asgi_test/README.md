---
title: ASGITransport — hit the endpoint without a server
difficulty: medium
tier: advanced
track: rsample
minutes: 20
prereqs: [84]
tags: [testing, asyncio, fastapi]
---
# ASGITransport — hit the endpoint without a server

*Test a FastAPI endpoint with no server running — httpx.ASGITransport.*

## Why
The take-home said "tests must run with pytest alone: no running server, no Docker". Your tests did that with `httpx.ASGITransport`, and an interviewer will ask how that works. An ASGI app like FastAPI is just a Python callable that takes a request and produces a response; uvicorn normally feeds it bytes from a socket. ASGITransport feeds it the same request object straight from the test, in the same process, so you get real routing, real validation and real JSON without a port.

## You get
nothing to start — you return an async function. The test calls it as `await call(app, params)` where:

- `app` — the FastAPI application object defined above
- `params` — a dict of query-string values, e.g. `{"q": "storage"}` or `{}`

## You return
a tuple `(status_code, body)` where body is the parsed JSON the endpoint answered with.

## Rules
- Build `httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")` inside an `async with`, so it is closed.
- `await client.get("/search", params=params)`.
- Return `(resp.status_code, resp.json())`.

> [!WARNING]
> With `params={}` FastAPI answers 422 (`q` is required) — return that too, do not special-case it.

## Read first
- [Testing](https://fastapi.tiangolo.com/tutorial/testing/) — the basic idea: call the app from a test
- [Async Tests](https://fastapi.tiangolo.com/advanced/async-tests/) — the exact pattern you used: `AsyncClient(transport=ASGITransport(app=app), base_url="http://test")`
- [Transports — ASGITransport](https://www.python-httpx.org/advanced/transports/) — the client talks to the app object in-process; no port, no socket, no uvicorn
- [Query Parameters](https://fastapi.tiangolo.com/tutorial/query-params/) — why `q` is required and what 422 means

> [!NOTE]
> **Take-home:** `httpx.ASGITransport(app=app)`

## Hints
### Hint 1
Three lines: `transport = httpx.ASGITransport(app=app)`, then `async with httpx.AsyncClient(transport=transport, base_url='http://test') as client:` and `resp = await client.get('/search', params=params)`. Return the tuple.
### Hint 2
Why base_url is a fake hostname: nothing is resolved or connected; the transport hands the request to `app` directly. The host only needs to look like a URL so httpx can build one. 422 is FastAPI saying 'a required query parameter is missing' — the validation ran, which proves this is the real app, not a mock.
### Hint 3
**Say it in the interview:**

> ASGITransport calls the FastAPI app in-process: the request goes through real routing and validation and returns a real response, but no server, port or network is involved, so the suite runs with plain pytest. I monkeypatched get_pool and embed_query to fakes, so the only real thing under test was my endpoint logic.
