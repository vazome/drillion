def solve(text: str):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import re

from _lib import rng

_VOWEL_SOUND = re.compile(r"^([aeiou]|y[^aeiou]|xr)")
_CONSONANT_RUN = re.compile(r"^([^aeiou]?qu|[^aeiouy]+|y(?=[aeiou]))([a-z]*)")

_WORDS = ["apple", "ear", "igloo", "object", "under", "equal", "into", "orange",
          "umbrella", "elephant", "pig", "koala", "chair", "thrush", "school",
          "therapy", "fast", "run", "strong", "glove", "twelve", "spring", "wrist",
          "queen", "square", "quick", "quiet", "qat", "liquid", "xenon", "xray",
          "yttria", "yellow", "yolk", "rhythm", "my", "style"]


def _gen(r):
    return " ".join(r.choice(_WORDS) for _ in range(r.randint(1, 6)))


def _translate_word(word):
    if _VOWEL_SOUND.match(word):
        return word + "ay"
    head, tail = _CONSONANT_RUN.match(word).groups()
    return tail + head + "ay"


def _reference(text):
    return " ".join(_translate_word(word) for word in text.split())


def test_solve():
    r = rng()
    for _ in range(6):
        text = _gen(r)
        assert solve(text) == _reference(text), f"text {text!r}"

    # canonical cases (exercism/python practice/pig-latin)
    assert solve("apple") == "appleay"
    assert solve("pig") == "igpay"
    assert solve("chair") == "airchay"
    assert solve("square") == "aresquay"
    assert solve("qat") == "atqay"
    assert solve("yttria") == "yttriaay"
    assert solve("rhythm") == "ythmrhay"
    assert solve("my") == "ymay"
    assert solve("quick fast run") == "ickquay astfay unray"
