def solve(pages: list[list[str]], first_n: int):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    services = r.sample(["api", "auth", "billing", "cron", "db", "ingest"], r.randint(3, 4))
    lines = [f"{s} {r.choice(['INFO', 'WARN', 'ERROR'])} req={r.randint(100, 999)}"
             for s in services for _ in range(r.randint(2, 5))]
    total = len(lines)
    first_n = r.randint(max(4, total * 2 // 3), total - 1)
    while True:                      # ensure the head really is interleaved
        r.shuffle(lines)
        keys = [ln.split()[0] for ln in lines[:first_n]]
        runs = sum(1 for i, k in enumerate(keys) if i == 0 or k != keys[i - 1])
        if runs > len(set(keys)):    # some service occurs in two separate runs
            break
    cut = sorted(r.sample(range(1, total), r.randint(1, 2)))
    pages = [lines[i:j] for i, j in zip([0] + cut, cut + [total])]
    return pages, first_n


def _reference(pages, first_n):
    from itertools import chain, groupby, islice
    svc = lambda line: line.split()[0]
    head = sorted(islice(chain.from_iterable(pages), first_n), key=svc)
    return [(s, len(list(grp))) for s, grp in groupby(head, key=svc)]


def test_solve():
    r = rng()
    for _ in range(4):
        pages, first_n = _gen(r)
        assert solve([list(p) for p in pages], first_n) == _reference(pages, first_n)
