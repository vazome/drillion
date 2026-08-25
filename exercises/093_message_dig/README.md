---
title: 'DRILL: dig tool calls out of a model response'
minutes: 20
prereqs: [30]
tags: [llm]
practices: [30, 43, 75]
---
# DRILL: dig tool calls out of a model response

*Whole-task drill: pull the facts out of a model response without a KeyError.*

Combines topics 30 (nested JSON), 43 (except), 75 (walking nested dicts).

## Why
A company pipeline sends a question to an AI chat service and gets back a nested answer record. Sometimes the answer is text; sometimes the model asks for a tool to be run instead and the text field is empty; sometimes the token-usage section is missing because the request was cut short. A script that assumes every field is always there crashes at 3am. Someone needs a function that pulls the useful facts out of any of these shapes without crashing.

## You get
`payload` — a nested dictionary (dictionaries and lists inside a dictionary), the shape a chat API returns, like

```python
{"choices": [{"finish_reason": "stop", "message": {"content": "all clear"}}],
 "usage": {"prompt_tokens": 9, "completion_tokens": 4}}
```

The test builds it, with random pieces missing or broken, and hands it to you.

## You return
a dictionary with exactly four keys: `"text"` (the answer text, or `""`), `"tools"` (a list of dictionaries with `"name"` and `"args"`, one per tool request), `"total_tokens"` (a number) and `"finish"` (the reason the answer ended, or `"unknown"`).

## Rules
A chat completion comes back as nested JSON where half the keys are conditional. Reaching straight for

```python
payload["choices"][0]["message"]["content"]
```

is how a pipeline dies at 3am: content is null whenever the model decided to call a tool instead of talking, usage is missing whenever the request died part way, and arguments arrive as a JSON *string* that models sometimes truncate. Summarise the payload instead.

Return exactly this shape:

```python
{"text": <str>, "tools": <list of dicts>,
 "total_tokens": <int>, "finish": <str>}
```

Read only the FIRST entry of `"choices"` — extra choices are ignored.

- `"text"` — that choice's message `"content"` when it is a non-empty string, otherwise `""`. The key can be missing entirely, or present and set to `None`.
- `"tools"` — one dict per entry of the message's `"tool_calls"`, in the order they appear: `{"name": <the function's name>, "args": <the arguments, parsed into a dict>}`. Each entry looks like `{"id": ..., "type": "function", "function": {"name": ..., "arguments": "{...}"}}`. `"arguments"` is a JSON string, so parse it — it can be missing, and it can be truncated mid-way, in either case use `{}` instead of raising. No `tool_calls` key, or an empty one, means an empty list.
- `"total_tokens"` — `"usage"` holds `"prompt_tokens"` and `"completion_tokens"`; add them. Any of those three can be missing, and a missing one counts as 0.
- `"finish"` — that choice's `"finish_reason"`, or `"unknown"` when absent.
- no choices — `"choices"` can be missing or empty. Then text is `""`, tools is `[]`, finish is `"unknown"`, and total_tokens is still read from usage as normal.

Worked example:

```python
payload = {"choices": [{"finish_reason": "stop",
                         "message": {"content": "all clear"}}],
           "usage": {"prompt_tokens": 9, "completion_tokens": 4}}
solve(payload)
# -> {"text": "all clear", "tools": [], "total_tokens": 13, "finish": "stop"}
```

> [!WARNING]
> Do not modify `payload` — the test checks that it comes back unchanged.

> [!TIP]
> Narrate the path down as you write it — "choices, first one, message, tool calls" — because that is what you will be doing out loud when a prompt breaks in production.

## Hints
### Hint 1
Every level of this thing is optional, so the question at each step is the same: what do I use if this key is not here? Answer it once per level and the code stops being scary. The trap is that a key being PRESENT is not the same as it holding something usable — content is routinely there and set to None, and usage is routinely there and half empty.
### Hint 2
Two tools cover almost all of it. dict.get(key) returns None instead of raising, and `x or default` turns None, {}, [] and "" into the default in one go — so `payload.get('choices') or []` handles missing AND empty in one expression, and you can then index [0] safely after checking it. For the arguments string, json.loads inside a try/except json.JSONDecodeError is the only part that needs a real except clause. Build the tools list with a plain for loop.
### Hint 3
Different data — same shape of problem, an incident record:

```python
event = {'alerts': [{'labels': {'sev': None}}]}

alerts = event.get('alerts') or []
first = alerts[0] if alerts else {}
labels = first.get('labels') or {}
print(repr(labels.get('sev') or 'none'))     # 'none'
print(repr(event.get('summary') or ''))      # ''
counts = event.get('counts') or {}
print(counts.get('firing', 0) + counts.get('resolved', 0))   # 0
```

Each line answers 'and if it is not there?' before moving down a level. Yours does the same walk, then loops over the tool calls.
