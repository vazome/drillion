import statistics


def solve(samples: list[float]) -> dict[str, float]:
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    return [round(r.uniform(1.0, 40.0), 2) for _ in range(r.randint(8, 25))]


def _reference(samples):
    q1, _, q3 = statistics.quantiles(samples, n=4, method="inclusive")
    return {
        "median": round(statistics.median(samples), 2),
        "q1": round(q1, 2),
        "q3": round(q3, 2),
        "stdev": round(statistics.stdev(samples), 2),
    }


def test_solve():
    canonical = [12.0, 4.5, 7.25, 19.0, 3.0, 8.5, 11.0, 6.25]
    assert solve(list(canonical)) == {
        "median": 7.88,
        "q1": 5.81,
        "q3": 11.25,
        "stdev": 5.07,
    }, "the inclusive quartiles and the sample standard deviation"

    r = rng()
    for _ in range(8):
        samples = _gen(r)
        original = list(samples)
        mine, theirs = solve(samples), _reference(original)
        assert samples == original, "the caller's list came back sorted or otherwise changed"
        assert set(mine) == set(theirs), f"exactly these four keys: {sorted(theirs)}"
        # named one at a time: pstdev and the exclusive quartiles agree with the right answer
        # on neither, and a whole-dict comparison would not say which of the four went wrong
        for name in theirs:
            assert mine[name] == theirs[name], (
                f"{name} of {len(samples)} samples is {theirs[name]}, got {mine[name]}"
            )
