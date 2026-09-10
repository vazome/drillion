import difflib


def solve(old, new, wanted):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_KEYS = ["retries", "timeout", "endpoint", "region", "log_level", "max_workers", "queue_name"]


def _gen(r):
    keys = r.sample(_KEYS, 5)
    old = [f"{k} = {r.randint(1, 99)}\n" for k in keys]
    new = list(old)
    new[r.randrange(len(new))] = f"{keys[0]} = {r.randint(100, 199)}\n"
    new.append(f"{r.choice(['debug', 'dry_run'])} = false\n")
    del new[-2]
    typo = r.choice(keys)
    # one letter dropped, which is what an operator actually types
    cut = r.randrange(1, len(typo))
    return old, new, typo[:cut] + typo[cut + 1 :]


def _reference(old, new, wanted):
    diff = list(difflib.unified_diff(old, new, fromfile="config.old", tofile="config.new"))
    keys = [line.split(" = ", 1)[0] for line in new]
    matches = difflib.get_close_matches(wanted, keys, n=1)
    return diff, (matches[0] if matches else None)


def test_solve():
    r = rng()
    old, new, wanted = _gen(r)

    diff, suggestion = solve(old, new, wanted)
    want_diff, want_suggestion = _reference(old, new, wanted)

    assert isinstance(diff, list), "return the diff as a list, not a generator"
    assert diff == want_diff, f"diff for wanted={wanted!r}"
    assert diff[0] == "--- config.old\n" and diff[1] == "+++ config.new\n", diff[:2]
    for line in diff:
        assert line.endswith("\n"), f"{line!r} lost its newline — do not strip the input lines"

    assert suggestion is None or isinstance(suggestion, str), "one key or None, never a list"
    assert suggestion == want_suggestion, f"suggestion for {wanted!r}"

    exact = new[0].split(" = ", 1)[0]
    assert solve(old, new, exact)[1] == exact, f"{exact!r} is spelt right and suggests itself"
    assert solve(old, new, "zzzzzzzz")[1] is None, "nothing close enough is None"
    assert solve(old, old, wanted)[0] == [], "two identical configs have an empty diff"
