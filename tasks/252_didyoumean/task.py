def solve(typed: str, commands: list[str]) -> str | None:
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_COMMANDS = [
    "status",
    "start",
    "stop",
    "restart",
    "deploy",
    "rollback",
    "logs",
    "config",
    "migrate",
    "version",
]


def _gen(r):
    commands = r.sample(_COMMANDS, r.randint(4, 8))
    typed = list(r.choice(commands + ["quixotic", "zzzyx"]))
    for _ in range(r.randint(0, 4)):
        where = r.randrange(len(typed) + 1)
        edit = r.choice(["insert", "delete", "substitute"])
        if edit == "insert" or not typed:
            typed.insert(where, r.choice("abcdefghijklmnopqrstuvwxyz"))
        elif edit == "delete":
            del typed[min(where, len(typed) - 1)]
        else:
            typed[min(where, len(typed) - 1)] = r.choice("abcdefghijklmnopqrstuvwxyz")
    return "".join(typed) or "x", commands


def _reference(typed, commands):
    def distance(a, b):
        row = list(range(len(b) + 1))
        for i, ca in enumerate(a, 1):
            corner, row[0] = row[0], i
            for j, cb in enumerate(b, 1):
                corner, row[j] = row[j], min(row[j] + 1, row[j - 1] + 1, corner + (ca != cb))
        return row[-1]

    best, best_at = None, None
    for command in commands:
        at = distance(typed, command)
        if best_at is None or at < best_at:
            best, best_at = command, at
    return best if best_at <= 3 else None


def test_solve():
    r = rng()
    known = [
        ("stauts", ["status", "start", "stop"], "status"),
        ("start", ["status", "start"], "start"),
        ("zzzzzzzz", ["status", "start"], None),
        ("rollbck", ["rollback", "logs"], "rollback"),
        # one substitution from 'car', one insertion from 'cast': a tie, and 'car' is listed first
        ("cat", ["car", "cast"], "car"),
        ("cat", ["cast", "car"], "cast"),
    ]
    for typed, commands, want in known:
        assert solve(typed, list(commands)) == want, f"{typed!r} against {commands} is {want!r}"

    for _ in range(8):
        typed, commands = _gen(r)
        assert solve(typed, list(commands)) == _reference(typed, commands), (
            f"typed={typed!r} commands={commands}"
        )
