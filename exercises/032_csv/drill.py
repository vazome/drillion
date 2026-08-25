def solve(text):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    comma_owners = ["Reyes, Ana", "Okafor, Chidi", "Sato, Yui", "Novak, Petra"]
    plain_owners = ["priya", "marcus", "lena", "tomas"]
    services = r.sample(["auth", "billing", "gateway", "ingest", "search", "notify", "cron"],
                        r.randint(3, 6))
    must_quote = r.randrange(len(services))     # at least one comma-in-quotes row
    lines = ["service,owner,cpu"]
    for i, s in enumerate(services):
        if i == must_quote or r.random() < 0.3:
            owner = f'"{r.choice(comma_owners)}"'
        else:
            owner = r.choice(plain_owners)
        lines.append(f"{s},{owner},{r.choice([100, 250, 500, 750])}m")
    return "\n".join(lines)


def _reference(text):
    import csv
    import io
    return list(csv.DictReader(io.StringIO(text)))


def test_solve():
    r = rng()
    for _ in range(4):
        text = _gen(r)
        assert solve(text) == _reference(text)
