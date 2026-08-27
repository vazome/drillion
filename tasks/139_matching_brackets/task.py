def solve(text: str):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_FILLER = ["", "", "", " ", "x", "42", "a + b", "185 + 223.85", "text", "\\mathrm e^x"]


def _balanced(r, depth):
    if depth <= 0 or r.random() < 0.4:
        return r.choice(_FILLER)
    opener, closer = r.choice(["()", "[]", "{}"])
    return f"{opener}{_balanced(r, depth - 1)}{closer}{_balanced(r, depth - 1)}"


def _gen(r):
    text = _balanced(r, r.randint(0, 3))
    if text and r.random() < 0.45:
        spot = r.randrange(len(text))
        text = text[:spot] + r.choice("([{}])") + text[spot + 1:]
    if r.random() < 0.25:
        text += r.choice("([{}])")
    return text


def _reference(text):
    partners = {")": "(", "]": "[", "}": "{"}
    stack = []
    for char in text:
        if char in "([{":
            stack.append(char)
        elif char in partners:
            opener = stack.pop() if stack else ""
            if opener != partners[char]:
                return False
    return not stack


def test_solve():
    r = rng()
    for _ in range(6):
        text = _gen(r)
        assert solve(text) == _reference(text), f"text {text!r}"

    # canonical cases (exercism/python practice/matching-brackets)
    assert solve("") is True
    assert solve("{[]}") is True
    assert solve("([{}({}[])])") is True
    assert solve("{[])") is False
    assert solve("[({]})") is False
    assert solve("[]]") is False
    assert solve("(((185 + 223.85) * 15) - 543)/2") is True
