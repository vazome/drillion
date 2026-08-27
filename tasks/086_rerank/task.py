def solve(query: str, rows: list[dict[str, int | str]], k: int):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import re

from _lib import rng

_TOPICS = ["billing", "authentication", "networking", "deployment", "monitoring",
           "storage", "search", "caching", "security", "onboarding"]
_SUBS = ["configuration", "troubleshooting", "best practices", "migration",
         "performance", "error handling", "setup", "integration"]


def _gen(r):
    rows = []
    for i in range(r.randint(8, 20)):
        t, s = r.choice(_TOPICS), r.choice(_SUBS)
        punct = r.choice(["", ".", ",", ":"])
        rows.append({"id": i + 1, "content": f"{t.title()} {s}{punct} notes for {r.choice(_TOPICS)}"})
    query = f"{r.choice(_TOPICS)} {r.choice(_SUBS)}" + r.choice(["", "?", "!"])
    return query, rows, r.randint(1, 6)


def _tokens(text):
    return set(re.sub(r"[^\w\s]", "", text.lower()).split())


def _reference(query, rows, k):
    q = _tokens(query)

    def score(content):
        return len(q & _tokens(content)) / len(q) if q else 0.0

    return sorted(rows, key=lambda r: score(r["content"]), reverse=True)[:k]


def test_solve():
    r = rng()
    for _ in range(5):
        query, rows, k = _gen(r)
        assert solve(query, list(rows), k) == _reference(query, rows, k)
    # the crafted case from the docstring: vector order 1,2,3 must become 2,3
    rows = [{"id": 1, "content": "billing setup"},
            {"id": 2, "content": "storage best practices guide"},
            {"id": 3, "content": "storage migration"}]
    assert [x["id"] for x in solve("storage best practices", rows, 2)] == [2, 3]
    assert [x["id"] for x in solve("", rows, 2)] == [1, 2], "empty query: all 0.0, keep order"
    assert [x["id"] for x in solve("zzz", rows, 5)] == [1, 2, 3], "no matches: keep order, all rows"
