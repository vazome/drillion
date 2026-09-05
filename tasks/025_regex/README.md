---
title: re — named groups on log lines
difficulty: medium
tier: core
track: rsample
minutes: 15
prereqs: [5]
tags: [files-text]
---
# re — named groups on log lines

*Pulling fields out of log lines is the regex work ops actually does.*

## Read first
- [Regular Expression HOWTO](https://docs.python.org/3/howto/regex.html) — the official intro; read up to 'Grouping'
- [Regular Expressions: Regexes in Python](https://realpython.com/regex-python/) — `re.sub` / `re.findall` with examples
- [regex101](https://regex101.com) — paste a pattern, see what it matches, live

> [!NOTE]
> **Take-home:** `_tokenize` in reranker.py

## Why
An application writes its log as free text, one line per event, with fields like `level=`, `host=` and `msg="..."`. Noise lines (stack traces, retry notes) are mixed in between. The incident commander wants a clean table of level, host and message for each real event to paste into the incident report. You pull those fields out of the matching lines and skip everything else.

## You get
`text` — one big multi-line string. Each real event line looks like the example in the rules below; the noise lines do not. The test creates it and hands it to you; you never build it yourself.

## You return
a list of dicts, one per event line in order, each with exactly the keys `"level"`, `"host"` and `"msg"`.

## Rules
Extract structured records from a raw log blob.

`text` is one multi-line string. The lines you want look like:

```text
2026-08-12T09:14:02 level=ERROR host=web-1 msg="disk full on /var" trace="a9f3c2"
```

Return a list of dicts, one per matching line, in file order:

```python
solve(text)
# -> [{"level": "ERROR", "host": "web-1", "msg": "disk full on /var"}, ...]
```

Ignore the timestamp and trace. Some lines are noise (stack-trace continuations and the like) — they match nothing and must be skipped.

> [!WARNING]
> `msg` contains spaces, and there is another quoted field after it. A greedy `.*` will eat its way into `trace`.

## Hints
### Hint 1
One pattern, compiled once, applied across the whole text. Named groups give you a dict per match instead of counting parentheses. And look at how many double quotes sit after `msg=` on a line — think about which one a greedy match stops at (hint: the last one).
### Hint 2
`re.compile` the pattern; `(?P<name>...)` names a group; `pat.finditer(text)` yields match objects and `m.groupdict()` is exactly the dict you need (`findall` would hand you bare tuples, names lost). For the quoted `msg` use `.*?` or `[^"]*` so it stops at the FIRST closing quote.
### Hint 3
Different data, same shape:

```python
import re
pat = re.compile(r'user=(?P<user>\w+) cmd="(?P<cmd>.*?)"')
log = 'user=ann cmd="rm -rf /tmp" id="7"\nplain noise\nuser=bo cmd="ls" id="9"'
print([m.groupdict() for m in pat.finditer(log)])
# [{'user': 'ann', 'cmd': 'rm -rf /tmp'}, {'user': 'bo', 'cmd': 'ls'}]
```

With a greedy `.*` the first `cmd` would swallow everything up to `id="7"`.
