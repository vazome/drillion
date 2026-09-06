def solve(configs: dict, start: str):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    names = ["main", "db", "creds", "http", "tls"]
    configs = {}
    for i, name in enumerate(names):
        entries = []
        for _ in range(r.randint(1, 3)):
            entries.append(f"{name}_{r.choice(['host', 'port', 'level'])}={r.randint(1, 99)}")
        for child in names[i + 1:]:
            if r.random() < 0.5:
                entries.insert(r.randint(0, len(entries)), ("include", child))
        if r.random() < 0.2:
            entries.append(("include", "missing"))
        configs[name] = entries
    return configs, "main"


def _reference(configs, start):
    def expand(name):
        for entry in configs.get(name, []):
            if isinstance(entry, tuple):
                yield from expand(entry[1])
            else:
                yield entry

    return expand(start)


def test_solve():
    r = rng()
    example = {"main": ["log_level=info", ("include", "db"), "port=80"],
               "db": ["db_host=localhost", ("include", "creds")],
               "creds": ["db_user=app"]}
    cases = [(example, "main"), ({}, "main")]
    for _ in range(6):
        cases.append(_gen(r))
    for configs, start in cases:
        got = solve(configs, start)
        assert iter(got) is got, "return a generator, not a list"
        assert list(got) == list(_reference(configs, start)), f"configs={configs}"
