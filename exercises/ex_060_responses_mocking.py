"""A test that hits the real API is slow, flaky, and fails when someone else's cert expires."""

import requests
import responses
from _lib import rng

META = {"topic": 60, "title": "responses — mock the HTTP the code under test will make",
        "tier": 4, "minutes": 20, "prereqs": [48], "tags": ["testing", "requests"]}


def solve(rsps, spec):
    """WHY: An inventory script (fetch_inventory, at the bottom of this file,
    already written) talks to a hosts API: list the hosts, ask each one for
    its CPU count, then post a report. To test it in CI without a real
    server, you set up a fake server that answers exactly the requests the
    script will make: the host list, one answer per host (some of them "404
    gone"), and the report endpoint. The fake is strict: a request it was
    not told about fails, and an answer you registered that the script never
    asked for also fails. Your job: read the script, then register precisely
    the answers it needs, built from a spec that changes every run.

    YOU GET: `rsps` — the active fake server object (a
    responses.RequestsMock). You register answers on it; the test then runs
    the real script through it. Nothing real is contacted.
    `spec` — a dict describing what the fake must answer, like
    {"base_url": "https://inv.example.com", "token": "tok-4f9a",
    "hosts": ["web-1", "db-2"], "cpu": {"web-1": 8}, "missing": ["db-2"],
    "report_id": "rep-77"}.

    YOU RETURN: nothing. The test calls fetch_inventory afterwards and
    checks what it produced and which requests it made.

    ─── exact rules ───
    Stand up the fake API that fetch_inventory needs, from `spec`.

    fetch_inventory lives at the bottom of this file. It is already
    written and you must not change it. Read it first: every request it
    makes has to exist in the mock before it runs, or requests raises
    ConnectionError.

    `rsps` is an active responses.RequestsMock. Register endpoints on
    it with rsps.add(...). `responses` is already imported up top.
    `spec` says what each endpoint must answer:

        spec = {"base_url": "https://inv.example.com",
                "token": "tok-4f9a",
                "hosts": ["web-1", "db-2"],   # the listing must return these
                "cpu": {"web-1": 8},          # these answer 200 with that cpu
                "missing": ["db-2"],          # these answer 404
                "report_id": "rep-77"}

    For that spec, exactly four registrations must exist:

        GET   https://inv.example.com/v1/hosts        200  {"hosts": ["web-1", "db-2"]}
        GET   https://inv.example.com/v1/hosts/web-1  200  {"cpu": 8}
        GET   https://inv.example.com/v1/hosts/db-2   404  body does not matter
        POST  https://inv.example.com/v1/reports      200  {"id": "rep-77"}

    and fetch_inventory(base_url, token) then returns

        {"hosts": [{"name": "web-1", "cpu": 8},
                   {"name": "db-2", "cpu": None}],
         "report_id": "rep-77"}

    which is what the test checks. solve itself returns nothing — the
    test calls fetch_inventory afterwards and grades the result.

    Two rules the mock enforces:
      - Register every call the client makes. One it did not expect is
        a ConnectionError, not a 404.
      - Register nothing else. This mock is strict about unused
        registrations and fails at the end of the block if one never
        fired. So no shotgunning every host into every shape.

    The spec varies each run: different host names, a different number
    of missing ones, different cpu counts. Build the registrations by
    walking the spec, not by typing them out.
    """
    raise NotImplementedError


HINTS = [
    ("The mock is a registry, not a proxy. Nothing is recorded or forwarded: "
    "you declare, up front, which (method, url) pairs exist and what each one "
    "answers, and any request outside that list fails. So the work is not "
    "really about the library — it is reading the client and listing the calls "
    "it will make, in the shapes it will make them: one listing call, one call "
    "per host, one write at the end. Notice which of those depend on data the "
    "previous response returned, because that decides what your listing "
    "registration has to say."),
    ("rsps.add(responses.GET, url, json={...}, status=200) is the whole api. "
    "json= takes a Python object and serialises it; status= defaults to 200, "
    "so you only pass it for the 404s. responses.POST is how you register the "
    "write — a POST url registered as a GET will not match. The url argument "
    "is the full url with no query string; query params on the request are "
    "ignored when the registered url has none. Three loops and one plain "
    "registration will cover it."),
    ("Different data — mocking a payments client that checks a balance then "
    "charges:\n"
    "    with responses.RequestsMock() as rsps:\n"
    "        rsps.add(responses.GET, 'https://pay.test/v1/balance',\n"
    "                 json={'cents': 500})\n"
    "        rsps.add(responses.POST, 'https://pay.test/v1/charge', status=402)\n"
    "        r = requests.get('https://pay.test/v1/balance', timeout=5)\n"
    "        print(r.json())                     # {'cents': 500}\n"
    "        print(requests.post('https://pay.test/v1/charge',\n"
    "                            timeout=5).status_code)      # 402\n"
    "        print(len(rsps.calls))              # 2\n"
    "Yours is the same three arguments, just produced in a loop from the spec "
    "instead of written out one at a time."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def fetch_inventory(base_url, token):
    """The code under test. Read it, do not change it, do not call it yourself."""
    session = requests.Session()
    session.headers["Authorization"] = f"Bearer {token}"

    listing = session.get(f"{base_url}/v1/hosts", params={"region": "eu"}, timeout=5)
    listing.raise_for_status()

    hosts = []
    for name in listing.json()["hosts"]:
        detail = session.get(f"{base_url}/v1/hosts/{name}", timeout=5)
        if detail.status_code == 404:               # a host can vanish mid-scan
            hosts.append({"name": name, "cpu": None})
            continue
        detail.raise_for_status()
        hosts.append({"name": name, "cpu": detail.json()["cpu"]})

    report = session.post(f"{base_url}/v1/reports", json={"hosts": hosts}, timeout=5)
    report.raise_for_status()
    return {"hosts": hosts, "report_id": report.json()["id"]}


def _gen(r):
    """A fixture spec: which hosts exist, which are gone, what each reports."""
    kinds = ["web", "db", "cache", "queue", "batch", "edge"]
    n = r.randint(3, 5)
    hosts = [f"{kind}-{i + 1}" for i, kind in enumerate(r.sample(kinds, k=n))]
    missing = r.sample(hosts, k=r.randint(1, n - 2))          # always at least one 404
    alive = [h for h in hosts if h not in missing]
    cpus = r.sample([1, 2, 4, 8, 16, 32, 64], k=len(alive))   # always differ from each other
    return {"base_url": f"https://{r.choice(['inv.example.com', 'cmdb.internal', 'fleet.corp.test'])}",
            "token": f"tok-{r.randrange(16 ** 6):06x}",
            "hosts": hosts,
            "cpu": dict(zip(alive, cpus)),
            "missing": missing,
            "report_id": f"rep-{r.randrange(16 ** 4):04x}"}


def _run(fn, spec):
    """Let fn register the mocks, then run the real client through them."""
    with responses.RequestsMock(assert_all_requests_are_fired=True) as rsps:
        fn(rsps, spec)
        result = fetch_inventory(spec["base_url"], spec["token"])
        seen = [(c.request.method, c.request.url.split("?")[0]) for c in rsps.calls]
        return result, seen


def _reference(rsps, spec):
    base = spec["base_url"]
    rsps.add(responses.GET, f"{base}/v1/hosts", json={"hosts": spec["hosts"]})
    for name, cpu in spec["cpu"].items():
        rsps.add(responses.GET, f"{base}/v1/hosts/{name}", json={"cpu": cpu})
    for name in spec["missing"]:
        rsps.add(responses.GET, f"{base}/v1/hosts/{name}",
                 json={"message": "no such host"}, status=404)
    rsps.add(responses.POST, f"{base}/v1/reports", json={"id": spec["report_id"]})


def test_solve():
    r = rng()
    for _ in range(4):
        spec = _gen(r)
        assert _run(solve, spec) == _run(_reference, spec)
