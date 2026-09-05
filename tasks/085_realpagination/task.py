def solve(first_url: str, token: str):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import requests
import responses
from _lib import rng


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
