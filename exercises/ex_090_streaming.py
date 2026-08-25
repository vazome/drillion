"""Streaming: tokens arrive one at a time, and you are allowed to stop pulling."""

from _lib import rng
from langchain_core.runnables import RunnableGenerator

META = {"topic": 90, "title": "streaming — accumulate tokens, stop at a sentinel",
        "tier": 3, "minutes": 15, "prereqs": [11], "tags": ["llm", "langchain"]}


def solve(model, prompt, sentinel):
    """WHY: LangChain is a library for wiring steps together around an AI
    model. When a chat assistant answers, the text arrives in small pieces
    (tokens) one after another, not as one finished block; that is why you
    see an answer "typing itself out". A company paying per token wants to
    stop reading the moment a special end marker appears, because every
    piece you never pull is one you never wait for or pay for.

    YOU GET: `model` — a stand-in for an AI model. Calling
    model.stream(prompt) gives you something you can loop over that hands
    out one piece of text at a time. The test's fake just replays a fixed
    list of pieces and counts how many you pulled; no real AI is called.

    `prompt` — the question to send, as a string like "why did it restart".

    `sentinel` — the end marker, as a string like "<END>".

    YOU RETURN: one string: all the pieces joined in order, up to but not
    including the marker.

    ─── exact rules ───
    A streaming model does not hand back a finished answer. `model.stream(prompt)`
    returns an iterator that yields small pieces of text — tokens — as they are
    produced, so you can print them or react to them before the model is done.

    Consume the stream and build the answer:

      - join the tokens together, in order, into one string
      - if a token is exactly equal to `sentinel`, stop there: leave the
        sentinel out of the result and pull nothing further from the iterator
      - if the sentinel never appears, the result is every token joined

        tokens "the ", "pod ", "<END>", "is ", "up"   with sentinel "<END>"
        ->  "the pod "

    Return the string. Nothing else.

    The test counts how many tokens the iterator actually produced, so
    collecting the lot and slicing afterwards fails. Stopping early means
    stopping the stream, not tidying up after it — that is most of the point
    of streaming, since tokens you never pull are tokens you never wait for
    and never pay for.
    """
    raise NotImplementedError


HINTS = [
    ("model.stream(...) is lazy: it does not hand you a list, it hands you "
    "something that produces the next token only when you ask for one. "
    "list(...) or a comprehension asks for all of them, which is exactly the "
    "behaviour being graded against — by the time you slice off the tail, the "
    "whole answer has already been generated."),
    ("A plain `for token in model.stream(prompt):` pulls one token per turn "
    "round the loop. Start with an empty string, add each token to it, and use "
    "`break` the moment a token equals the sentinel — break abandons the "
    "iterator where it stands. Return the accumulated string after the loop."),
    ("Different data — read a line-by-line feed and stop at a marker:\n"
    "    def feed():\n"
    "        for line in ['ok ', 'ok ', 'HALT', 'never ', 'reached']:\n"
    "            print('produced', line)\n"
    "            yield line\n"
    "\n"
    "    seen = ''\n"
    "    for line in feed():\n"
    "        if line == 'HALT':\n"
    "            break\n"
    "        seen += line\n"
    "    print(repr(seen))     # 'ok ok '\n"
    "The prints show 'produced' three times, not five — the last two lines "
    "were never generated at all."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

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
