def solve(subtitle):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import re
from collections import Counter

from _lib import rng

_WORD = re.compile(r"[a-z0-9]+(?:'[a-z]+)?")

_WORDS = ["word", "one", "of", "each", "fish", "two", "red", "blue", "testing", "go",
          "stop", "don't", "you're", "can't", "joe", "large", "apple", "app", "and",
          "romance", "123", "42", "the", "first", "laugh", "cry", "getting", "it"]
_SEPARATORS = [" ", ", ", ",\n", "   ", "\t", ": ", "! ", " '", "' ", "?\n", "_",
               "&@$%^& ", ". ", " - "]


def _gen(r):
    words = []
    for _ in range(r.randint(3, 12)):
        word = r.choice(_WORDS)
        if r.random() < 0.3:
            word = word.upper() if r.random() < 0.5 else word.capitalize()
        words.append(word)
    text = words[0]
    for word in words[1:]:
        text += r.choice(_SEPARATORS) + word
    if r.random() < 0.4:
        text = r.choice(["'", " ", ",\n", "''"]) + text + r.choice(["'", ".", "!!", " "])
    return text


def _reference(subtitle):
    return dict(Counter(match.group(0) for match in _WORD.finditer(subtitle.lower())))


def test_solve():
    r = rng()
    for _ in range(6):
        subtitle = _gen(r)
        assert solve(subtitle) == _reference(subtitle), f"subtitle {subtitle!r}"

    # canonical cases (exercism/python practice/word-count)
    assert solve("word") == {"word": 1}
    assert solve("one fish two fish red fish blue fish") == {
        "one": 1, "fish": 4, "two": 1, "red": 1, "blue": 1}
    assert solve("car: carpet as java: javascript!!&@$%^&") == {
        "car": 1, "carpet": 1, "as": 1, "java": 1, "javascript": 1}
    assert solve("testing, 1, 2 testing") == {"testing": 2, "1": 1, "2": 1}
    assert solve("go Go GO Stop stop") == {"go": 3, "stop": 2}
    assert solve("can, can't, 'can't'") == {"can": 1, "can't": 2}
    assert solve("hey,my_spacebar_is_broken") == {
        "hey": 1, "my": 1, "spacebar": 1, "is": 1, "broken": 1}
