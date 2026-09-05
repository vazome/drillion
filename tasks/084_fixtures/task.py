import asyncio

import pytest

# ── the "app" under test: a tiny search endpoint over a pooled database ──
# You do not edit anything in this block. Your fixture swaps the two
# module-level names `embed_query` and `get_pool` for fakes.

async def embed_query(text):
    """The real one: slow network call. Tests must never reach it."""
    await asyncio.sleep(5)
    return [0.0] * 16


class _RealPool:
    def acquire(self):
        raise RuntimeError("no database in tests — the fixture did not patch get_pool")


async def get_pool():
    return _RealPool()


async def search(q):
    pool = await get_pool()
    vector = await embed_query(q)
    async with pool.acquire() as conn:
        rows = await conn.fetch(vector)
    return [{"id": r["id"], "content": r["content"]} for r in rows]


_ORIGINAL = (embed_query, get_pool)   # the test checks these come back


@pytest.fixture
def solve(monkeypatch: pytest.MonkeyPatch):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import sys

from _lib import rng


def _gen(r):
    n = r.randint(1, 4)
    rows = [{"id": r.randint(1, 500), "content": f"chunk {r.randint(1, 99)}"} for _ in range(n)]
    return rows, r.choice(["storage", "billing setup", "auth"])


def _reference(monkeypatch):
    class FakePool:
        def __init__(self, rows):
            self.rows = rows

        def acquire(self):
            return self

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            pass

        async def fetch(self, vector):
            return self.rows

    async def fake_embed(text):
        return [0.0] * 16

    def run(rows, q):
        async def fake_get_pool():
            return FakePool(rows)

        mod = sys.modules[__name__]
        monkeypatch.setattr(mod, "embed_query", fake_embed)
        monkeypatch.setattr(mod, "get_pool", fake_get_pool)
        return asyncio.run(search(q))

    return run


def test_solve(solve):
    r = rng()
    for _ in range(3):
        rows, q = _gen(r)
        got = solve(rows, q)
        assert got == [{"id": x["id"], "content": x["content"]} for x in rows]
    mod = sys.modules[__name__]
    assert mod.embed_query is not _ORIGINAL[0], "embed_query was not patched"
    assert mod.get_pool is not _ORIGINAL[1], "get_pool was not patched"


def test_originals_restored_after_fixture():
    mod = sys.modules[__name__]
    assert (mod.embed_query, mod.get_pool) == _ORIGINAL, (
        "the fakes leaked: patch through monkeypatch so pytest restores them"
    )
