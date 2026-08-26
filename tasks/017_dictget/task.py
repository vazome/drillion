def solve(words):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


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
