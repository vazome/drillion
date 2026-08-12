"""Ops scripts get re-run — after a crash, by a retry, by a nervous human at 3am."""

from _lib import rng

META = {"topic": 47, "title": "idempotency — apply desired state, safe to re-run",
        "tier": 3, "minutes": 15, "prereqs": [43]}


def solve(state, desired):
    """Bring `state` in line with `desired` and report what you changed.

    `state` is the resource as it is right now: a dict of key -> value.
    `desired` is how it should look: key -> wanted value, where the value
    None means "this key must not be present".

    Return the tuple (new_state, changes):

      - new_state: a NEW dict. Do not mutate the one you were handed.
      - changes: a sorted list of strings, one per key you actually
        touched, each formatted "<action> <key>" where action is add,
        update or remove.

    Rules, for each key in desired:
      - want is None, key is in state       -> drop it,  "remove <key>"
      - want is None, key is absent         -> nothing
      - key is not in state                 -> set it,   "add <key>"
      - key is in state, value differs      -> set it,   "update <key>"
      - key is in state, value already equal -> nothing
    Keys in state that desired never mentions are left alone — you only
    manage what you were asked to manage.

        state   = {"replicas": "2", "image": "api:1.4", "debug": "on"}
        desired = {"replicas": "3", "image": "api:1.4", "debug": None}
        ->  ({"replicas": "3", "image": "api:1.4"},
             ["remove debug", "update replicas"])

    Feed new_state back in with the same desired and you must get an
    identical state and an empty changes list. That is what idempotent
    means, and it is exactly what the test does: run once, then run
    again on the result.
    """
    raise NotImplementedError


HINTS = [
    "The whole exercise is the comparison before the write. Code that just "
    "assigns every desired key produces the right state but reports a change "
    "every single run, so nobody can tell a real drift from noise. Second "
    "trap: writing into the dict you were given means the caller's 'before' "
    "is gone and you can no longer diff against it.",
    "Start with new = dict(state) and changes = []. Loop over "
    "desired.items(). Three tests in order: want is None, then key not in "
    "new, then new[key] != want. Removal is del new[key] or new.pop(key). "
    "Return (new, sorted(changes)) so the order never depends on dict order.",
    "Different data — reconciling feature flags:\n"
    "    have = {'tls': 'on', 'logs': 'debug'}\n"
    "    want = {'tls': 'on', 'retries': '3'}\n"
    "    out, log = dict(have), []\n"
    "    for k, v in want.items():\n"
    "        if k not in out:\n"
    "            out[k] = v\n"
    "            log.append('add ' + k)\n"
    "        elif out[k] != v:\n"
    "            out[k] = v\n"
    "            log.append('update ' + k)\n"
    "    print(out)          # {'tls': 'on', 'logs': 'debug', 'retries': '3'}\n"
    "    print(sorted(log))  # ['add retries']\n"
    "'logs' survives because want never mentions it, and 'tls' logs nothing "
    "because it already matched. Yours adds the None-means-absent branch.",
]


# ─────────────────────────────  below here is the machinery  ──────────────

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
