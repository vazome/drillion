"""A generator hands over one item at a time, so a 10 GB log never lands in RAM."""

from _lib import rng

META = {"topic": 11, "title": "generators — yield a filtered stream, lazily", "tier": 3,
        "minutes": 10, "prereqs": []}


def solve(lines):
    """WHY: A log file on a production server is 10 GB. Support needs the
    request ids of every failed request so they can look them up, and they
    want the first one right away, not after the whole file has been read.
    Loading the file into memory would crash the box. You need a way to hand
    out results one at a time, reading only as far as needed for the next
    answer.

    YOU GET: `lines` — a stream of log lines like "api INFO req=a1", one
    line per item, that you can walk through exactly once. The test creates
    it and hands it to you; you never build it yourself.

    YOU RETURN: not a list, but a generator: an object that hands out one
    request id at a time, for ERROR lines only, doing the reading as it goes.

    ─── exact rules ───
    Stream the request ids of the ERROR lines.

    Each line looks like "<service> <LEVEL> req=<id>". Produce the <id> part
    (a string) of every line whose LEVEL is ERROR, in order, nothing else.

        ["api INFO req=a1", "db ERROR req=b2", "api ERROR req=c3"]
        ->  yields "b2", then "c3"

    What you return must be a generator, not a list. Two ways to make one: a
    def with yield in its body, or a comprehension written with round brackets
    instead of square ones.

    The test checks with inspect.isgenerator, and it also checks that you are
    lazy. It feeds you a stream that counts how many lines you pulled off it,
    takes exactly one id from you, and then expects you to have read no
    further than the line that id came from. Building a list first and yielding
    from that fails the check even though the values would be right.

    lines is any iterable of strings. Do not index it, do not call len on it,
    just iterate it once.
    """
    raise NotImplementedError


HINTS = [
    ("A list comprehension does all the work up front and hands you the "
    "finished list; you cannot see item one until item ten thousand is done. "
    "A generator flips that: it does the least work needed to produce the next "
    "item, then stops and waits. Same values, different question — when does "
    "the work happen. On a log you are tailing, or a file bigger than memory, "
    "only one of the two is usable."),
    ("Either write a def whose body loops over lines and yields the id when the "
    "level is ERROR — the moment a function contains yield anywhere, calling it "
    "runs none of the body and returns a generator instead. Or take the list "
    "comprehension you would have written and swap [ ] for ( ). For one line, "
    "line.split() gives the three fields; the id is the part of the third after "
    "the '='."),
    ("Different data — even numbers, squared:\n"
    "    def evens(nums):\n"
    "        for n in nums:\n"
    "            if n % 2 == 0:\n"
    "                yield n * n\n"
    "\n"
    "    g = evens([1, 2, 3, 4])\n"
    "    print(g)          # <generator object evens at 0x...>  <- body not run yet\n"
    "    print(next(g))    # 4    <- only now does the loop start, and it stops again\n"
    "    print(list(g))    # [16] <- the 4 is already spent, a generator is one-shot\n"
    "\n"
    "    same = (n * n for n in [1, 2, 3, 4] if n % 2 == 0)   # identical, one line\n"
    "Yours is the same shape: loop, test the level, yield the id."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    """A short log with at least one ERROR line, somewhere unpredictable."""
    services = ["api", "auth", "billing", "cron", "db", "edge"]
    n = r.randint(6, 14)
    lines = []
    for _ in range(n):
        rid = "".join(r.choice("0123456789abcdef") for _ in range(4))
        lines.append(f"{r.choice(services)} {r.choice(['INFO', 'WARN', 'DEBUG'])} req={rid}")
    for i in r.sample(range(n), r.randint(1, max(1, n // 3))):
        svc, _, req = lines[i].split()
        lines[i] = f"{svc} ERROR {req}"
    return lines


def _reference(lines):
    for line in lines:
        _service, level, req = line.split()
        if level == "ERROR":
            yield req.split("=", 1)[1]


def _counting(lines, pulled):
    """Hands out lines one at a time, noting each one it was asked for."""
    for line in lines:
        pulled.append(line)
        yield line


def test_solve():
    import inspect

    r = rng()
    for _ in range(4):
        lines = _gen(r)
        expected = list(_reference(lines))

        got = solve(iter(lines))
        assert inspect.isgenerator(got), "solve must return a generator"
        assert list(got) == expected

        # laziness: reading one id must not drag the whole stream through
        pulled = []
        stream = solve(_counting(lines, pulled))
        assert pulled == [], "no lines should be read before the first next()"
        assert next(stream) == expected[0]
        stop = 1 + next(i for i, ln in enumerate(lines) if ln.split()[1] == "ERROR")
        assert len(pulled) == stop, "read past the first ERROR line — not lazy"
