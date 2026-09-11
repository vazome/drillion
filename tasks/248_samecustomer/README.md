---
title: union-find — merge duplicate account records as the matches arrive
difficulty: hard
tier: advanced
minutes: 25
prereqs: [57, 244]
tags: [graphs, classes]
---
# union-find — merge duplicate account records as the matches arrive

*Every id points at another id in its group, and following those pointers to the end tells two ids apart in one step.*

## Read first
- [Mapping types — dict](https://devdocs.io/python~3.14/library/stdtypes#mapping-types-dict) — `setdefault`, for an id that is being merged for the first time
- [Classes](https://devdocs.io/python~3.14/tutorial/classes) — the state lives on the instance, so two books of records never share it
- [`sorted`](https://devdocs.io/python~3.14/library/functions#sorted) — sorting a list of lists compares them element by element

## Why
Support opened three tickets from one customer under three account ids, because the customer signed up twice on the website and once through the app. A matching job runs over the data and reports pairs: this account and that account are the same person. The pairs arrive in no particular order, and half of them are things you already knew. What the billing run needs is the merged view — one list of ids per real person — and what the support console needs, live, is a straight yes or no for two ids on screen.

## You get
nothing to start — you return a class. The test builds it and drives it, like

```python
Records = solve()
book = Records()
book.link("acct-001", "acct-002")
book.same("acct-001", "acct-002")   # -> True
```

## You return
the class itself, not an instance of it.

## Rules
Your class takes no arguments and offers three methods:

- `link(one, other)` — record that these two ids belong to the same person. Either id may be new, may already be in a group, or the pair may have been reported before.
- `same(one, other)` — a real `bool`: are these two ids the same person? Two ids nobody ever mentioned are two different people, and an id is always the same person as itself.
- `groups()` — one sorted list of ids per person, the lists in order of their first id. Only ids that have appeared in a `link` are in there.

```python
book = Records()
book.link("acct-001", "acct-002")
book.link("acct-003", "acct-004")
book.link("acct-001", "acct-003")
book.same("acct-002", "acct-004")   # -> True
book.groups()   # -> [["acct-001", "acct-002", "acct-003", "acct-004"]]
```

> [!WARNING]
> `parent[one] = other` looks like it records the merge, and it loses records. In the example above `acct-001` already points at `acct-002` when the third merge arrives; overwriting that pointer leaves `acct-002` behind in a group of its own, and a customer's invoices split in two. Point the **end of one chain** at the end of the other, never the id you were handed.

> [!NOTE]
> Chains that are only ever appended to get long, and every `same` walks one to the end. Repoint the ids you pass on the way, so the next walk is shorter: that one extra line is the difference between a console that answers instantly and one that gets slower every week.

## Hints
### Hint 1
Keep `self.parent`, a dict from an id to the next id in its group. An id that points at itself is the end of a chain — the one id that stands for the whole group.
### Hint 2
Write the walk to the end first, as a small helper: follow `self.parent` until an id points at itself, and return that id. Then `same` is two calls to it compared with `==`, and `link` is one call for each side, with the first result pointed at the second.
### Hint 3
The same idea, grouping photographs that turn out to be of the same face:

```python
class Faces:
    def __init__(self):
        self.parent = {}

    def _end(self, photo):
        while self.parent.get(photo, photo) != photo:
            photo = self.parent[photo]
        return photo

    def link(self, one, other):
        self.parent.setdefault(one, one)
        self.parent.setdefault(other, other)
        self.parent[self._end(one)] = self._end(other)
```

`link` on two ids that are already in the same group points that group's end at itself, which changes nothing — so repeated matches are free. This `_end` walks the chain without shortening it; shortening it is the line the note above is about.
