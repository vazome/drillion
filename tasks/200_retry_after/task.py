from collections.abc import Callable


def solve(call: Callable[[], dict], sleep: Callable[[float], None], max_attempts: int):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _reference(call, sleep, max_attempts):
    for attempt in range(1, max_attempts + 1):
        response = call()
        if response["status"] != 429 or attempt == max_attempts:
            return {"response": response, "attempts": attempt}
        sleep(response.get("retry_after", 1))


def _script(responses):
    remaining = iter(responses)
    calls = []
    sleeps = []

    def call():
        response = next(remaining)
        calls.append(response)
        return response

    def sleep(seconds):
        sleeps.append(seconds)

    return call, sleep, calls, sleeps


def test_solve():
    responses = [{"status": 429, "retry_after": 2}, {"status": 429}, {"status": 200}]
    call, sleep, calls, sleeps = _script(responses)
    assert solve(call, sleep, 4) == {"response": {"status": 200}, "attempts": 3}
    assert len(calls) == 3 and sleeps == [2, 1]

    call, sleep, calls, sleeps = _script([{"status": 429, "retry_after": 7}] * 3)
    assert solve(call, sleep, 3) == {
        "response": {"status": 429, "retry_after": 7}, "attempts": 3}
    assert len(calls) == 3 and sleeps == [7, 7], "do not sleep after the final attempt"

    r = rng()
    for _ in range(5):
        attempts = r.randint(1, 5)
        responses = [{"status": 429, "retry_after": r.randint(1, 8)}
                     for _ in range(r.randint(0, attempts))]
        responses += [{"status": r.choice([200, 201, 500])}]
        mine = _script(responses)
        theirs = _script(responses)
        assert solve(mine[0], mine[1], attempts) == _reference(theirs[0], theirs[1], attempts)
        assert mine[2:] == theirs[2:]
