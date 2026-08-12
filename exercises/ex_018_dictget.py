"""Counting into a dict by hand — the KeyError that bites every beginner."""

from _lib import rng

META = {"topic": 18, "title": "dict.get — count without KeyError", "tier": 2,
        "minutes": 8, "prereqs": []}


def solve(words):
    """Count how many times each word appears. Return a plain dict.

        ["a", "b", "a"]  ->  {"a": 2, "b": 1}

    Do it with a loop and a dict — no Counter here. This is the version
    interviewers make you write when they say "without imports".
    """
    raise NotImplementedError


HINTS = [
    "counts[word] += 1 explodes the first time a word appears, because += has "
    "to READ the old value before adding — and there isn't one yet.",
    "dict has a method that reads a key but returns a fallback instead of "
    "exploding when the key is missing. Look up `dict.get`.",
    "Different data, same shape:\n"
    "    tally = {}\n"
    "    for c in 'hello':\n"
    "        tally[c] = tally.get(c, 0) + 1\n"
    "    print(tally)     # {'h': 1, 'e': 1, 'l': 2, 'o': 1}\n"
    "The 0 is what .get hands back when the key is new.",
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    vocab = ["deploy", "rollback", "pod", "node", "sync", "drain", "evict"]
    return [r.choice(vocab) for _ in range(r.randint(8, 20))]


def _reference(words):
    counts = {}
    for w in words:
        counts[w] = counts.get(w, 0) + 1
    return counts


def test_solve():
    r = rng()
    for _ in range(4):
        words = _gen(r)
        assert solve(words) == _reference(words)
