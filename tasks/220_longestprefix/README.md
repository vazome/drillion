---
title: ipaddress — which subnet does this address really belong to?
difficulty: medium
tier: core
minutes: 18
prereqs: [12, 25]
tags: [stdlib-ops, dicts]
---
# ipaddress — which subnet does this address really belong to?

*`ipaddress` turns the strings in a routing table into objects that know how to answer "does this contain that?".*

## Read first
- [`ipaddress`](https://devdocs.io/python~3.14/library/ipaddress) — `ip_address`, `ip_network` and what each one accepts
- [`IPv4Network`](https://devdocs.io/python~3.14/library/ipaddress#ipaddress.IPv4Network) — `prefixlen`, and the `in` test for membership
- [`max`](https://devdocs.io/python~3.14/library/functions#max) — picking a winner with `key=`

## Why
The firewall rules are written per subnet, and the subnets overlap on purpose: `10.0.0.0/8` is the catch-all for the whole office, `10.4.0.0/16` is the finance floor, and `10.4.7.0/24` is the payments rack inside it. Every one of those three contains the address `10.4.7.9`, and only one of them is the rule that applies to it. Routers settle this with a single convention that has been the same since the 1990s: the most specific subnet wins. Get it wrong and finance's rule quietly governs the payments rack.

## You get
`networks` — a list of CIDR strings such as `["10.0.0.0/8", "10.4.7.0/24"]`, in no particular order and all distinct.

`addresses` — a list of plain IPv4 address strings such as `["10.4.7.9", "192.0.2.1"]`.

## You return
a `dict` mapping each address that lands inside at least one network to the CIDR string it belongs to, spelled exactly as it appeared in `networks`.

## Rules
- An address that no network contains is left out of the dictionary entirely.
- When several networks contain the same address, the winner is the one with the longest prefix — the larger number after the slash, the smaller block.
- Keys are the address strings you were given, unchanged. Values are the CIDR strings you were given, unchanged.
- Every network is a valid CIDR block with its host bits already clear, and every address is a valid IPv4 address.

```python
solve(["10.0.0.0/8", "10.4.7.0/24"], ["10.4.7.9", "10.9.9.9", "192.0.2.1"])
# -> {"10.4.7.9": "10.4.7.0/24", "10.9.9.9": "10.0.0.0/8"}
```

> [!WARNING]
> Stopping at the first network that matches is the near-miss this task exists to catch. `networks` is unordered, so the broad `/8` is often the first thing you test, and the answer that comes out looks entirely reasonable until someone asks why the payments rack is on the finance rule.

## Hints
### Hint 1
`ipaddress.ip_address("10.4.7.9") in ipaddress.ip_network("10.4.7.0/24")` is the whole membership test — no masking arithmetic of your own.
### Hint 2
Collect *all* the matches for an address rather than breaking out of the loop, then choose between them afterwards.
### Hint 3
`prefixlen` is the number after the slash, and it is exactly the specificity ranking:

```python
best = max(matches, key=lambda net: net.prefixlen)
```

Keep the original string beside each network — pairing them up front, or looking the string up by index, saves you from rebuilding the CIDR text by hand.
