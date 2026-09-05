def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    service = r.choice(["api", "worker", "web", "cron"])
    version = r.choice([f"{r.randint(0, 9)}.{r.randint(0, 9)}.{r.randint(0, 20)}",
                        f"{r.randint(1, 9)}.{r.randint(0, 9)}", "latest", "v2.0.0"])
    return f"{service} {version} {r.choice(['ok', 'failed', 'rolled-back'])}", version


def _reference():
    class Deploy:
        def __init__(self, service, version, status):
            self.service, self.version, self.status = service, version, status

        def __repr__(self):
            return f"Deploy({self.service}, {self.version}, {self.status})"

        @classmethod
        def from_line(cls, line):
            return cls(*line.split())

        @staticmethod
        def is_semver(version):
            parts = version.split(".")
            return len(parts) == 3 and all(p.isdigit() for p in parts)

    return Deploy


def test_solve():
    r = rng()
    mine, theirs = solve(), _reference()
    for _ in range(8):
        line, version = _gen(r)
        assert repr(mine.from_line(line)) == repr(theirs.from_line(line)), line
        assert mine.is_semver(version) == theirs.is_semver(version), version

    class Mine(mine):
        pass

    assert type(Mine.from_line("api 1.0.0 ok")) is Mine, "from_line must build through cls"
    assert mine.is_semver("1.4.2") is True and mine.is_semver("1.4") is False
