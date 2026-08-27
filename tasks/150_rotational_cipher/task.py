def solve(text: str, key: int):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from string import ascii_lowercase, ascii_uppercase

from _lib import rng

_WORDS = ["the", "quick", "brown", "fox", "jumps", "over", "lazy", "dog", "omg",
          "cool", "testing", "Let's", "eat", "Grandma", "Zebra", "42", "v1",
          "deploy", "rollback", "Prod", "staging", "OMG", "hello", "World"]
_JOINERS = [" ", ", ", " - ", "! ", "? ", ". ", "  ", "; "]


def _gen(r):
    words = []
    for _ in range(r.randint(2, 8)):
        word = r.choice(_WORDS)
        roll = r.random()
        if roll < 0.12:
            word = word.upper()
        elif roll < 0.24:
            word = word.capitalize()
        words.append(word)
    text = words[0]
    for word in words[1:]:
        text += r.choice(_JOINERS) + word
    if r.random() < 0.4:
        text += r.choice([".", "!", "?!", " "])
    key = r.choice([0, 26] + list(range(1, 26)))
    return text, key


def _reference(text, key):
    shifted = []
    for char in text:
        if char in ascii_lowercase:
            shifted.append(ascii_lowercase[(ascii_lowercase.index(char) + key) % 26])
        elif char in ascii_uppercase:
            shifted.append(ascii_uppercase[(ascii_uppercase.index(char) + key) % 26])
        else:
            shifted.append(char)
    return "".join(shifted)


def test_solve():
    r = rng()
    for _ in range(6):
        text, key = _gen(r)
        assert solve(text, key) == _reference(text, key), f"text {text!r} key {key}"

    # canonical cases (exercism/python practice/rotational-cipher)
    assert solve("a", 0) == "a"
    assert solve("a", 1) == "b"
    assert solve("a", 26) == "a"
    assert solve("m", 13) == "z"
    assert solve("n", 13) == "a"
    assert solve("OMG", 5) == "TRL"
    assert solve("O M G", 5) == "T R L"
    assert solve("Testing 1 2 3 testing", 4) == "Xiwxmrk 1 2 3 xiwxmrk"
    assert solve("Let's eat, Grandma!", 21) == "Gzo'n zvo, Bmviyhv!"
    assert solve("The quick brown fox jumps over the lazy dog.", 13) == (
        "Gur dhvpx oebja sbk whzcf bire gur ynml qbt.")
