import ipaddress


def solve(networks: list[str], addresses: list[str]) -> dict[str, str]:
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    second, third = r.randrange(0, 250), r.randrange(0, 250)
    # deliberately nested, and shuffled so the broadest block is often tested first
    networks = ["10.0.0.0/8", f"10.{second}.0.0/16", f"10.{second}.{third}.0/24",
                "172.16.0.0/12", f"172.16.{third}.0/24"]
    r.shuffle(networks)
    addresses = [
        f"10.{second}.{third}.{r.randrange(1, 254)}",
        f"10.{second}.{(third + 7) % 250}.{r.randrange(1, 254)}",
        f"10.{(second + 11) % 250}.{r.randrange(0, 254)}.{r.randrange(1, 254)}",
        f"172.16.{third}.{r.randrange(1, 254)}",
        f"192.0.2.{r.randrange(1, 254)}",
    ]
    r.shuffle(addresses)
    return networks, addresses


def _reference(networks, addresses):
    parsed = [(ipaddress.ip_network(text), text) for text in networks]
    out = {}
    for text in addresses:
        ip = ipaddress.ip_address(text)
        hits = [pair for pair in parsed if ip in pair[0]]
        if hits:
            out[text] = max(hits, key=lambda pair: pair[0].prefixlen)[1]
    return out


def test_solve():
    assert solve(["10.0.0.0/8", "10.4.7.0/24"], ["10.4.7.9", "10.9.9.9", "192.0.2.1"]) == {
        "10.4.7.9": "10.4.7.0/24",
        "10.9.9.9": "10.0.0.0/8",
    }, "the /24 wins over the /8, and an address outside both is absent"

    r = rng()
    for _ in range(8):
        networks, addresses = _gen(r)
        mine, theirs = solve(list(networks), list(addresses)), _reference(networks, addresses)
        assert mine == theirs, f"networks {networks} against {addresses}"
        # spelled out, because a first-match answer agrees with the reference on every
        # address that only one network contains and differs only on the nested ones
        for address, cidr in theirs.items():
            assert mine.get(address) == cidr, (
                f"{address} belongs to {cidr}, the longest prefix containing it, not {mine.get(address)}"
            )
