---
title: Kruskal — the cheapest set of links that still connects every office
difficulty: hard
tier: advanced
minutes: 25
prereqs: [248]
tags: [graphs, sorted]
source: TheAlgorithms/Python graphs/minimum_spanning_tree_kruskal.py (MIT, adapted)
---
# Kruskal — the cheapest set of links that still connects every office

*Take the quotes cheapest first, and skip any quote whose two ends are already connected to each other some other way.*

## Read first
- [`sorted`](https://devdocs.io/python~3.14/library/functions#sorted) — `key=` with a tuple, to rank by price and break ties predictably
- [Mapping types — dict](https://devdocs.io/python~3.14/library/stdtypes#mapping-types-dict) — the dict that remembers which sites have already been joined up
- [Sequence types](https://devdocs.io/python~3.14/library/stdtypes#sequence-types-list-tuple-range) — each quote is a plain tuple, and the answer is a list of them

## Why
Seven offices, and a carrier has quoted a monthly price for a leased line between various pairs of them. Every office has to be able to reach every other one, but not directly — traffic is happy to go through another office. Finance wants the smallest total monthly bill that still leaves nobody cut off. Buying the cheapest quotes until the money runs out is how it gets done in practice, and it is how one office ends up on its own while three others have two links each.

## You get
- `sites` — the sorted list of office names.
- `quotes` — a list of `(site, site, price)` tuples in no particular order, each naming the two ends and the monthly price. The two names in a tuple are in alphabetical order, and no pair is quoted twice.

Every set of quotes you are given is enough to connect all the offices.

## You return
the quotes to buy, as a list of the same tuples, in the order you chose them.

## Rules
- A link carries traffic both ways.
- The total price of what you return has to be the lowest possible, and every office has to be reachable from every other. With `n` offices that always means exactly `n - 1` links.
- Ties would otherwise make several answers correct, so fix the order: consider the quotes sorted by `(price, first name, second name)`, and return the ones you take in that order.
- One office on its own needs no links: return `[]`.

```python
quotes = [
    ("berlin", "cardiff", 1),
    ("berlin", "espoo", 1),
    ("cardiff", "espoo", 1),
    ("cardiff", "dublin", 9),
]
solve(["berlin", "cardiff", "dublin", "espoo"], quotes)
# -> [("berlin", "cardiff", 1), ("berlin", "espoo", 1), ("cardiff", "dublin", 9)]
```

> [!WARNING]
> The three cheapest quotes above cost 3 in total and leave Dublin unreachable — they buy a triangle between the other three offices, and the third of them joins two sites that were already connected. Taking the `n - 1` cheapest quotes is not the answer. Every quote has to be checked against what is already joined up, and skipped when it would only add a second path between two offices that already have one.

> [!NOTE]
> "Already joined up" is the same question as topic 248's `same`: two sites are in one group once a link is bought between their groups. The whole algorithm is that check, run over the quotes in price order.

## Hints
### Hint 1
Sort the quotes by `(price, first, second)` and walk them once. That is the outer shape, and everything else is deciding whether to take the quote in front of you.
### Hint 2
Give every site a pointer to itself in a dict. To take a quote, follow both ends to the end of their chains: two different ends means the quote connects two groups that were separate, so take it and point one end at the other. The same end on both sides means the two offices already reach each other, so skip it.
### Hint 3
The same greedy pass, choosing which roads to grit overnight so every village stays reachable:

```python
def grit(villages, roads):
    group = {village: village for village in villages}

    def end(village):
        while group[village] != village:
            village = group[village]
        return village

    chosen = []
    for road in sorted(roads, key=lambda road: (road[2], road[0], road[1])):
        left, right = end(road[0]), end(road[1])
        if left != right:
            group[left] = right
            chosen.append(road)
    return chosen
```

The `if` is the whole algorithm: without it you have "the cheapest few roads", which is a different and wrong answer.

---
Adapted from TheAlgorithms/Python — MIT
