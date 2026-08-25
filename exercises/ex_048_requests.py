"""Half of platform work is one HTTP call to somebody else's API, done properly."""

import requests
import responses
from _lib import rng

META = {"topic": 48, "title": "requests — params, auth header, timeout, raise_for_status",
        "tier": 3, "minutes": 18, "prereqs": []}


def solve(url, token, params):
    """WHY: The team's deploy dashboard needs the latest deploys from an
    internal deployment service. That service has a web API: you send a
    request to a web address with a few filters (which environment, how
    many) and a secret token that proves who you are, and it answers with
    data. Platform work is full of this one call, and the usual mistakes
    cause real outages: no time limit, so a dead server freezes your script
    forever; ignoring error answers, so a broken server looks like "no
    deploys today". You are asked to make that one call properly.

    YOU GET: `url` — a string web address like
    "https://api.example.com/v1/deploys".
    `token` — a string secret like "tok-91ab3c" the server uses to check you
    are allowed in.
    `params` — a dict of filters like {"env": "prod", "limit": 20} to send
    along with the request.
    The test points the requests library at a fake server, so nothing real
    is contacted; it then inspects exactly what your request contained.

    YOU RETURN: the server's answer decoded from JSON into Python data (a
    dict or list), exactly as it came. If the server answered with an error
    code like 404 or 500, do not return anything: let the library's
    HTTPError escape.

    ─── exact rules ───
    Make one authenticated GET and hand back the decoded body.

    Four things, all of them graded:

      - GET `url`, sending `params` as the query string. Pass them
        through the params= argument; do not glue them onto the url
        yourself and do not url-encode anything by hand.
      - Send the header  Authorization: Bearer <token>
      - Pass timeout=. Any number. This one is not optional.
      - Call raise_for_status(), then return the parsed JSON body.

        solve("https://api.example.com/v1/deploys",
              "tok-91ab3c",
              {"env": "prod", "limit": 20})
        ->  {"items": [{"id": 7, "state": "done"}], "total": 1}

    So: the return value is whatever .json() gives you, nothing wrapped
    around it, and nothing pulled out of it.

    The server does not always answer 200. 201 and 202 are successes
    too — return their bodies exactly the same way. 404 and 500 are
    not: raise_for_status turns those into
    requests.exceptions.HTTPError, and that error must escape solve.
    Do not catch it, do not translate it into your own exception, and
    do not write `if r.status_code == 200` instead — that test calls a
    202 a failure and quietly does the wrong thing on a 500.

    Nothing here touches the internet. The test points requests at a
    fake transport and then reads back what you sent: the header, the
    query string, and whether a timeout was set. Getting the answer
    right while sending it wrong still fails.
    """
    raise NotImplementedError


HINTS = [
    ("requests.get hands you a Response object, not the body — the body only "
    "appears when you ask for it. Everything else in this drill is keyword "
    "arguments on that one call: where the query string comes from, where the "
    "header comes from, how long you are prepared to wait. The timeout is the "
    "one people leave off, and it is the one that hurts: with no timeout a "
    "dead peer parks your worker forever, and a thread pool of those is an "
    "outage. Also worth being precise about: a 4xx or 5xx is still a perfectly "
    "normal response object, so nothing raises unless you ask it to."),
    ("One call: requests.get(url, params=..., headers=..., timeout=...). params "
    "takes the dict as-is. headers takes a dict too, and the value you want is "
    "the string 'Bearer ' with the token after it. Then two lines on the "
    "response: .raise_for_status() to convert a bad status into an exception, "
    "and .json() to decode the body. Order matters — check the status before "
    "you trust the body."),
    ("Different data — one call to a weather API that wants a key header:\n"
    "    r = requests.get('https://wx.example.com/v1/now',\n"
    "                     params={'city': 'Vilnius', 'units': 'metric'},\n"
    "                     headers={'X-Api-Key': 'abc123'},\n"
    "                     timeout=10)\n"
    "    r.raise_for_status()          # HTTPError on 4xx/5xx, silent on 2xx\n"
    "    print(r.url)                  # .../v1/now?city=Vilnius&units=metric\n"
    "    print(r.json())               # {'temp': 14.2, 'wind': 3}\n"
    "Yours is the same four arguments and the same two lines after, with a "
    "Bearer token instead of an api key header."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

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
