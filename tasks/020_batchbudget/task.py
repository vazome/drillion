def solve(messages: list[str], budget: int):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    words = ["disk full", "conn reset", "ok", "slow query", "upstream timeout",
             "restarted", "cache miss", "deploy finished"]
    messages = [r.choice(words) for _ in range(r.randint(3, 9))]
    budget = r.choice([0, 3, len(messages[0]), 20, 40, 500])
    return messages, budget


def _reference(messages, budget):
    batch, used, i = [], 0, 0
    while i < len(messages) and used + len(messages[i]) <= budget:
        batch.append(messages[i])
        used += len(messages[i])
        i += 1
    return batch, messages[i:]


def test_solve():
    r = rng()
    cases = [(["disk full", "conn reset", "ok"], 20), (["a very long message"], 3), ([], 10)]
    for _ in range(6):
        cases.append(_gen(r))
    for messages, budget in cases:
        got, want = solve(messages, budget), _reference(messages, budget)
        assert got == want, f"messages={messages} budget={budget}"
        batch, rest = got
        assert batch + rest == messages, "batch + rest must be the original list"
