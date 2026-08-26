def solve(services_csv, members_csv, min_cpu):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    teams = r.sample(["core", "infra", "data", "web", "sre"], r.randint(2, 4))
    plain = ["priya", "marcus", "lena", "tomas", "ana", "kai"]
    quoted = ["Reyes, Ana", "Okafor, Chidi", "Sato, Yui"]

    member_rows = []
    for i, team in enumerate(teams):
        if i and r.random() < 0.25:
            continue                    # a team with nobody on it
        names = r.sample(plain + quoted, r.randint(1, 3))
        if i == 0:
            names.append(r.choice(quoted))      # always at least one quoted cell
        for name in dict.fromkeys(names):
            cell = f'"{name}"' if "," in name else name
            member_rows.append(f"{team},{cell}")
    r.shuffle(member_rows)
    members_csv = "team,member\n" + "\n".join(member_rows)

    services = r.sample(["auth", "billing", "gateway", "ingest", "search",
                         "notify", "cron"], r.randint(4, 7))
    service_rows = [f"{s},{r.choice(teams + ['ghost'])},"
                    f"{r.choice([100, 250, 500, 750, 900])}" for s in services]
    r.shuffle(service_rows)
    services_csv = "service,team,cpu\n" + "\n".join(service_rows)
    return services_csv, members_csv, r.choice([0, 200, 250, 500])


def _reference(services_csv, members_csv, min_cpu):
    import csv
    import io
    from collections import defaultdict

    by_team = defaultdict(list)
    for row in csv.DictReader(io.StringIO(members_csv)):
        by_team[row["team"]].append(row["member"])

    out = []
    for row in csv.DictReader(io.StringIO(services_csv)):
        cpu = int(row["cpu"])
        members = by_team.get(row["team"])
        if not members or cpu < min_cpu:
            continue
        out.append({"service": row["service"], "team": row["team"],
                    "cpu": cpu, "members": sorted(members)})
    out.sort(key=lambda d: d["service"])
    return out


def test_solve():
    r = rng()
    for _ in range(4):
        services_csv, members_csv, min_cpu = _gen(r)
        assert (solve(services_csv, members_csv, min_cpu)
                == _reference(services_csv, members_csv, min_cpu))
