"""anagram — same letters, different order: fingerprint a word and compare."""
# SOURCE: exercism/python practice/anagram (MIT, adapted)
# READ FIRST:
#   https://docs.python.org/3/howto/sorting.html  — sorted(), which turns any iterable into a
#       list in a fixed order — including a string, character by character
#   https://docs.python.org/3/tutorial/datastructures.html#more-on-lists  — list methods and
#       list comprehensions, the shape this answer wants
#   https://docs.python.org/3/library/collections.html#collections.Counter  — the other
#       fingerprint: how many of each item

from _lib import rng

META = {"topic": 307, "title": "anagram — pick the rearrangements out of a word list",
        "minutes": 10, "prereqs": [200, 203, 209, 215, 218, 221, 224, 227],
        "tags": ["exercism", "list-methods", "core"]}


def solve(word, candidates):
    """WHY: A daily word game ships a target word and a pile of guesses,
    and the server has to say which guesses are true rearrangements of it.
    Two rules trip people up: the comparison ignores capitals ("Silent"
    counts for "LISTEN") but the answer must give the guess back spelled
    exactly as it arrived, and a word is never an anagram of itself no
    matter how it is capitalised. The general skill is turning a value into
    a comparable fingerprint — the same move behind deduplicating records
    and grouping like with like.

    YOU GET:
      `word`       — the target word, e.g. "listen"
      `candidates` — a list of words to check, e.g.
                     ["enlists", "google", "inlets", "banana"]

    YOU RETURN: a list of the candidates that are anagrams of the target,
    in the order they appeared in `candidates`, each spelled exactly as it
    was given to you. No matches means an empty list.

    ─── exact rules ───
    A candidate matches when it uses exactly the same letters as the
    target, each the same number of times — no letter left over on either
    side. Case is ignored when comparing. A candidate that *is* the target
    word (ignoring case) never counts.

        solve("stone", ["stone", "tones", "banana", "notes", "Seton"])
            ->  ["tones", "notes", "Seton"]     ("stone" is itself, so it is out)
        solve("good", ["dog", "goody"])
            ->  []                              (subsets and supersets do not count)
        solve("BANANA", ["Banana"])
            ->  []
    """
    raise NotImplementedError


HINTS = [
    ("Two words are anagrams when they hold the same letters in the same "
    "quantities — order is exactly what you must stop caring about. So find a "
    "way to boil a word down to something that is equal for any rearrangement "
    "of it, then compare those. One extra rule then removes the target itself."),
    ("`sorted(some_string)` gives you its characters in a fixed order, so any "
    "rearrangement produces the same list — lower-case the word first so "
    "capitals stop mattering. Compute the target's version once outside the "
    "loop, then keep each candidate whose version matches AND whose lower-cased "
    "spelling is not the target's. Keep the candidate's original spelling in "
    "what you return."),
    ("Different data, same idea — grouping receipts that hold the same items:\n"
    "    sorted(('milk', 'eggs')) == sorted(('eggs', 'milk'))   ->  True\n"
    "Counter answers the same question and also keeps the counts, which is why "
    "it is the honest tool when duplicates matter:\n"
    "    Counter('aab') == Counter('aba')  ->  True\n"
    "    Counter('aab') == Counter('ab')   ->  False"),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    families = [("listen", ["silent", "enlist", "tinsel", "inlets"]),
                ("stone", ["tones", "notes", "seton"]),
                ("allergy", ["gallery", "regally", "largely"]),
                ("solemn", ["lemons", "melons"]),
                ("orchestra", ["carthorse"]),
                ("nose", ["eons", "ones"])]
    distractors = ["banana", "google", "cherry", "radishes", "dog", "goody", "patter",
                   "last", "mass", "clergy", "leading", "cashregister", "zombies"]
    word, mates = r.choice(families)
    picked = (r.sample(mates, r.randint(1, len(mates)))
              + r.sample(distractors, r.randint(1, 3))
              + [word])
    cased = [w.upper() if r.random() < 0.3 else w.capitalize() if r.random() < 0.3 else w
             for w in picked]
    r.shuffle(cased)
    return (word.upper() if r.random() < 0.5 else word), cased


def _reference(word, candidates):
    target = word.lower()
    letters = sorted(target)
    return [candidate for candidate in candidates
            if candidate.lower() != target and sorted(candidate.lower()) == letters]


def test_solve():
    r = rng()
    for _ in range(5):
        word, candidates = _gen(r)
        assert solve(word, list(candidates)) == _reference(word, candidates), f"word {word}"

    # canonical cases (exercism/python practice/anagram)
    assert solve("diaper", ["hello", "world", "zombies", "pants"]) == []
    assert solve("solemn", ["lemons", "cherry", "melons"]) == ["lemons", "melons"]
    assert solve("listen", ["enlists", "google", "inlets", "banana"]) == ["inlets"]
    assert solve("good", ["dog", "goody"]) == []
    assert solve("nose", ["Eons", "ONES"]) == ["Eons", "ONES"]
    assert solve("BANANA", ["Banana"]) == []
