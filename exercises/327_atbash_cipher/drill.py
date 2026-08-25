def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from string import ascii_lowercase

from _lib import rng

_MIRROR = str.maketrans(ascii_lowercase, ascii_lowercase[::-1])
_BLOCK = 5

_WORDS = ["truth", "is", "fiction", "the", "quick", "brown", "fox", "jumps", "over",
          "lazy", "dog", "testing", "exercism", "obstacle", "often", "stepping",
          "stone", "mindblowingly", "yes", "no", "omg", "x123", "42", "deep",
          "thought", "anagram", "puzzle", "cipher"]
_JOINERS = [" ", ", ", "  ", ". ", "! ", " - ", "'", "?  ", "; "]


def _gen(r):
    words = []
    for _ in range(r.randint(2, 8)):
        word = r.choice(_WORDS)
        roll = r.random()
        if roll < 0.15:
            word = word.upper()
        elif roll < 0.30:
            word = word.capitalize()
        words.append(word)
    text = words[0]
    for word in words[1:]:
        text += r.choice(_JOINERS) + word
    if r.random() < 0.4:
        text += r.choice([".", "!", " ", "?!"])
    return text


def _transcode(text):
    return "".join(char for char in text if char.isalnum()).lower().translate(_MIRROR)


def _reference():
    def encode(plain_text):
        cipher = _transcode(plain_text)
        return " ".join(cipher[start:start + _BLOCK]
                        for start in range(0, len(cipher), _BLOCK))

    def decode(ciphered_text):
        return _transcode(ciphered_text)

    return {"encode": encode, "decode": decode}


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    for _ in range(6):
        text = _gen(r)
        assert got["encode"](text) == want["encode"](text), f"encode {text!r}"
        ciphered = want["encode"](text)
        assert got["decode"](ciphered) == want["decode"](ciphered), f"decode {ciphered!r}"

    # canonical cases (exercism/python practice/atbash-cipher)
    assert got["encode"]("yes") == "bvh"
    assert got["encode"]("no") == "ml"
    assert got["encode"]("OMG") == "lnt"
    assert got["encode"]("O M G") == "lnt"
    assert got["encode"]("mindblowingly") == "nrmwy oldrm tob"
    assert got["encode"]("Testing,1 2 3, testing.") == "gvhgr mt123 gvhgr mt"
    assert got["encode"]("Truth is fiction.") == "gifgs rhurx grlm"
    assert got["encode"]("The quick brown fox jumps over the lazy dog.") == (
        "gsvjf rxpyi ldmul cqfnk hlevi gsvoz abwlt")
    assert got["decode"]("vcvix rhn") == "exercism"
    assert got["decode"]("zmlyh gzxov rhlug vmzhg vkkrm thglm v") == (
        "anobstacleisoftenasteppingstone")
    assert got["decode"]("gvhgr mt123 gvhgr mt") == "testing123testing"
    assert got["decode"]("vc vix    r hn") == "exercism"
    assert got["decode"]("zmlyhgzxovrhlugvmzhgvkkrmthglmv") == (
        "anobstacleisoftenasteppingstone")
