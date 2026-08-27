def solve(phrase: str, pair: tuple[str, str], text: str, n: int):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    palindromes = ["Never odd or even", "A man, a plan, a canal: Panama",
                   "No lemon, no melon", "Was it a car or a cat I saw",
                   "Step on no pets"]
    plain = ["deploy the pods", "rollback finished", "node not ready",
             "scale up the queue", "drain and evict"]
    phrase = r.choice(palindromes if r.random() < 0.5 else plain)

    a, b = r.choice([("Dirty room", "Dormitory"), ("Listen", "Silent"),
                     ("The eyes", "They see"), ("Astronomer", "Moon starer")])
    if r.random() < 0.5:
        b = b[:-1] + r.choice("xyz")        # one letter off, no longer a match

    vocab = ["pod", "deploy", "node", "sync", "drain", "evict", "restart"]
    words = []
    for _ in range(r.randint(12, 25)):
        w = r.choice(vocab)
        if r.random() < 0.3:
            w = w.upper() if r.random() < 0.5 else w + r.choice(".,;:?")
        words.append(w)
    return phrase, (a, b), " ".join(words), r.randint(2, 4)


def _reference(phrase, pair, text, n):
    from collections import Counter

    def letters(s):
        return sorted(s.lower().replace(" ", ""))

    clean = "".join(c.lower() for c in phrase if c.isalnum())
    counts = Counter(w.strip(".,!?;:'\"") for w in text.lower().split())
    top = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:n]
    return {"palindrome": clean == clean[::-1],
            "anagram": letters(pair[0]) == letters(pair[1]),
            "top_words": top}


def test_solve():
    r = rng()
    for _ in range(4):
        phrase, pair, text, n = _gen(r)
        got = dict(solve(phrase, pair, text, n))
        got["top_words"] = [tuple(row) for row in got["top_words"]]
        assert got == _reference(phrase, pair, text, n)
