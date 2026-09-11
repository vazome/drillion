import sqlite3


def solve(charges, adjustments, team):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_TEAMS = ["ops", "billing", "O'Hare & Sons", "platform", "d'Angelo"]


def _gen(r):
    charges = [(i, r.choice(_TEAMS), r.randrange(0, 120)) for i in range(1, r.randint(4, 9) + 1)]
    ids = [c[0] for c in charges]
    adjustments = [(r.choice(ids), r.randint(-60, 40)) for _ in range(r.randint(2, 6))]
    return charges, adjustments, r.choice(_TEAMS)


class _Negative(Exception):
    pass


def _reference(charges, adjustments, team):
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE charges (id INTEGER PRIMARY KEY, team TEXT, amount INTEGER)")
    con.executemany("INSERT INTO charges VALUES (?, ?, ?)", charges)
    con.commit()
    applied = True
    try:
        with con:
            for cid, delta in adjustments:
                con.execute("UPDATE charges SET amount = amount + ? WHERE id = ?", (delta, cid))
                (left,) = con.execute("SELECT amount FROM charges WHERE id = ?", (cid,)).fetchone()
                if left < 0:
                    raise _Negative(cid)
    except _Negative:
        applied = False
    amounts = dict(con.execute("SELECT id, amount FROM charges ORDER BY id"))
    (total,) = con.execute("SELECT SUM(amount) FROM charges WHERE team = ?", (team,)).fetchone()
    con.close()
    return {"applied": applied, "amounts": amounts, "team_total": total or 0}


def test_solve():
    r = rng()
    seen_rollback = seen_applied = False
    for _ in range(30):
        charges, adjustments, team = _gen(r)
        got, want = solve(charges, adjustments, team), _reference(charges, adjustments, team)
        assert got == want, f"for charges={charges} adjustments={adjustments} team={team!r}: got {got}"
        assert set(got) == {"applied", "amounts", "team_total"}, f"exactly three keys, got {sorted(got)}"
        if want["applied"]:
            seen_applied = True
        else:
            seen_rollback = True
            # the batch is undone in full, not up to the offending row
            assert got["amounts"] == {c[0]: c[2] for c in charges}, "a rolled-back batch leaves every amount as loaded"
    assert seen_applied and seen_rollback, "generator should produce both outcomes"

    # a team name the database has no trouble with and a spliced string cannot survive
    quoted = solve([(1, "O'Hare & Sons", 50), (2, "ops", 10)], [(1, -20)], "O'Hare & Sons")
    assert quoted == {"applied": True, "amounts": {1: 30, 2: 10}, "team_total": 30}, quoted

    # deltas stack: neither -40 alone sinks the charge, together they do
    stacked = solve([(1, "ops", 50)], [(1, -40), (1, -40)], "ops")
    assert stacked == {"applied": False, "amounts": {1: 50}, "team_total": 50}, stacked

    empty = solve([(1, "ops", 7)], [], "billing")
    assert empty == {"applied": True, "amounts": {1: 7}, "team_total": 0}, empty
