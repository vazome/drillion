---
title: streaming — accumulate tokens, stop at a sentinel
difficulty: medium
tier: packages
minutes: 15
prereqs: [7]
tags: [llm, langchain]
---
# streaming — accumulate tokens, stop at a sentinel

*Streaming: tokens arrive one at a time, and you are allowed to stop pulling.*

## Why
LangChain is a library for wiring steps together around an AI model. When a chat assistant answers, the text arrives in small pieces (tokens) one after another, not as one finished block; that is why you see an answer "typing itself out". A company paying per token wants to stop reading the moment a special end marker appears, because every piece you never pull is one you never wait for or pay for.

## You get
`model` — a stand-in for an AI model. Calling `model.stream(prompt)` gives you something you can loop over that hands out one piece of text at a time. The test's fake just replays a fixed list of pieces and counts how many you pulled; no real AI is called.

`prompt` — the question to send, as a string like `"why did it restart"`.

`sentinel` — the end marker, as a string like `"<END>"`.

## You return
one string: all the pieces joined in order, up to but not including the marker.

## Rules
A streaming model does not hand back a finished answer. `model.stream(prompt)` returns an iterator that yields small pieces of text — tokens — as they are produced, so you can print them or react to them before the model is done.

Consume the stream and build the answer:

- join the tokens together, in order, into one string
- if a token is exactly equal to `sentinel`, stop there: leave the sentinel out of the result and pull nothing further from the iterator
- if the sentinel never appears, the result is every token joined

```python
# the model streams "the ", "pod ", "<END>", "is ", "up"
solve(model, prompt, "<END>")   # -> "the pod "
```

Return the string. Nothing else.

> [!WARNING]
> The test counts how many tokens the iterator actually produced, so collecting the lot and slicing afterwards fails. Stopping early means stopping the stream, not tidying up after it — that is most of the point of streaming, since tokens you never pull are tokens you never wait for and never pay for.

## Hints
### Hint 1
model.stream(...) is lazy: it does not hand you a list, it hands you something that produces the next token only when you ask for one. list(...) or a comprehension asks for all of them, which is exactly the behaviour being graded against — by the time you slice off the tail, the whole answer has already been generated.
### Hint 2
A plain `for token in model.stream(prompt):` pulls one token per turn round the loop. Start with an empty string, add each token to it, and use `break` the moment a token equals the sentinel — break abandons the iterator where it stands. Return the accumulated string after the loop.
### Hint 3
Different data — read a line-by-line feed and stop at a marker:

```python
def feed():
    for line in ['ok ', 'ok ', 'HALT', 'never ', 'reached']:
        print('produced', line)
        yield line

seen = ''
for line in feed():
    if line == 'HALT':
        break
    seen += line
print(repr(seen))     # 'ok ok '
```

The prints show 'produced' three times, not five — the last two lines were never generated at all.
