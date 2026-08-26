from fastapi import FastAPI

# ── the app under test (do not edit) ────────────────────────────────────
_ROWS = []          # the test fills this before each call

app = FastAPI()


@app.get("/search")
async def search(q: str):
    return [{"id": r["id"], "content": r["content"]} for r in _ROWS]


def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import asyncio
import inspect

import httpx
from _lib import rng


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
