def solve(rsps, spec):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import requests
import responses
from _lib import rng


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
