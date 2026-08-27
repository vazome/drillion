def solve(message: str):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    body = r.choice(["tom-ay-to, tom-aaaah-to", "how are you", "1, 2, 3", "watch out",
                     "does this cryogenic chamber make me look fat", "fffbbcbeab", "4",
                     ":) ", "it's ok if you don't want to go work for nasa", "hmmmmmmm..."])
    if r.random() < 0.45:
        body = body.upper()
    if r.random() < 0.45:
        body += "?"
    if r.random() < 0.35:
        body = r.choice(["  ", "\t", "\n "]) + body + r.choice(["   ", "\t\t", "\n"])
    if r.random() < 0.15:
        body = r.choice(["", "   ", "\t\t\t\t", "\n\r \t"])
    return body


def _reference(message):
    text = message.strip()
    if not text:
        return "Fine. Be that way!"
    question = text.endswith("?")
    if text.isupper():
        return "Calm down, I know what I'm doing!" if question else "Whoa, chill out!"
    return "Sure." if question else "Whatever."


def test_solve():
    r = rng()
    for _ in range(6):
        message = _gen(r)
        assert solve(message) == _reference(message), f"message {message!r}"

    # canonical cases (exercism/python practice/bob)
    assert solve("Does this cryogenic chamber make me look fat?") == "Sure."
    assert solve("WATCH OUT!") == "Whoa, chill out!"
    assert solve("WHAT'S GOING ON?") == "Calm down, I know what I'm doing!"
    assert solve("\t\t\t\t\t\t\t\t\t\t") == "Fine. Be that way!"
    assert solve("1, 2, 3") == "Whatever."
    assert solve("Okay if like my  spacebar  quite a bit?   ") == "Sure."
