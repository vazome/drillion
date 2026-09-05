---
title: walrus — assign inside the condition
difficulty: medium
tier: core
minutes: 12
prereqs: [172]
tags: [walrus, while]
---
# walrus — assign inside the condition

*`:=` gives the value a name and hands the same value to the `if` or `while` asking about it.*

## Read first
- [Assignment expressions](https://devdocs.io/python~3.14/reference/expressions#assignment-expressions) — the `name := value` form and where the parentheses are required
- [PEP 572 — examples](https://peps.python.org/pep-0572/#examples) — the read-a-chunk loop and the match-a-line loop, which are the two shapes worth memorising
- [The while statement](https://devdocs.io/python~3.14/reference/compound_stmts#the-while-statement) — the loop this pairs with

## Why
Reading from a socket or a file handle means calling `read()` until it hands back nothing. Without an assignment expression you either write the call twice, once before the loop and once at the bottom, or you loop forever with a `break` in the middle. Both work; both put the same call in two places, and the day the arguments change, one of them gets missed. The walrus lets the loop ask its question and keep the answer in one line.

## You get
`read` — a function of no arguments. Each call hands back the next chunk of the stream as a string, and an empty string `""` when there is nothing left. You cannot ask how many chunks there are, and calls are not free.

## You return
a list of the chunks, in order, with the final empty one left out.

## Rules
- Call `read()` until it returns `""`.
- Return the non-empty chunks in the order they arrived.
- Call `read()` exactly once per chunk, plus once for the empty one that ends it. The test counts the calls, so reading a chunk twice or reading past the end fails.

```python
solve(read)   # read() returns "ab", then "cd", then ""
# -> ["ab", "cd"]
```

> [!WARNING]
> An empty stream is normal: the very first `read()` may return `""`, and the answer is `[]` with exactly one call made. A loop that reads once before it checks anything makes two.

## Hints
### Hint 1
The condition needs the value of `read()` twice: once to decide whether to keep going, once to store. `:=` is how one call does both.
### Hint 2
`while (chunk := read()):` calls `read`, names the result `chunk`, and treats that same string as the condition. An empty string is falsy, so the loop ends exactly when the stream does. The parentheses are not optional here.
### Hint 3
Different data, same shape:

```python
def source(items=iter(["a", "b", ""])):
    return next(items)

out = []
while (item := source()):
    out.append(item)
print(out)   # ['a', 'b']
```

The same shape works with `if` for a regex: `if (m := rx.search(line)): use(m)`.
