"""Whole-task drill: pull the facts out of a model response without a KeyError.

Combines topics 30 (nested JSON), 43 (except), 75 (walking nested dicts).
"""

import json

from _lib import rng

META = {"topic": 93, "title": "DRILL: dig tool calls out of a model response",
        "tier": 4, "minutes": 20, "prereqs": [30],
        "practices": [30, 43, 75], "tags": ["llm"]}


def solve(payload):
    """WHY: A company pipeline sends a question to an AI chat service and
    gets back a nested answer record. Sometimes the answer is text;
    sometimes the model asks for a tool to be run instead and the text field
    is empty; sometimes the token-usage section is missing because the
    request was cut short. A script that assumes every field is always there
    crashes at 3am. Someone needs a function that pulls the useful facts out
    of any of these shapes without crashing.

    YOU GET: `payload` — a nested dictionary (dictionaries and lists inside
    a dictionary), the shape a chat API returns, like {"choices":
    [{"finish_reason": "stop", "message": {"content": "all clear"}}],
    "usage": {"prompt_tokens": 9, "completion_tokens": 4}}. The test builds
    it, with random pieces missing or broken, and hands it to you.

    YOU RETURN: a dictionary with exactly four keys: "text" (the answer
    text, or ""), "tools" (a list of dictionaries with "name" and "args",
    one per tool request), "total_tokens" (a number) and "finish" (the
    reason the answer ended, or "unknown").

    ─── exact rules ───
    A chat completion comes back as nested JSON where half the keys are
    conditional. Reaching straight for

        payload["choices"][0]["message"]["content"]

    is how a pipeline dies at 3am: content is null whenever the model decided
    to call a tool instead of talking, usage is missing whenever the request
    died part way, and arguments arrive as a JSON *string* that models
    sometimes truncate. Summarise the payload instead.

    Return exactly this shape:

        {"text": <str>, "tools": <list of dicts>,
         "total_tokens": <int>, "finish": <str>}

    Read only the FIRST entry of "choices" — extra choices are ignored. Rules:

      "text"          that choice's message "content" when it is a non-empty
                      string, otherwise "". The key can be missing entirely,
                      or present and set to None
      "tools"         one dict per entry of the message's "tool_calls", in the
                      order they appear:
                          {"name": <the function's name>,
                           "args": <the arguments, parsed into a dict>}
                      Each entry looks like
                          {"id": ..., "type": "function",
                           "function": {"name": ..., "arguments": "{...}"}}
                      "arguments" is a JSON string, so parse it. It can be
                      missing, and it can be truncated mid-way — in either
                      case use {} instead of raising. No tool_calls key, or an
                      empty one, means an empty list
      "total_tokens"  "usage" holds "prompt_tokens" and "completion_tokens";
                      add them. Any of those three can be missing, and a
                      missing one counts as 0
      "finish"        that choice's "finish_reason", or "unknown" when absent
      no choices      "choices" can be missing or empty. Then text is "",
                      tools is [], finish is "unknown", and total_tokens is
                      still read from usage as normal

    Worked example:

        {"choices": [{"finish_reason": "stop",
                      "message": {"content": "all clear"}}],
         "usage": {"prompt_tokens": 9, "completion_tokens": 4}}

        ->  {"text": "all clear", "tools": [], "total_tokens": 13,
             "finish": "stop"}

    Do not modify payload. The test checks that. Narrate the path down as you
    write it — "choices, first one, message, tool calls" — because that is
    what you will be doing out loud when a prompt breaks in production.
    """
    raise NotImplementedError


HINTS = [
    ("Every level of this thing is optional, so the question at each step is "
    "the same: what do I use if this key is not here? Answer it once per level "
    "and the code stops being scary. The trap is that a key being PRESENT is "
    "not the same as it holding something usable — content is routinely there "
    "and set to None, and usage is routinely there and half empty."),
    ("Two tools cover almost all of it. dict.get(key) returns None instead of "
    "raising, and `x or default` turns None, {}, [] and \"\" into the default "
    "in one go — so `payload.get('choices') or []` handles missing AND empty "
    "in one expression, and you can then index [0] safely after checking it. "
    "For the arguments string, json.loads inside a try/except "
    "json.JSONDecodeError is the only part that needs a real except clause. "
    "Build the tools list with a plain for loop."),
    ("Different data — same shape of problem, an incident record:\n"
    "    event = {'alerts': [{'labels': {'sev': None}}]}\n"
    "\n"
    "    alerts = event.get('alerts') or []\n"
    "    first = alerts[0] if alerts else {}\n"
    "    labels = first.get('labels') or {}\n"
    "    print(repr(labels.get('sev') or 'none'))     # 'none'\n"
    "    print(repr(event.get('summary') or ''))      # ''\n"
    "    counts = event.get('counts') or {}\n"
    "    print(counts.get('firing', 0) + counts.get('resolved', 0))   # 0\n"
    "Each line answers 'and if it is not there?' before moving down a level. "
    "Yours does the same walk, then loops over the tool calls."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    names = ["restart_pod", "scale_deployment", "rotate_cert", "drain_node", "get_logs"]
    replies = ["all clear", "the node is cordoned", "I will restart it",
               "checked, nothing looks odd"]

    def tool_call(index):
        args = {"target": r.choice(["api-7", "web-2", "db-0"]),
                "force": r.choice([True, False])}
        if r.random() < 0.4:
            args["wait"] = r.randint(1, 60)
        raw = json.dumps(args)
        call = {"id": f"call_{index}", "type": "function",
                "function": {"name": r.choice(names)}}
        roll = r.random()
        if roll < 0.15:
            pass                                            # arguments missing
        elif roll < 0.30:                                   # truncated mid-write
            call["function"]["arguments"] = raw[:r.randint(1, len(raw) - 2)]
        else:
            call["function"]["arguments"] = raw
        return call

    payload = {"id": f"chatcmpl-{r.randint(1000, 9999)}",
               "model": r.choice(["gpt-x", "claude-y", "llama-z"])}

    shape = r.random()
    if shape < 0.10:
        pass                                                # no choices key
    elif shape < 0.20:
        payload["choices"] = []                             # empty choices
    else:
        message = {"role": "assistant"}
        count = r.choice([0, 0, 1, 2, 3])
        if count:
            message["tool_calls"] = [tool_call(i) for i in range(count)]
            roll = r.random()
            if roll < 0.7:
                message["content"] = None
            elif roll < 0.85:
                message["content"] = r.choice(replies)
        else:
            if r.random() < 0.25:
                message["tool_calls"] = []
            if r.random() < 0.85:
                message["content"] = r.choice(replies)
        choice = {"index": 0, "message": message}
        if r.random() < 0.85:
            choice["finish_reason"] = "tool_calls" if count else r.choice(["stop", "length"])
        payload["choices"] = [choice]
        if r.random() < 0.3:                                # a second choice to ignore
            payload["choices"].append(
                {"index": 1, "finish_reason": "length",
                 "message": {"role": "assistant", "content": "IGNORE ME"}})

    if r.random() < 0.8:
        usage = {}
        if r.random() < 0.9:
            usage["prompt_tokens"] = r.randint(5, 400)
        if r.random() < 0.9:
            usage["completion_tokens"] = r.randint(1, 200)
        payload["usage"] = usage
    return payload


def _reference(payload):
    choices = payload.get("choices") or []
    choice = choices[0] if choices else {}
    message = choice.get("message") or {}

    tools = []
    for call in message.get("tool_calls") or []:
        function = call.get("function") or {}
        try:
            args = json.loads(function.get("arguments") or "{}")
        except json.JSONDecodeError:
            args = {}
        tools.append({"name": function.get("name"), "args": args})

    usage = payload.get("usage") or {}
    return {
        "text": message.get("content") or "",
        "tools": tools,
        "total_tokens": (usage.get("prompt_tokens") or 0)
                        + (usage.get("completion_tokens") or 0),
        "finish": choice.get("finish_reason") or "unknown",
    }


def test_solve():
    r = rng()
    for _ in range(8):
        payload = _gen(r)
        before = json.dumps(payload, sort_keys=True)
        got = solve(payload)
        assert json.dumps(payload, sort_keys=True) == before, "solve modified payload"
        assert got == _reference(payload), f"got {got!r}"
