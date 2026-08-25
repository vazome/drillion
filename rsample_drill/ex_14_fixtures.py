"""pytest fixtures + monkeypatch — the setup/teardown you copy-pasted six times."""
# READ FIRST:
#   https://realpython.com/pytest-python-testing/  — section 'Fixtures: Managing State and Dependencies'
#   https://docs.pytest.org/en/stable/how-to/fixtures.html  — read 'What fixtures are', then
#       'Factories as fixtures' (a fixture that RETURNS A FUNCTION — exactly what you build here)
#   https://docs.pytest.org/en/stable/how-to/monkeypatch.html  — setattr a fake in, and pytest
#       puts the real thing back after the test, automatically
#   https://docs.pytest.org/en/stable/how-to/fixtures.html#teardown-cleanup-aka-fixture-finalization

import asyncio
import sys

import pytest
from _lib import rng

META = {"topic": 14, "title": "fixtures — one setup, automatic restore", "tier": 4,
        "minutes": 25, "prereqs": []}


# ── the "app" under test: a tiny copy of the take-home's main.py ─────────
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
def solve(monkeypatch):
    """WHY: The take-home README said "use pytest fixtures to set up and tear
    down mocks". Your six endpoint tests each re-declared `fake_get_pool`,
    re-applied two `monkeypatch.setattr` lines, and re-built the HTTP client.
    It works, but a reviewer reads it as "does not know fixtures". A fixture
    is the one place that setup lives; every test that names it as an
    argument gets it, and pytest undoes the patching after each test on its
    own — no cleanup code, no leaking fakes into the next test.

    YOU GET: `monkeypatch` — pytest hands this in because you named it as a
    parameter. `monkeypatch.setattr(obj, "name", fake)` replaces `obj.name`
    until the test ends. This module is reachable as
    `sys.modules[__name__]`, so `monkeypatch.setattr(sys.modules[__name__],
    "embed_query", fake)` swaps the function that `search()` will call.

    YOU RETURN: a function `run(rows, q)` (the "factory" pattern) that:
      1. patches `embed_query` in this module with a fast fake returning any
         16-number list,
      2. patches `get_pool` in this module with an async fake returning a
         pool whose `acquire()` works in `async with` and whose conn's
         `fetch(vector)` returns `rows` (a FakePool from ex_11 is perfect),
      3. calls `search(q)` via `asyncio.run(...)` and returns its result.

    ─── exact rules ───
      - Replace `raise NotImplementedError` with the fixture body; keep the
        decorator and the `monkeypatch` argument.
      - Patch with `monkeypatch.setattr`, not by assigning to the globals —
        the second test in this file checks the originals were restored,
        and only monkeypatch does that for you.
      - `run` is a plain `def`; `asyncio.run` lives inside it.
    """
    raise NotImplementedError


HINTS = [
    ("Inside the fixture: define `async def fake_embed(text): return [0.0] * 16`, "
    "a small FakePool class (rows, acquire -> self, __aenter__/__aexit__, "
    "async fetch -> rows), and `def run(rows, q)` that patches both names with "
    "`monkeypatch.setattr(sys.modules[__name__], ...)` and returns "
    "`asyncio.run(search(q))`. Then `return run`."),
    ("Why return a function instead of a value: the test needs to choose `rows` "
    "and `q` per call. A fixture runs before the test and cannot take arguments "
    "from it — so it returns a callable that does. pytest docs call this "
    "'factories as fixtures'. Everything the callable patches is still undone "
    "at teardown because it went through `monkeypatch`."),
    ("SAY IT IN THE INTERVIEW: 'I should have put the two monkeypatch.setattr "
    "calls and the client construction in one fixture and taken it as a "
    "parameter in each test. Fixtures give one place for setup, automatic "
    "teardown — monkeypatch restores the originals after every test — and "
    "tests that only state the behaviour they check. Copy-pasting the setup "
    "six times is what the README's fixtures sentence was warning against.'"),
]


# ─────────────────────────────  below here is the machinery  ──────────────

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
