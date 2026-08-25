def solve(url, token, params):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import requests
import responses
from _lib import rng


def _gen(r, status=None):
    """One request/response pair. `status` pins the status code when given."""
    host = r.choice(["api.example.com", "deploys.internal", "gw.corp.test"])
    path = r.choice(["/v1/deploys", "/api/services", "/v2/releases"])
    status = status or r.choice([200, 200, 201, 202])
    params = {"env": r.choice(["prod", "stage", "dev"]), "limit": r.randint(5, 50)}
    if r.random() < 0.5:
        params["team"] = r.choice(["core", "data", "sre"])
    if status >= 400:
        body = {"message": r.choice(["Not Found", "internal error", "no such release"])}
    else:
        body = {"items": [{"id": r.randint(1, 99), "state": r.choice(["done", "failed"])}
                          for _ in range(r.randint(1, 3))],
                "total": r.randint(1, 5)}
    return {"url": f"https://{host}{path}", "token": f"tok-{r.randrange(16 ** 6):06x}",
            "params": params, "status": status, "body": body}


def _run(fn, case):
    """Run fn against a mocked endpoint; report the answer AND what it sent."""
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        rsps.add(responses.GET, case["url"], json=case["body"], status=case["status"])
        try:
            answer = ("returned", fn(case["url"], case["token"], dict(case["params"])))
        except NotImplementedError:                  # the empty stub, not an answer
            raise
        except requests.exceptions.HTTPError:
            answer = ("raised HTTPError", None)
        if not rsps.calls:
            return answer, {"calls": 0}
        sent = rsps.calls[0].request
        return answer, {"calls": len(rsps.calls),
                        "auth": sent.headers.get("Authorization"),
                        "query": dict(sent.params),
                        "timeout_set": sent.req_kwargs.get("timeout") is not None}


def _reference(url, token, params):
    r = requests.get(url, params=params,
                     headers={"Authorization": f"Bearer {token}"}, timeout=10)
    r.raise_for_status()
    return r.json()


def test_solve():
    r = rng()
    for status in [None, None, 202, 404, 500]:       # every seed sees both endings
        case = _gen(r, status)
        assert _run(solve, case) == _run(_reference, case)
