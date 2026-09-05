def solve(uri: str):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    buckets = ["logs-prod", "s3-archive", "3d-renders", "backups", "ss-metrics"]
    keys = ["2026/08/api.log.gz", "dump.sql", "a/b/c/deep.log", "report.csv.gz", "single.gz"]
    return f"s3://{r.choice(buckets)}/{r.choice(keys)}"


def _reference(uri):
    rest = uri.removeprefix("s3://")
    bucket, _, key = rest.partition("/")
    name = key.rpartition("/")[2]
    return bucket, key, name, name.removesuffix(".gz")


def test_solve():
    r = rng()
    cases = ["s3://logs-prod/2026/08/api.log.gz", "s3://s3-archive/dump.sql"]
    for _ in range(8):
        cases.append(_gen(r))
    for uri in cases:
        assert solve(uri) == _reference(uri), f"uri={uri}"
