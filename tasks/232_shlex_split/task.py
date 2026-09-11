import shlex


def solve(lines):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_PATHS = ["/var/log/last run", "/etc/app.conf", "/srv/my data/db.sqlite", "/tmp/out"]
_NOTES = ["nightly", "see ticket 4412", "do not reorder", "runs as root"]


def _gen(r):
    lines = []
    for _ in range(5):
        path = r.choice(_PATHS)
        quoted = f'"{path}"' if " " in path or r.random() < 0.5 else path
        line = f"{r.choice(['cp -r', 'rm -f', 'stat', 'tar -cf /backup.tar'])} {quoted}"
        if r.random() < 0.5:
            line += f"  # {r.choice(_NOTES)}"
        lines.append(line)
    lines.append("   # only a note")
    lines.append("")
    lines.append(f'echo "{r.choice(_NOTES)}')
    r.shuffle(lines)
    return lines


def _reference(lines):
    out = []
    for line in lines:
        try:
            out.append(shlex.split(line, comments=True))
        except ValueError:
            out.append(None)
    return out


def test_solve():
    r = rng()
    lines = _gen(r)

    got = solve(lines)
    want = _reference(lines)

    assert len(got) == len(lines), "one entry per input line"
    for line, mine, theirs in zip(lines, got, want):
        assert mine == theirs, f"{line!r}"

    assert None in want and [] in want, "generator should cover the bad line and the blank one"

    canonical = solve(
        [
            'cp -r "/var/log/last run" /backup  # nightly',
            "   # just a note",
            'echo "unterminated',
            "grep '#tag' notes.txt",
        ]
    )
    assert canonical == [
        ["cp", "-r", "/var/log/last run", "/backup"],
        [],
        None,
        ["grep", "#tag", "notes.txt"],
    ], canonical
