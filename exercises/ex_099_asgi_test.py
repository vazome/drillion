"""Test a FastAPI endpoint with no server running — httpx.ASGITransport."""
# READ FIRST:
#   https://fastapi.tiangolo.com/tutorial/testing/  — the basic idea: call the app from a test
#   https://fastapi.tiangolo.com/advanced/async-tests/  — the exact pattern you used:
#       AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
#   https://www.python-httpx.org/advanced/transports/  — section 'ASGITransport': the client talks
#       to the app object in-process; no port, no socket, no uvicorn
#   https://fastapi.tiangolo.com/tutorial/query-params/  — why `q` is required and what 422 means
#   TAKE-HOME: `httpx.ASGITransport(app=app)`

import asyncio
import inspect

import httpx
from _lib import rng
from fastapi import FastAPI

META = {"topic": 99, "title": "ASGITransport — hit the endpoint without a server", "tier": 4,
        "minutes": 20, "prereqs": [98], "tags": ["testing", "asyncio", "fastapi", "rsample"]}


# ── the app under test (do not edit) ────────────────────────────────────
_ROWS = []          # the test fills this before each call

app = FastAPI()


@app.get("/search")
async def search(q: str):
    return [{"id": r["id"], "content": r["content"]} for r in _ROWS]


def solve():
    """WHY: The take-home said "tests must run with pytest alone: no running
    server, no Docker". Your tests did that with `httpx.ASGITransport`, and
    an interviewer will ask how that works. An ASGI app like FastAPI is just
    a Python callable that takes a request and produces a response; uvicorn
    normally feeds it bytes from a socket. ASGITransport feeds it the same
    request object straight from the test, in the same process, so you get
    real routing, real validation and real JSON without a port.

    YOU GET: nothing to start — you return an async function. The test calls
    it as `await call(app, params)` where:
      `app`    — the FastAPI application object defined above
      `params` — a dict of query-string values, e.g. {"q": "storage"} or {}

    YOU RETURN: a tuple `(status_code, body)` where body is the parsed JSON
    the endpoint answered with.

    ─── exact rules ───
      - Build `httpx.AsyncClient(transport=httpx.ASGITransport(app=app),
        base_url="http://test")` inside an `async with`, so it is closed.
      - `await client.get("/search", params=params)`.
      - Return `(resp.status_code, resp.json())`.
      - With `params={}` FastAPI answers 422 (q is required) — return that
        too, do not special-case it.
    """
    raise NotImplementedError


HINTS = [
    ("Three lines: `transport = httpx.ASGITransport(app=app)`, then `async with "
    "httpx.AsyncClient(transport=transport, base_url='http://test') as client:` "
    "and `resp = await client.get('/search', params=params)`. Return the tuple."),
    ("Why base_url is a fake hostname: nothing is resolved or connected; the "
    "transport hands the request to `app` directly. The host only needs to "
    "look like a URL so httpx can build one. 422 is FastAPI saying 'a required "
    "query parameter is missing' — the validation ran, which proves this is the "
    "real app, not a mock."),
    ("SAY IT IN THE INTERVIEW: 'ASGITransport calls the FastAPI app in-process: "
    "the request goes through real routing and validation and returns a real "
    "response, but no server, port or network is involved, so the suite runs "
    "with plain pytest. I monkeypatched get_pool and embed_query to fakes, so "
    "the only real thing under test was my endpoint logic.'"),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    n = r.randint(0, 4)
    return [{"id": r.randint(1, 500), "content": f"chunk {r.randint(1, 99)}"} for _ in range(n)]


def _reference():
    async def call(app, params):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/search", params=params)
        return resp.status_code, resp.json()

    return call


def test_solve():
    r = rng()
    call = solve()
    assert inspect.iscoroutinefunction(call), "solve() must return an async def"
    for _ in range(3):
        rows = _gen(r)
        _ROWS[:] = rows
        status, body = asyncio.run(call(app, {"q": "storage"}))
        assert status == 200
        assert body == [{"id": x["id"], "content": x["content"]} for x in rows]
    status, body = asyncio.run(call(app, {}))
    assert status == 422, "missing q must surface FastAPI's own 422, not be hidden"
    assert "detail" in body
