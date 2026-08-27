def solve(payload: dict[str, dict[str, int] | list[object] | str] | dict[str, list[object] | str] | dict[str, str]):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import json

from _lib import rng


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
