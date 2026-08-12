"""split(',') corrupts real CSV the day a field grows a comma."""

from _lib import rng

META = {"topic": 32, "title": "csv — parse quoted fields correctly", "tier": 3,
        "minutes": 10, "prereqs": []}


def solve(text):
    """Parse CSV text into a list of dicts, one per data row.

        'service,owner,cpu\\nauth,"Reyes, Ana",250m\\ncron,priya,100m'
        ->
        [{"service": "auth", "owner": "Reyes, Ana", "cpu": "250m"},
         {"service": "cron", "owner": "priya", "cpu": "100m"}]

    The first line is the header. All values stay strings. Some owner
    fields are quoted and contain a comma — split(",") shreds those rows,
    which is the whole point of this drill.

    text is a string, not a file: use io.StringIO to give the csv module
    the file-like object it wants. No real files.
    """
    raise NotImplementedError


HINTS = [
    "Count the commas on a quoted row: split(',') sees four fields where "
    "there are three. CSV quoting rules (commas inside quotes don't split, "
    "doubled quotes escape) are exactly what the csv module exists to handle "
    "— never reimplement them.",
    "csv.DictReader reads the header row itself and yields one dict per data "
    "row. It wants a file-like object, and io.StringIO(text) turns your "
    "string into one. Wrap the reader in list().",
    "Different data, same shape:\n"
    "    import csv, io\n"
    "    raw = 'city,motto\\nParis,\"Fluctuat, nec mergitur\"\\nOslo,Blue'\n"
    "    print(list(csv.DictReader(io.StringIO(raw))))\n"
    "    # [{'city': 'Paris', 'motto': 'Fluctuat, nec mergitur'},\n"
    "    #  {'city': 'Oslo', 'motto': 'Blue'}]\n"
    "    print(raw.splitlines()[1].split(','))\n"
    "    # ['Paris', '\"Fluctuat', ' nec mergitur\"']   <- shredded\n"
    "The reader undid the quotes; the naive split tore the field in half.",
]


# ─────────────────────────────  below here is the machinery  ──────────────

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
