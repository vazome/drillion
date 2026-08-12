r"""Whole-task drill: rebuild grep, flags and all.

Combines topics 29 (regex), 37 (argparse), 28 (str methods).
"""

from _lib import rng

META = {"topic": 83, "title": "DRILL: mini-grep with argparse flags",
        "tier": 4, "minutes": 25, "prereqs": [29],
        "practices": [29, 37, 28]}


def solve(lines, argv):
    """Write the guts of grep.

    `lines` is a list of strings with no trailing newlines. `argv` is the
    command line as a list, exactly what sys.argv[1:] would hand you.
    Parse it with argparse — do not pick the flags apart by hand:

        pattern              positional, a regex
        -i, --ignore-case    match without regard to case
        -v, --invert-match   keep the lines that do NOT match
        -n, --line-number    prefix each kept line with "<number>:", 1-based

    Return the kept lines as a list of strings.

        lines = ["INFO ok", "ERROR boom", "warn slow"]
        argv  = ["-n", "-i", "error"]
        ->  ["2:ERROR boom"]

    Flags arrive in any order, long or short form, and the pattern may
    come before or after them. A hit anywhere in the line counts, the
    pattern does not have to match the whole line.

    Interviewers like this one because the invert flag catches people.
    Say out loud what -v does to the decision before you code it.
    """
    raise NotImplementedError


HINTS = [
    "Two halves. First turn argv into settings — that is argparse's whole "
    "job, and hand-rolling `if '-i' in argv` is the answer that loses points. "
    "Then one pass over the lines. Invert is the flag that trips people: it "
    "does not change the pattern or the search, it flips the keep-or-drop "
    "decision at the end.",
    "add_argument('pattern') for the positional, then each flag with "
    "action='store_true' — argparse turns --ignore-case into args.ignore_case "
    "for you. parse_args(argv), not parse_args(). Compile once with "
    "re.compile(pattern, re.IGNORECASE) when the flag is set and no flags "
    "otherwise. Then per line: matched = rx.search(line) is not None, and "
    "keep it when matched != args.invert_match. enumerate(lines, start=1) and "
    "an f-string give you the numbered form.",
    "Different data, both halves:\n"
    "    import argparse\n"
    "    p = argparse.ArgumentParser()\n"
    "    p.add_argument('word')\n"
    "    p.add_argument('-c', '--count', action='store_true')\n"
    "    args = p.parse_args(['--count', 'pod'])\n"
    "    print(args.word, args.count)       # pod True\n"
    "\n"
    "    for matched, invert in [(True, False), (True, True), (False, True)]:\n"
    "        print(matched != invert)        # True, False, True\n"
    "That second loop is the whole invert rule: not-equal is exclusive or, "
    "and it reads better than four branches.",
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    levels = ["INFO", "ERROR", "WARN", "DEBUG"]
    msgs = ["pod restarted", "disk full", "conn reset", "slow query",
            "cache miss", "deploy done"]
    lines = [f"10:{i:02d} {r.choice(levels)} {r.choice(msgs)}"
             for i in range(r.randint(8, 20))]
    pattern = r.choice(["error", "ERROR", r"\d\d:\d\d", "pod|disk", "WARN",
                        "conn", r"slow\s+query", "deploy done", "xyzzy"])
    argv = [r.choice(pair) for pair in [("-i", "--ignore-case"),
                                        ("-v", "--invert-match"),
                                        ("-n", "--line-number")]
            if r.random() < 0.5]
    r.shuffle(argv)
    if r.random() < 0.3:
        argv.insert(0, pattern)
    else:
        argv.append(pattern)
    return lines, argv


def _reference(lines, argv):
    import argparse
    import re
    parser = argparse.ArgumentParser()
    parser.add_argument("pattern")
    parser.add_argument("-i", "--ignore-case", action="store_true")
    parser.add_argument("-v", "--invert-match", action="store_true")
    parser.add_argument("-n", "--line-number", action="store_true")
    args = parser.parse_args(argv)
    rx = re.compile(args.pattern, re.IGNORECASE if args.ignore_case else 0)
    out = []
    for number, line in enumerate(lines, start=1):
        matched = rx.search(line) is not None
        if matched != args.invert_match:
            out.append(f"{number}:{line}" if args.line_number else line)
    return out


def test_solve():
    r = rng()
    for _ in range(4):
        lines, argv = _gen(r)
        assert solve(list(lines), list(argv)) == _reference(lines, argv)
