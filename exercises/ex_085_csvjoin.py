"""Whole-task drill: two CSVs, one shared column, join and filter.

Combines topics 32 (csv), 18 (dict lookups), 20 (defaultdict grouping).
"""

from _lib import rng

META = {"topic": 85, "title": "DRILL: inner-join two CSVs on a shared key",
        "tier": 4, "minutes": 30, "prereqs": [32],
        "practices": [32, 18, 20]}


def solve(services_csv, members_csv, min_cpu):
    '''WHY: One spreadsheet lists services with the team that owns each and
    its CPU allocation. Another lists which people are on which team. A
    manager asks "for every service using at least 200 CPU, who do I
    contact?" That means matching rows from the two files on the shared
    "team" column, which is the single most common "write a quick script"
    request in ops.

    YOU GET: `services_csv` — the first file as one string in CSV form with
    a header, like "service,team,cpu" on the first line and "auth,core,500"
    on the next.

    `members_csv` — the second file as one string, like "team,member" then
    "core,priya". Some names are wrapped in quotes and contain a comma.

    `min_cpu` — a whole number, like 200: the smallest CPU value to include.
    The test builds all three and hands them to you.

    YOU RETURN: a list of dictionaries, one per service that has a known
    team and enough CPU, sorted by service name. Each has "service", "team",
    "cpu" (a number) and "members" (a list of names, alphabetical).

    ─── exact rules ───
    Two CSV strings that share the column "team". Join them.

        services_csv                members_csv
        service,team,cpu            team,member
        auth,core,500               core,priya
        cron,infra,100              core,"Reyes, Ana"
        search,ghost,900            infra,marcus

    Return, for every service whose team appears in members_csv AND whose
    cpu is at least min_cpu:

        min_cpu=200
        ->  [{"service": "auth", "team": "core", "cpu": 500,
              "members": ["Reyes, Ana", "priya"]}]

      - Inner join: "search" is gone, no team "ghost" in the members file.
        "cron" is gone too, its cpu is below min_cpu.
      - cpu comes back as an int, not a string.
      - A team can have several members. Sort them alphabetically.
      - Sort the result by service name.
      - Parse both with the csv module and io.StringIO. Some member names
        are quoted and contain a comma, so split(",") will betray you.

    Joining two files on a key is the most common "write a script" task
    there is. Say which side becomes the lookup table, and why, out loud.
    '''
    raise NotImplementedError


HINTS = [
    ("Two files, two different jobs — do not loop over both at once. The "
    "members file has many rows per team, so it becomes a lookup table first: "
    "team to list of members. Then the services file is a single pass where "
    "every row asks the table one question. Building the index once is the "
    "difference between one pass and a scan per service, and saying that out "
    "loud is the point of the question."),
    ("defaultdict(list) over csv.DictReader(io.StringIO(members_csv)), keyed "
    "by row['team'], appending row['member']. Then loop the services rows: "
    "int(row['cpu']) for the number, and by_team.get(team) hands back None "
    "for a team nobody is on — that None IS your inner join, skip the row. "
    "Skip on the cpu filter too, build the dict, and finish with "
    "result.sort(key=lambda d: d['service'])."),
    ("Different data, the index and the miss:\n"
    "    import csv, io\n"
    "    from collections import defaultdict\n"
    "    raw = 'pet,owner\\ncat,\"Diaz, Sam\"\\ncat,jo\\ndog,al'\n"
    "    by_pet = defaultdict(list)\n"
    "    for row in csv.DictReader(io.StringIO(raw)):\n"
    "        by_pet[row['pet']].append(row['owner'])\n"
    "    print(dict(by_pet))     # {'cat': ['Diaz, Sam', 'jo'], 'dog': ['al']}\n"
    "    print(by_pet.get('fish'))       # None\n"
    "Use .get for the lookup, not by_pet['fish'] — indexing a defaultdict "
    "creates the missing key and your inner join quietly stops dropping rows."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

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
