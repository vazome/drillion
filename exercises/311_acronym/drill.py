def solve(phrase):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_WORDS = ["portable", "network", "graphics", "ruby", "rails", "first", "in", "out",
          "complementary", "metal", "oxide", "semiconductor", "rolling", "floor",
          "laughing", "hard", "dogs", "came", "over", "licked", "thin", "air",
          "halley's", "comet", "road", "taken", "gnu", "image", "program", "as",
          "soon", "possible", "liquid", "crystal", "display", "thank", "george"]
_JOINERS = [" ", " ", " ", "-", ", ", " - ", " _", "_ ", "! ", ". "]


def _gen(r):
    words = []
    for _ in range(r.randint(2, 8)):
        word = r.choice(_WORDS)
        roll = r.random()
        if roll < 0.55:
            word = word.capitalize()
        elif roll < 0.7:
            word = word.upper()
        words.append(word)
    phrase = words[0]
    for word in words[1:]:
        phrase += r.choice(_JOINERS) + word
    if r.random() < 0.3:
        phrase += r.choice(["!", ".", "?", ""])
    return phrase


def _reference(phrase):
    kept = "".join(char if char.isalpha() or char == "'" else " " for char in phrase)
    return "".join(word[0].upper() for word in kept.replace("'", "").split())


def test_solve():
    r = rng()
    for _ in range(6):
        phrase = _gen(r)
        assert solve(phrase) == _reference(phrase), f"phrase {phrase!r}"

    # canonical cases (exercism/python practice/acronym)
    assert solve("Portable Network Graphics") == "PNG"
    assert solve("Ruby on Rails") == "ROR"
    assert solve("First In, First Out") == "FIFO"
    assert solve("GNU Image Manipulation Program") == "GIMP"
    assert solve("Complementary metal-oxide semiconductor") == "CMOS"
    assert solve("Something - I made up from thin air") == "SIMUFTA"
    assert solve("Halley's Comet") == "HC"
    assert solve("The Road _Not_ Taken") == "TRNT"
