def solve(text: str, argv: list[str]):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    services = r.sample(["api", "auth", "cache", "jobs", "search", "web"], r.randint(3, 6))
    regions = ["eu", "us", "ap"]
    rows = [f"{name},{r.choice(regions)},{r.randint(0, 9)}" for name in services]
    text = "service,region,replicas\n" + "\n".join(rows)
    argv = ["--minimum", str(r.randint(0, 5))]
    if r.random() < 0.7:
        argv += ["--region", r.choice(regions)]
    if r.random() < 0.5:
        argv.append("--descending")
    return text, argv


def _reference(text, argv):
    import argparse
    import csv
    import io

    parser = argparse.ArgumentParser()
    parser.add_argument("--region")
    parser.add_argument("--minimum", type=int, default=0)
    parser.add_argument("--descending", action="store_true")
    args = parser.parse_args(argv)
    rows = [row for row in csv.DictReader(io.StringIO(text))
            if (args.region is None or row["region"] == args.region)
            and int(row["replicas"]) >= args.minimum]
    rows.sort(key=(lambda row: (-int(row["replicas"]), row["service"]))
              if args.descending else (lambda row: row["service"]))
    return [f"service={row['service']!r} region={row['region']} replicas={row['replicas']}"
            for row in rows]


def test_solve():
    text = 'service,region,replicas\n"api,edge",eu,3\nweb,us,5\nauth,eu,1'
    assert solve(text, ["--region", "eu", "--minimum", "2"]) == [
        "service='api,edge' region=eu replicas=3"]
    assert solve(text, ["--descending"]) == [
        "service='web' region=us replicas=5",
        "service='api,edge' region=eu replicas=3",
        "service='auth' region=eu replicas=1",
    ]
    r = rng()
    for _ in range(5):
        text, argv = _gen(r)
        assert solve(text, list(argv)) == _reference(text, argv)
