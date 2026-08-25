"""Take-home Task 2 — retrieve wide, then rerank: fraction-of-query-words score, stable top-k."""
# READ FIRST:
#   https://www.pinecone.io/learn/series/rag/rerankers/  — read the first half: why a cheap wide
#       first stage + an expensive narrow second stage beats either alone
#   https://en.wikipedia.org/wiki/Precision_and_recall  — just the intro: recall = "did we fetch all
#       the relevant ones", precision = "is what we show actually relevant"
#   https://docs.python.org/3/howto/sorting.html  — key=, reverse=True, and 'Sort Stability':
#       equal scores keep their incoming order, which is how ties stay in vector order
#   https://docs.python.org/3/library/stdtypes.html#set  — `&` gives the words in both sets

import re

from _lib import rng

META = {"topic": 16, "title": "take-home Task 2 — rerank the candidate pool", "tier": 3,
        "minutes": 20, "prereqs": []}


def solve(query, rows, k):
    """WHY: Vector search returned the 5 geometrically nearest chunks, and
    they were often not the 5 best answers — two chunks can sit close in
    embedding space while only one actually contains the words the user
    typed. The fix was two stages: ask the database for 20 (cheap, wide,
    recall) and re-score those 20 against the query with a second function
    (narrow, precision), keeping the top 5. Your submission scored by raw
    count of overlapping words; here you use the FRACTION of the query's
    words found, which is the same idea but comparable across queries and
    bounded 0..1 — the improvement you would name in the interview.

    YOU GET:
      `query` — the user's text, e.g. "Storage best-practices"
      `rows`  — the candidate pool in vector-distance order: a list of dicts
                like {"id": 7, "content": "storage configuration: ..."}
      `k`     — how many to keep, e.g. 5

    YOU RETURN: a list of the top `k` rows (same dicts, unchanged), best
    score first; ties keep their incoming (vector) order.

    ─── exact rules ───
      - Tokenise both sides the same way: lowercase, remove everything that is
        not a letter, digit, underscore or whitespace, split on whitespace,
        and use a SET of words (repeats do not count).
      - score = (number of query words present in the chunk) / (number of
        distinct query words). An empty query scores 0.0 for every chunk.
      - Sort by score descending with a stable sort, take the first k. If
        fewer than k rows exist, return them all.

        query="storage best practices"
        rows=[{"id": 1, "content": "billing setup"},
              {"id": 2, "content": "storage best practices guide"},
              {"id": 3, "content": "storage migration"}]
        k=2   ->  [row 2 (score 1.0), row 3 (score 1/3)]
    """
    raise NotImplementedError


HINTS = [
    ("Write `_tokens(text)` first: `set(re.sub(r'[^\\w\\s]', '', text.lower()).split())`. "
    "Then score = len(q & c) / len(q) with a guard for an empty q. Then "
    "`sorted(rows, key=lambda r: score(...), reverse=True)[:k]`."),
    ("Why `sorted(..., reverse=True)` keeps ties in order: Python's sort is "
    "stable, and reverse=True still preserves the original order among equal "
    "keys (it is not the same as sorting then reversing). That is why the "
    "'all scores equal' test in your take-home came back in vector order."),
    ("SAY IT IN THE INTERVIEW: 'Stage one is recall-oriented: vector distance "
    "is cheap and fetches 20 plausible chunks. Stage two is precision-oriented: "
    "a per-chunk score against the actual query text reorders them and keeps "
    "5. The cost is 20 cheap scoring calls per request, paid to fix cases "
    "where embedding closeness and relevance disagree. I used raw overlap "
    "count; a fraction would be bounded and comparable across query lengths.'"),
]


# ─────────────────────────────  below here is the machinery  ──────────────

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
