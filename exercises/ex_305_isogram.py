"""isogram — no letter twice: the set-length trick for spotting duplicates."""
# SOURCE: exercism/python practice/isogram (MIT, adapted)
# READ FIRST:
#   https://docs.python.org/3/library/stdtypes.html#str.isalpha  — isalpha() and lower(), the
#       two methods that decide which characters count here
#   https://docs.python.org/3/library/stdtypes.html#set  — a set keeps one copy of each item;
#       its length is therefore "how many distinct things did I see"
#   https://realpython.com/python-strings/  — walking a string character by character

from _lib import rng

META = {"topic": 305, "title": "isogram — a word with no repeated letter", "minutes": 10,
        "prereqs": [215], "tags": ["exercism", "strings", "core"]}


def solve(phrase):
    """WHY: A crossword setter keeps a list of "non-pattern words" — words
    in which no letter appears twice — and submissions arrive from the
    public, so somebody has to screen them. Underneath the word game is the
    duplicate check you will run for the rest of your career: are these ids
    unique, did this CSV column repeat a key, did two hosts claim the same
    address. The measuring trick is always the same one.

    YOU GET: `phrase` — a word or phrase, e.g. "six-year-old". It may be
    empty, may mix upper and lower case, and may contain spaces and hyphens.

    YOU RETURN: `True` if no letter repeats, `False` if one does. A real
    boolean.

    ─── exact rules ───
    Only letters are compared, and case is ignored: "Alphabet" is not an
    isogram because of its two a's. Everything that is not a letter —
    spaces, hyphens, digits, punctuation — may repeat as often as it likes
    and never makes the answer False. An empty phrase is an isogram.

        solve("lumberjacks")          ->  True
        solve("six-year-old")         ->  True   (hyphen repeats, letters do not)
        solve("Alphabet")             ->  False  ('A' and 'a' are the same letter)
        solve("up-to-date")           ->  False  ('t' appears twice)
    """
    raise NotImplementedError


HINTS = [
    ("Two separate questions here. First, which characters are even in the game "
    "— the hyphens in 'six-year-old' repeat and that is fine. Second, how do you "
    "notice a repeat at all? Think about a container that refuses to hold the "
    "same thing twice."),
    ("Collect the characters that count — the alphabetic ones, all folded to a "
    "single case — into a list. Then compare how many you collected with how "
    "many *distinct* ones you collected. If those two numbers differ, some "
    "letter turned up more than once. `str.isalpha()` answers 'is this "
    "character a letter?' for one character at a time."),
    ("Different data, same trick — checking a CSV column for duplicate ids:\n"
    "    ids = ['a1', 'b2', 'a1']\n"
    "    len(set(ids)) != len(ids)   ->  True, so there is a duplicate\n"
    "The set throws away the repeats; the length difference is what tells you "
    "they existed."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    pool = ["lumberjacks", "background", "downstream", "subdermatoglyphic", "isograms",
            "eleven", "accentor", "angola", "alphabet", "thumbscrew-japingly", "zzyzx",
            "thumbscrew-jappingly", "six-year-old", "up-to-date", "emily jung schwartzkopf", ""]
    word = r.choice(pool)
    if r.random() < 0.5:
        word = "".join(c.upper() if r.random() < 0.3 else c for c in word)
    if r.random() < 0.25:
        word = f"{word} {r.randrange(100)}"
    return word


def _reference(phrase):
    letters = [char.lower() for char in phrase if char.isalpha()]
    return len(set(letters)) == len(letters)


def test_solve():
    r = rng()
    for _ in range(6):
        phrase = _gen(r)
        assert solve(phrase) == _reference(phrase), f"phrase {phrase!r}"

    # canonical cases (exercism/python practice/isogram)
    assert solve("") is True
    assert solve("isogram") is True
    assert solve("eleven") is False
    assert solve("subdermatoglyphic") is True
    assert solve("Alphabet") is False
    assert solve("six-year-old") is True
