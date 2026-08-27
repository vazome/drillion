def solve(state: dict[str, str], desired: dict[str, str | None] | dict[str, str]):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    pool = ["replicas", "image", "cpu", "mem", "debug", "region", "tls", "log_level"]
    r.shuffle(pool)

    def val():
        return r.choice(["1", "2", "3", "api:1.4", "api:1.5", "on", "off", "eu-1"])

    n_have = r.randint(2, 5)
    have = {k: val() for k in pool[:n_have]}
    want = {}
    for k in pool[:n_have]:
        roll = r.random()
        if roll < 0.35:
            want[k] = have[k]           # already correct, no change
        elif roll < 0.70:
            want[k] = val() + "-new"    # always differs, so always an update
        elif roll < 0.85:
            want[k] = None              # present and must go
        # else: unmanaged, left out of desired entirely
    for k in pool[n_have:n_have + r.randint(0, 3)]:
        want[k] = None if r.random() < 0.3 else val()   # absent: add, or no-op
    return have, want


def _reference(state, desired):
    new = dict(state)
    changes = []
    for key, want in desired.items():
        if want is None:
            if key in new:
                del new[key]
                changes.append(f"remove {key}")
        elif key not in new:
            new[key] = want
            changes.append(f"add {key}")
        elif new[key] != want:
            new[key] = want
            changes.append(f"update {key}")
    return new, sorted(changes)


def test_solve():
    r = rng()
    for _ in range(5):
        have, want = _gen(r)
        before = dict(have)

        state1, changes1 = solve(have, want)
        assert have == before, "solve mutated the state dict it was given"
        assert (state1, changes1) == _reference(before, want)

        state2, changes2 = solve(state1, want)          # the re-run
        assert changes2 == [], "second run reported changes — not idempotent"
        assert state2 == state1
