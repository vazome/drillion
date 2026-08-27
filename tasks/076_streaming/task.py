from langchain_core.runnables import Runnable


def solve(model: Runnable[str, str], prompt: str, sentinel: str):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng
from langchain_core.runnables import RunnableGenerator


def _gen(r):
    """One batch of cases. Every awkward position of the sentinel appears each
    seed — first token, last token, absent — while the text itself varies."""
    words = ["the ", "pod ", "restarted ", "after ", "a ", "node ", "drained ",
             "and ", "the ", "cert ", "rotated ", "cleanly ", "again "]
    prompts = ["why did it restart", "what happened", "explain the alert"]
    places = ["first", "last", "middle", "absent", r.choice(["middle", "absent"])]
    r.shuffle(places)

    cases = []
    for place in places:
        count = r.randint(4, 12)
        tokens = [r.choice(words) for _ in range(count)]
        sentinel = r.choice(["<END>", "[STOP]", "<|eot|>"])
        if place == "first":
            tokens.insert(0, sentinel)
        elif place == "last":
            tokens.append(sentinel)
        elif place == "middle":
            tokens.insert(r.randrange(1, count), sentinel)
        cases.append((tokens, sentinel, r.choice(prompts)))
    return cases


def _model(tokens, pulled):
    """A Runnable whose .stream() yields `tokens`, recording each one pulled."""
    def emit(inputs):
        for _ in inputs:
            for token in tokens:
                pulled.append(token)
                yield token
    return RunnableGenerator(emit)


def _reference(model, prompt, sentinel):
    text = ""
    for token in model.stream(prompt):
        if token == sentinel:
            break
        text += token
    return text


def test_solve():
    r = rng()
    for _ in range(2):
        for tokens, sentinel, prompt in _gen(r):
            pulled = []
            got = solve(_model(tokens, pulled), prompt, sentinel)
            want = _reference(_model(tokens, []), prompt, sentinel)
            assert got == want, f"got {got!r}, expected {want!r}"

            expected_pulls = (tokens.index(sentinel) + 1 if sentinel in tokens
                              else len(tokens))
            assert len(pulled) == expected_pulls, (
                f"the stream produced {len(pulled)} tokens; it should have "
                f"stopped after {expected_pulls}. Break out of the loop "
                f"instead of collecting everything first."
            )
