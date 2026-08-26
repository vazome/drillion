---
title: csv — inner-join two CSVs on a shared key
difficulty: medium
tier: core
minutes: 30
prereqs: [30]
tags: [csv]
practices: [30, 17, 19]
---
# csv — inner-join two CSVs on a shared key

*Whole-task task: two CSVs, one shared column, join and filter.*

Combines topics 32 (csv), 18 (dict lookups), 20 (defaultdict grouping).

## Why
One spreadsheet lists services with the team that owns each and its CPU allocation. Another lists which people are on which team. A manager asks "for every service using at least 200 CPU, who do I contact?" That means matching rows from the two files on the shared "team" column, which is the single most common "write a quick script" request in ops.

## You get
`services_csv` — the first file as one string in CSV form with a header, like `"service,team,cpu"` on the first line and `"auth,core,500"` on the next.

`members_csv` — the second file as one string, like `"team,member"` then `"core,priya"`. Some names are wrapped in quotes and contain a comma.

`min_cpu` — a whole number, like `200`: the smallest CPU value to include. The test builds all three and hands them to you.

## You return
a list of dictionaries, one per service that has a known team and enough CPU, sorted by service name. Each has `"service"`, `"team"`, `"cpu"` (a number) and `"members"` (a list of names, alphabetical).

## Rules
Two CSV strings that share the column `"team"`. Join them.

`services_csv`:

```text
service,team,cpu
auth,core,500
cron,infra,100
search,ghost,900
```

`members_csv`:

```text
team,member
core,priya
core,"Reyes, Ana"
infra,marcus
```

Return, for every service whose team appears in `members_csv` AND whose cpu is at least `min_cpu`:

```python
solve(services_csv, members_csv, 200)
# -> [{"service": "auth", "team": "core", "cpu": 500,
#      "members": ["Reyes, Ana", "priya"]}]
```

- Inner join: `"search"` is gone, no team `"ghost"` in the members file. `"cron"` is gone too, its cpu is below `min_cpu`.
- `cpu` comes back as an `int`, not a string.
- A team can have several members. Sort them alphabetically.
- Sort the result by service name.

> [!WARNING]
> Parse both with the `csv` module and `io.StringIO`. Some member names are quoted and contain a comma, so `split(",")` will betray you.

> [!TIP]
> Joining two files on a key is the most common "write a script" task there is. Say which side becomes the lookup table, and why, out loud.

## Hints
### Hint 1
Two files, two different jobs — do not loop over both at once. The members file has many rows per team, so it becomes a lookup table first: team to list of members. Then the services file is a single pass where every row asks the table one question. Building the index once is the difference between one pass and a scan per service, and saying that out loud is the point of the question.
### Hint 2
defaultdict(list) over csv.DictReader(io.StringIO(members_csv)), keyed by row['team'], appending row['member']. Then loop the services rows: int(row['cpu']) for the number, and by_team.get(team) hands back None for a team nobody is on — that None IS your inner join, skip the row. Skip on the cpu filter too, build the dict, and finish with result.sort(key=lambda d: d['service']).
### Hint 3
Different data, the index and the miss:

```python
import csv, io
from collections import defaultdict
raw = 'pet,owner\ncat,"Diaz, Sam"\ncat,jo\ndog,al'
by_pet = defaultdict(list)
for row in csv.DictReader(io.StringIO(raw)):
    by_pet[row['pet']].append(row['owner'])
print(dict(by_pet))     # {'cat': ['Diaz, Sam', 'jo'], 'dog': ['al']}
print(by_pet.get('fish'))       # None
```

Use .get for the lookup, not by_pet['fish'] — indexing a defaultdict creates the missing key and your inner join quietly stops dropping rows.
