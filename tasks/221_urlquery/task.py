from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


def solve(url: str, key: str, value: str) -> str:
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    pairs = [("tag", r.choice(["blue", "red", "green"])),
             ("q", r.choice(["dry cider", "oat milk", "rye"])),
             ("tag", r.choice(["sale", "new"])),
             ("page", str(r.randint(1, 9)))]
    r.shuffle(pairs)
    if r.random() < 0.4:
        pairs.append(("debug", ""))
    query = urlencode(pairs[: r.randint(0, len(pairs))])
    fragment = r.choice(["", "results", "top"])
    url = urlunsplit(("https", r.choice(["ex.com", "shop.example"]),
                      r.choice(["/search", "/a/b", "/"]), query, fragment))
    key = r.choice(["page", "q", "tag", "sort"])
    return url, key, r.choice(["2", "new value", "a&b"])


def _reference(url, key, value):
    parts = urlsplit(url)
    pairs, done = [], False
    for name, existing in parse_qsl(parts.query, keep_blank_values=True):
        if name != key:
            pairs.append((name, existing))
        elif not done:
            pairs.append((name, value))
            done = True
    if not done:
        pairs.append((key, value))
    return urlunsplit(parts._replace(query=urlencode(pairs)))


def test_solve():
    assert solve("https://ex.com/search?tag=a&q=old&tag=b#top", "q", "new") == (
        "https://ex.com/search?tag=a&q=new&tag=b#top"
    ), "both tags survive, in place, and the fragment stays on the end"
    assert solve("https://ex.com/search", "page", "2") == "https://ex.com/search?page=2", (
        "a URL with no query yet grows one"
    )
    assert solve("https://ex.com/s?page=1&page=9", "page", "3") == "https://ex.com/s?page=3", (
        "the first copy is set, later copies are dropped"
    )

    r = rng()
    for _ in range(10):
        url, key, value = _gen(r)
        mine = solve(url, key, value)
        assert mine == _reference(url, key, value), f"setting {key}={value!r} on {url}"
        # a dict-shaped answer stringifies a repeated parameter as a Python list
        assert "%5B%27" not in mine, f"a repeated parameter was collapsed into a list: {mine}"
