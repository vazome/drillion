---
title: fixtures — one setup, automatic restore
difficulty: medium
tier: advanced
track: rsample
minutes: 25
prereqs: [54]
tags: [testing, asyncio]
---
# fixtures — one setup, automatic restore

*pytest fixtures + monkeypatch — the setup/teardown you copy-pasted six times.*

## Why
The take-home README said "use pytest fixtures to set up and tear down mocks". Your six endpoint tests each re-declared `fake_get_pool`, re-applied two `monkeypatch.setattr` lines, and re-built the HTTP client. It works, but a reviewer reads it as "does not know fixtures". A fixture is the one place that setup lives; every test that names it as an argument gets it, and pytest undoes the patching after each test on its own — no cleanup code, no leaking fakes into the next test.

## You get
`monkeypatch` — pytest hands this in because you named it as a parameter. `monkeypatch.setattr(obj, "name", fake)` replaces `obj.name` until the test ends. This module is reachable as `sys.modules[__name__]`, so `monkeypatch.setattr(sys.modules[__name__], "embed_query", fake)` swaps the function that `search()` will call.

## You return
a function `run(rows, q)` (the "factory" pattern) that:

1. patches `embed_query` in this module with a fast fake returning any 16-number list,
2. patches `get_pool` in this module with an async fake returning a pool whose `acquire()` works in `async with` and whose conn's `fetch(vector)` returns `rows` (a FakePool from task 096 is perfect),
3. calls `search(q)` via `asyncio.run(...)` and returns its result.

## Rules
- Replace `raise NotImplementedError` with the fixture body; keep the decorator and the `monkeypatch` argument.
- Patch with `monkeypatch.setattr`, not by assigning to the globals.
- `run` is a plain `def`; `asyncio.run` lives inside it.

> [!WARNING]
> The second test in this file checks the originals were restored, and only `monkeypatch` does that for you — assigning to the globals directly would leak the fake into the next test.

## Read first
- [Fixtures: Managing State and Dependencies](https://realpython.com/pytest-python-testing/) — section 'Fixtures: Managing State and Dependencies'
- [How to use fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html) — read 'What fixtures are', then 'Factories as fixtures' (a fixture that RETURNS A FUNCTION — exactly what you build here)
- [How to use monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html) — setattr a fake in, and pytest puts the real thing back after the test, automatically
- [Teardown / cleanup, aka fixture finalization](https://docs.pytest.org/en/stable/how-to/fixtures.html#teardown-cleanup-aka-fixture-finalization)

> [!NOTE]
> **Take-home:** what the README asked and you skipped

## Hints
### Hint 1
Inside the fixture: define `async def fake_embed(text): return [0.0] * 16`, a small FakePool class (rows, acquire -> self, __aenter__/__aexit__, async fetch -> rows), and `def run(rows, q)` that patches both names with `monkeypatch.setattr(sys.modules[__name__], ...)` and returns `asyncio.run(search(q))`. Then `return run`.
### Hint 2
Why return a function instead of a value: the test needs to choose `rows` and `q` per call. A fixture runs before the test and cannot take arguments from it — so it returns a callable that does. pytest docs call this 'factories as fixtures'. Everything the callable patches is still undone at teardown because it went through `monkeypatch`.
### Hint 3
**Say it in the interview:**

> I should have put the two monkeypatch.setattr calls and the client construction in one fixture and taken it as a parameter in each test. Fixtures give one place for setup, automatic teardown — monkeypatch restores the originals after every test — and tests that only state the behaviour they check. Copy-pasting the setup six times is what the README's fixtures sentence was warning against.
