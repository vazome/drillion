"""Whole-task drill: the three warm-ups that open half of all phone screens.

Combines topics 28 (str methods), 19 (Counter), 22 (sets and sorting).
"""

from _lib import rng

META = {"topic": 82, "title": "DRILL: palindrome, anagram, top-N words",
        "tier": 4, "minutes": 30, "prereqs": [19],
        "practices": [28, 19, 22], "tags": ["whole-task"]}


def solve(phrase, pair, text, n):
    """WHY: Many phone screens for ops roles open with two or three tiny
    warm-up questions before the real work: is this phrase the same read
    backwards, are these two words made of the same letters, what are the
    most common words in this text. They are not about the job; they check
    that you can state a rule clearly and then write it. Here all three are
    bundled into one function so you can practise them together.

    YOU GET: `phrase` — a string like "Nurses, run." to test for reading the
    same backwards.

    `pair` — two strings packed together, like ("Dirty room", "Dormitory"),
    to test whether they use the same letters.

    `text` — a string of words like "pod pod, POD deploy Deploy node".

    `n` — a whole number, like 2: how many of the most common words to
    report. The test builds all four and hands them to you.

    YOU RETURN: a dictionary with three keys: "palindrome" (True or False),
    "anagram" (True or False) and "top_words" (a list of (word, count)
    pairs, most common first).

    ─── exact rules ───
    Three small questions, one dict back:

        {"palindrome": True,
         "anagram": True,
         "top_words": [("pod", 3), ("deploy", 2)]}

    palindrome — is `phrase` the same read backwards, ignoring case and
        anything that is not a letter or a digit.

            "Nurses, run."  ->  True

    anagram — `pair` is (a, b). Same letters rearranged, ignoring case and
        spaces.

            ("Dirty room", "Dormitory")  ->  True

    top_words — the n most common words in `text`. Lowercase them and
        strip the characters .,!?;:'" off both ends of each word. Sort by
        count descending, then by the word alphabetically, so the answer
        never depends on which word you happened to see first. Return
        (word, count) tuples.

            "pod pod, POD deploy Deploy node", 2
            ->  [("pod", 3), ("deploy", 2)]

    Each one is five lines. The grading here is on how cleanly you say the
    rule before you write it, so narrate all three out loud.
    """
    raise NotImplementedError


HINTS = [
    ("Three unrelated questions, so resist making them share code. Every one "
    "is the same two beats: normalise, then compare. Every bug lives in the "
    "normalise beat — which characters you drop, and whether you dropped them "
    "on both sides."),
    ("Palindrome: build a cleaned string with a comprehension over phrase "
    "keeping c.isalnum(), lowercased, then compare it to s[::-1]. Anagram: "
    "sorted() of each side, lowercased with spaces removed, and compare the "
    "two lists. Top words: Counter over text.lower().split() with "
    "w.strip('.,!?;:\\'\"') on each word, then sorted(counts.items(), "
    "key=lambda kv: (-kv[1], kv[0]))[:n] — most_common would leave ties in "
    "whatever order they arrived."),
    ("Different data, both normalising moves:\n"
    "    from collections import Counter\n"
    "    words = [w.strip('.,;') for w in 'Red, red; blue GREEN green red'.lower().split()]\n"
    "    counts = Counter(words)\n"
    "    print(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:2])\n"
    "    # [('red', 3), ('green', 2)]\n"
    "\n"
    "    s = ''.join(c.lower() for c in 'Ab, ba.' if c.isalnum())\n"
    "    print(s, s == s[::-1])          # abba True\n"
    "    print(sorted('cat') == sorted('act'))    # True\n"
    "Note the sort key: minus the count sorts big first, the word sorts A to "
    "Z, one pass."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

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
