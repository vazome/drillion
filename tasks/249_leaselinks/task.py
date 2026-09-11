def solve(sites, quotes):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_SITES = ["berlin", "cardiff", "dublin", "espoo", "faro", "genoa", "hague"]


def _gen(r):
    sites = _SITES[: r.randint(5, 7)]
    quotes, joined = [], [sites[0]]
    for site in sites[1:]:
        quotes.append(tuple(sorted((site, r.choice(joined)))) + (r.randint(1, 40),))
        joined.append(site)
    seen = {(a, b) for a, b, _ in quotes}
    for _ in range(r.randint(2, 6)):
        pair = tuple(sorted(r.sample(sites, 2)))
        if pair not in seen:
            seen.add(pair)
            quotes.append(pair + (r.randint(1, 40),))
    r.shuffle(quotes)
    return sorted(sites), quotes


def _reference(sites, quotes):
    parent = {site: site for site in sites}

    def root(site):
        while parent[site] != site:
            parent[site] = parent[parent[site]]
            site = parent[site]
        return site

    leased = []
    for quote in sorted(quotes, key=lambda quote: (quote[2], quote[0], quote[1])):
        left, right = root(quote[0]), root(quote[1])
        if left != right:
            parent[left] = right
            leased.append(quote)
    return leased


def test_solve():
    r = rng()
    for _ in range(12):
        sites, quotes = _gen(r)
        got, want = solve(sites, quotes), _reference(sites, quotes)
        assert got == want, f"expected {want}, got {got!r}, for {quotes}"
        assert len(got) == len(sites) - 1, f"{len(sites)} sites need {len(sites) - 1} links"

    # the three cheapest quotes leave dublin out: one of them only re-links berlin to cardiff
    fixed = [
        ("berlin", "cardiff", 1),
        ("berlin", "espoo", 1),
        ("cardiff", "espoo", 1),
        ("cardiff", "dublin", 9),
    ]
    assert solve(["berlin", "cardiff", "dublin", "espoo"], fixed) == [
        ("berlin", "cardiff", 1),
        ("berlin", "espoo", 1),
        ("cardiff", "dublin", 9),
    ], "skip a quote whose two sites are already joined, however cheap it is"

    pair = [("berlin", "cardiff", 4)]
    assert solve(["berlin", "cardiff"], pair) == pair
    assert solve(["berlin"], []) == [], "one site needs no links at all"
