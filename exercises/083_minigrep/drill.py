def solve(lines, argv):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


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
