def solve(fetch_page):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r, single=False):
    """Page contents and cursors. `single` forces the one-page case."""
    n = 1 if single else r.randint(1, 5)
    kinds = ["pod", "job", "node", "volume"]
    pages = []
    for i in range(n):
        empty = r.random() < 0.2 and i < n - 1      # an empty middle page
        count = 0 if empty else r.randint(1, 4)
        pages.append([f"{r.choice(kinds)}-{r.randint(100, 999)}" for _ in range(count)])
    cursors = [f"cur-{r.randrange(16 ** 4):04x}" for _ in range(n - 1)]
    return pages, cursors


def _api(pages, cursors):
    """Build a fetch_page(cursor) over those pages, plus a call counter."""
    lookup = {}
    for i, items in enumerate(pages):
        here = None if i == 0 else cursors[i - 1]
        lookup[here] = {"items": list(items),
                        "next": cursors[i] if i < len(cursors) else None}
    calls = {"n": 0}

    def fetch_page(cursor):
        calls["n"] += 1
        if calls["n"] > len(pages) + 3:
            raise AssertionError("fetch_page called far too often — the loop never ends")
        if cursor not in lookup:
            raise AssertionError(f"no such cursor: {cursor!r}")
        return dict(lookup[cursor])

    return fetch_page, calls


def _reference(fetch_page):
    items = []
    cursor = None
    while True:
        page = fetch_page(cursor)
        items.extend(page["items"])
        cursor = page["next"]
        if cursor is None:
            return items


def test_solve():
    r = rng()
    for i in range(4):
        pages, cursors = _gen(r, single=(i == 0))
        flat = [item for page in pages for item in page]

        mine, my_calls = _api(pages, cursors)
        got = solve(mine)
        assert got == flat

        theirs, their_calls = _api(pages, cursors)
        assert got == _reference(theirs)
        assert my_calls["n"] == their_calls["n"] == len(pages)
