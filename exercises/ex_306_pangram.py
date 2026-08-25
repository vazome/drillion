"""pangram — does the sentence use all 26 letters? A subset check, not 26 ifs."""
# SOURCE: exercism/python practice/pangram (MIT, adapted)
# READ FIRST:
#   https://docs.python.org/3/library/stdtypes.html#set  — sets, and `<=` / issubset: "is
#       everything I need in there?"
#   https://docs.python.org/3/library/string.html#string.ascii_lowercase  — the alphabet as a
#       ready-made constant, so you never type it out
#   https://docs.python.org/3/library/functions.html#all  — all(), the other way to say the
#       same thing

from string import ascii_lowercase

from _lib import rng

META = {"topic": 306, "title": "pangram — a sentence that uses every letter", "minutes": 10,
        "prereqs": [200, 203, 209, 215], "tags": ["exercism", "strings", "core"]}


def solve(sentence):
    """WHY: A shop that sells fonts wants a different sample sentence each
    time someone previews a typeface, and every sample has to show off all
    26 letters — otherwise a customer never sees what the font's "q" looks
    like. Sentences are crowdsourced, so submissions need screening. The
    check itself ("does this thing contain everything on my required
    list?") is the same one you run against required config keys or
    required IAM permissions.

    YOU GET: `sentence` — a string, e.g. "the quick brown fox jumps over
    the lazy dog". It may be empty and may contain digits, underscores,
    punctuation and mixed case.

    YOU RETURN: `True` if every letter of the English alphabet appears at
    least once, `False` otherwise. A real boolean.

    ─── exact rules ───
    Case does not matter: "K" counts as "k". Only the 26 English letters
    matter — digits, punctuation and underscores are neither required nor
    a problem, and a letter appearing many times is no better than once.
    An empty sentence is not a pangram.

        solve("the quick brown fox jumps over the lazy dog")   ->  True
        solve("the_quick_brown_fox_jumps_over_the_lazy_dog")   ->  True
        solve("five boxing wizards jump quickly at it")        ->  False  (no "h")
        solve("abcdefghijklm ABCDEFGHIJKLM")                   ->  False  (13 letters twice)
    """
    raise NotImplementedError


HINTS = [
    ("You are asking one question 26 times: 'did the sentence contain this "
    "letter?'. Rather than write it 26 times, make one collection of what the "
    "sentence contains and one of what it must contain, and compare them in a "
    "single step."),
    ("Fold the sentence to a single case, then turn it into a set of characters "
    "— duplicates and punctuation stop mattering the moment you do. "
    "`string.ascii_lowercase` is the 26 letters, ready made. Sets answer 'is "
    "every item of A also in B?' directly with `<=` (or `.issubset`); `all()` "
    "with a generator says the same thing one letter at a time."),
    ("Different data, same check — validating a config:\n"
    "    required = {'host', 'port', 'token'}\n"
    "    required <= set(config)   ->  True when nothing is missing\n"
    "Extra keys in `config` are irrelevant, exactly as extra punctuation is "
    "irrelevant to a pangram."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    base = r.choice(["the quick brown fox jumps over the lazy dog",
                     "pack my box with five dozen liquor jugs",
                     "five quacking zephyrs jolt my wax bed",
                     "how vexingly quick daft zebras jump",
                     "a quick movement of the enemy will jeopardize five gunboats"])
    if r.random() < 0.5:                       # knock a letter out, or replace it with a digit
        base = base.replace(r.choice(ascii_lowercase), r.choice(["", "3", "_", "7"]))
    if r.random() < 0.4:
        base = base.replace(" ", r.choice(["_", "  "]))
    if r.random() < 0.4:
        base = "".join(c.upper() if r.random() < 0.3 else c for c in base)
    if r.random() < 0.3:
        base = f'"{base}." {r.randrange(10)}'
    return base


def _reference(sentence):
    return set(ascii_lowercase) <= set(sentence.lower())


def test_solve():
    r = rng()
    for _ in range(6):
        sentence = _gen(r)
        assert solve(sentence) == _reference(sentence), f"sentence {sentence!r}"

    # canonical cases (exercism/python practice/pangram)
    assert solve("") is False
    assert solve("abcdefghijklmnopqrstuvwxyz") is True
    assert solve("the quick brown fox jumps over the lazy dog") is True
    assert solve("five boxing wizards jump quickly at it") is False
    assert solve('"Five quacking Zephyrs jolt my wax bed."') is True
    assert solve("abcdefghijklm ABCDEFGHIJKLM") is False
