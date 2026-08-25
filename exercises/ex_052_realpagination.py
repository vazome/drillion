"""GitHub-shaped APIs hide the next page in a header, and requests already parsed it.

Topic 52 on the checklist is FastAPI. That needs a running server and packages we
do not have offline, so this slot drills real-API pagination instead — the same
loop as topic 49, but against actual requests/Response objects rather than a fake.
"""

import requests
import responses
from _lib import rng

META = {"topic": 52, "title": "Link header pagination — follow rel=next with requests",
        "tier": 4, "minutes": 25, "prereqs": [48, 49], "tags": ["http", "requests"]}


def solve(first_url, token):
    """WHY: A manager wants every open issue in the team's repo on a
    GitHub-style server, to build a backlog report. The server hands back
    issues a few at a time, and it tells you where the next batch lives not
    in the data but in a response header called Link: a line listing web
    addresses labelled next, prev, first and last. You must follow the
    "next" address until there is none, send the token and a time limit
    with every request, and never guess at addresses yourself, because the
    server only answers addresses it handed out.

    YOU GET: `first_url` — a string: the web address of the first page,
    like "https://api.github.test/repos/sre/runbooks/issues?page=1".
    `token` — a string secret that proves who you are.
    The test points the requests library at a fake server with made-up
    pages and inspects each request you made; nothing real is contacted.

    YOU RETURN: one flat list of every issue dict from every page, in the
    order received, like [{"number": 412, "title": "flaky test"}, ...].

    ─── exact rules ───
    Collect every item the API will give you, across all pages.

    GET `first_url` with the header  Authorization: Bearer <token>
    and a timeout=, call raise_for_status(), and keep going until the
    server stops offering a next page.

    Each response body is a JSON array of objects:

        [{"number": 412, "title": "flaky test"},
         {"number": 415, "title": "rotate certs"}]

    The pointer to the next page is not in the body. It is in the Link
    header, GitHub style:

        Link: <https://api.example.com/...?page=2&per_page=2>; rel="next",
              <https://api.example.com/...?page=4&per_page=2>; rel="last"

    requests parses that for you into response.links, a dict keyed by
    rel:

        {"next": {"url": "https://...page=2&per_page=2", "rel": "next"},
         "last": {"url": "https://...page=4&per_page=2", "rel": "last"}}

    Return one flat list of every item dict, in the order the pages
    handed them over:

        page 1  ->  [{"number": 412, "title": "flaky test"}]
        page 2  ->  [{"number": 415, "title": "rotate certs"}]
        ->  [{"number": 412, "title": "flaky test"},
             {"number": 415, "title": "rotate certs"}]

    Three ways this goes wrong:
      - "links is empty" is not the stop signal. The last page still
        advertises first and prev; what it lacks is next. Ask for the
        "next" key specifically.
      - Do not build page urls yourself. Send back the url the server
        gave you, whole, query string and all. Page 2 is not always
        just page=2 — servers change the page size or hand you a
        cursor, and this API only answers urls it has issued.
      - Every request needs the token and the timeout, not just the
        first one.

    A one-page response has no Link header at all. That must work too,
    with the same loop.
    """
    raise NotImplementedError


HINTS = [
    ("You cannot know the page count up front, so this is a while loop, and the "
    "thing that survives each turn is the url to fetch next. Two details are "
    "specific to HTTP: the pointer lives in a response header rather than in "
    "the JSON, and requests has already turned that header into a small dict "
    "for you, so there is no parsing to write. The stop condition is the "
    "absence of one particular rel, not the absence of links."),
    ("Keep a url variable starting at first_url and an items list outside the "
    "loop. Inside: requests.get(url, headers=..., timeout=...), "
    "raise_for_status(), items.extend(r.json()) — extend, since the body is "
    "already a list — then look at r.links. r.links.get('next') gives you "
    "either None or a dict with a 'url' key, which is exactly what decides "
    "whether the loop runs again. `while url:` reads well once url becomes "
    "None at the end."),
    ("Different data — walking an audit log the same way:\n"
    "    url = 'https://audit.example.com/events?since=monday'\n"
    "    rows = []\n"
    "    while url:\n"
    "        r = requests.get(url, headers={'X-Api-Key': 'k-9'}, timeout=10)\n"
    "        r.raise_for_status()\n"
    "        rows.extend(r.json())\n"
    "        print(r.links)   # {'next': {'url': '...&cursor=e4f', 'rel': 'next'},\n"
    "                         #  'first': {'url': '...', 'rel': 'first'}}\n"
    "        nxt = r.links.get('next')\n"
    "        url = nxt['url'] if nxt else None\n"
    "    print(len(rows))     # 57\n"
    "Same three beats as yours: fetch, accumulate, ask the response where to "
    "go next."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r, n_pages=None):
    """Build the page set: urls, bodies, and the Link header each one sends."""
    base = (f"https://{r.choice(['api.github.test', 'git.internal', 'hub.corp.test'])}"
            f"/repos/{r.choice(['platform', 'sre', 'data-eng'])}"
            f"/{r.choice(['terraform', 'runbooks', 'pipelines'])}/issues")
    per_page = r.choice([2, 3, 5])
    n = n_pages or r.randint(2, 5)
    verbs = ["fix", "rotate", "drain", "upgrade", "revert", "document"]
    nouns = ["certs", "node pool", "flaky test", "helm chart", "runbook", "alert"]

    def url(i):
        return f"{base}?page={i}&per_page={per_page}"

    pages = []
    for i in range(1, n + 1):
        count = per_page if i < n else r.randint(1, per_page)
        items = [{"number": r.randint(100, 999),
                  "title": f"{r.choice(verbs)} {r.choice(nouns)}"} for _ in range(count)]
        rels = []
        if i < n:
            rels.append(f'<{url(i + 1)}>; rel="next"')
            rels.append(f'<{url(n)}>; rel="last"')
        if i > 1:
            rels.append(f'<{url(i - 1)}>; rel="prev"')
            rels.append(f'<{url(1)}>; rel="first"')
        pages.append((url(i), items, ", ".join(rels)))
    return {"first_url": url(1), "token": f"tok-{r.randrange(16 ** 6):06x}", "pages": pages}


def _run(fn, case):
    """Run fn against the mocked pages; report the answer AND every call made."""
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        for url, items, link in case["pages"]:
            rsps.add(responses.GET, url, json=items,
                     headers={"Link": link} if link else None)
        answer = fn(case["first_url"], case["token"])
        wire = [(c.request.url,
                 c.request.headers.get("Authorization"),
                 c.request.req_kwargs.get("timeout") is not None) for c in rsps.calls]
        return answer, wire


def _reference(first_url, token):
    items = []
    url = first_url
    headers = {"Authorization": f"Bearer {token}"}
    while url:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        items.extend(r.json())
        nxt = r.links.get("next")
        url = nxt["url"] if nxt else None
    return items


def test_solve():
    r = rng()
    for n_pages in [1, 2, 4, None]:      # one page, two pages, and a middle to skip
        case = _gen(r, n_pages)
        assert _run(solve, case) == _run(_reference, case)
