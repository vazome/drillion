"""Every list API caps the page size, so "get all of them" is always a loop."""

from _lib import rng

META = {"topic": 49, "title": "pagination — follow the cursor until it runs out",
        "tier": 3, "minutes": 12, "prereqs": [], "tags": ["http"]}


def solve(fetch_page):
    """WHY: An ops engineer needs a list of every pod in a cluster for a
    capacity report. The cluster's API never hands back the whole list at
    once: each answer holds a handful of items plus a bookmark (called a
    cursor) that you send back to get the next batch. Miss a batch and the
    report silently under-counts; keep asking after the last batch and the
    API refuses. The task: fetch batch after batch until the API says there
    are no more, and glue all the items into one list.

    YOU GET: `fetch_page` — a function that takes a cursor (None for the
    first call) and returns a dict like {"items": ["pod-4", "pod-9"],
    "next": "cur-3f1a"}, where "next" is the cursor for the following batch,
    or None when there are no more. The test hands in a stand-in over
    made-up batches, counts how many times you call it, and blows up if you
    call it too often; no real API is contacted.

    YOU RETURN: one flat list of every item from every batch, in the order
    they arrived, like ["pod-4", "pod-9", "pod-2"].

    ─── exact rules ───
    Collect every item the API will give you, across all pages.

    `fetch_page(cursor)` is one API call. Pass None to get the first
    page. It answers with a dict:

        {"items": ["pod-4", "pod-9"], "next": "cur-3f1a"}

    "next" is the cursor for the following page, or None when there are
    no more pages. Return one flat list of all items, in the order the
    pages handed them over.

        fetch_page(None)   -> {"items": ["a", "b"], "next": "c1"}
        fetch_page("c1")   -> {"items": [],         "next": "c2"}
        fetch_page("c2")   -> {"items": ["c"],      "next": None}
        ->  ["a", "b", "c"]

    Rules:
      - Call fetch_page exactly once per page, no more. The fake blows
        up if you keep calling after the cursor is spent.
      - Do not stop on an empty items list. Emptiness is not the end
        signal; "next": None is. A page can be empty and still point at
        a page that is not.
      - Some responses have one page and nothing else. That still works
        with the same loop.
    """
    raise NotImplementedError


HINTS = [
    ("You cannot know how many pages there are before you start, so a `for` "
    "over a range is out — this is a while loop. Two things have to survive "
    "from one turn of the loop to the next: the cursor you will send on the "
    "next call, and the list you are accumulating into. The server owns the "
    "stop condition, not you."),
    ("cursor = None and items = [] before the loop. Then `while True:` call "
    "fetch_page(cursor), items.extend(page['items']) — extend, not append, "
    "or you get a list of lists — then cursor = page['next'] and break when "
    "it is None. An alternative shape is `while cursor is not None:` with the "
    "first call pulled out above it; the break version avoids that duplicate."),
    ("Different data — walking a chain of jobs where each one names the next:\n"
    "    chain = {None: ('a', 1), 1: ('b', 2), 2: ('c', None)}\n"
    "    out, key = [], None\n"
    "    while True:\n"
    "        value, key = chain[key]\n"
    "        out.append(value)\n"
    "        if key is None:\n"
    "            break\n"
    "    print(out)      # ['a', 'b', 'c']\n"
    "Identical shape: each response carries both the data and the pointer "
    "you need for the next call."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

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
