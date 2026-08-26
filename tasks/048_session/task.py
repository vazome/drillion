def solve(base_url, token, agent, names):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import requests
import responses
from _lib import rng


def _gen(r):
    pool = ["api", "db", "cache", "queue", "auth", "search", "billing"]
    names = r.sample(pool, k=r.randint(2, 5))
    states = ["healthy", "degraded", "down", "draining"]
    return {"base_url": f"https://{r.choice(['ops.example.com', 'status.internal', 'sre.corp.test'])}",
            "token": f"tok-{r.randrange(16 ** 6):06x}",
            "agent": f"{r.choice(['deploybot', 'healthcheck', 'inventory'])}/{r.randint(1, 4)}.{r.randint(0, 9)}",
            "names": names,
            "status": {n: r.choice(states) for n in names}}


def _run(fn, case):
    """Run fn with Session.request spied on, so 'one session' is checkable."""
    seen = []
    real_request = requests.Session.request

    def spy(self, *args, **kwargs):
        seen.append(id(self))
        return real_request(self, *args, **kwargs)

    requests.Session.request = spy
    try:
        with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
            for name in case["names"]:
                rsps.add(responses.GET, f"{case['base_url']}/services/{name}",
                         json={"name": name, "status": case["status"][name]})
            session, statuses = fn(case["base_url"], case["token"],
                                   case["agent"], list(case["names"]))
            wire = [{"url": c.request.url,
                     "auth": c.request.headers.get("Authorization"),
                     "agent": c.request.headers.get("User-Agent"),
                     "timeout_set": c.request.req_kwargs.get("timeout") is not None}
                    for c in rsps.calls]
            return {"statuses": statuses,
                    "wire": wire,
                    "is_session": isinstance(session, requests.Session),
                    "session_auth": session.headers.get("Authorization"),
                    "session_agent": session.headers.get("User-Agent"),
                    "one_session": bool(seen) and set(seen) == {id(session)}}
    finally:
        requests.Session.request = real_request


def _reference(base_url, token, agent, names):
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {token}", "User-Agent": agent})
    statuses = {}
    for name in names:
        r = session.get(f"{base_url}/services/{name}", timeout=10)
        r.raise_for_status()
        statuses[name] = r.json()["status"]
    return session, statuses


def test_solve():
    r = rng()
    for _ in range(4):
        case = _gen(r)
        assert _run(solve, case) == _run(_reference, case)
