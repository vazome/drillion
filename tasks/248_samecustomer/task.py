def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from itertools import pairwise

from _lib import rng

_IDS = [f"acct-{n:03d}" for n in range(1, 13)]


def _gen(r):
    ids = list(_IDS)
    r.shuffle(ids)
    people, rest = [], ids
    while len(rest) > 1:
        people.append([rest.pop() for _ in range(min(r.randint(2, 4), len(rest)))])
    if rest:
        # every account in the answer has to have been merged at least once
        people[-1].extend(rest)
    merges = []
    for owned in people:
        for i, account in enumerate(owned[1:], start=1):
            merges.append((account, owned[r.randrange(i)]))
        if len(owned) > 2:
            # a merge nobody needed, whose left-hand account was already merged once
            left = r.randrange(1, len(owned))
            merges.append((owned[left], owned[r.randrange(left)]))
    r.shuffle(merges)
    return merges, sorted(sorted(owned) for owned in people)


def _reference():
    class Records:
        def __init__(self):
            self.parent = {}

        def _root(self, account):
            if account not in self.parent:
                return account
            while self.parent[account] != account:
                # path halving: every hop shortens the chain for the next lookup
                self.parent[account] = self.parent[self.parent[account]]
                account = self.parent[account]
            return account

        def link(self, one, other):
            for account in (one, other):
                self.parent.setdefault(account, account)
            self.parent[self._root(one)] = self._root(other)

        def same(self, one, other):
            return self._root(one) == self._root(other)

        def groups(self):
            found = {}
            for account in self.parent:
                found.setdefault(self._root(account), []).append(account)
            return sorted(sorted(owned) for owned in found.values())

    return Records


def test_solve():
    r = rng()
    records = solve()

    for _ in range(8):
        merges, people = _gen(r)
        book = records()
        for one, other in merges:
            book.link(one, other)
        assert book.groups() == people, f"grouping {merges}"
        for owned in people:
            for account in owned:
                assert book.same(owned[0], account) is True, f"{owned[0]} and {account} are one"
        for left, right in pairwise(people):
            assert book.same(left[0], right[0]) is False, f"{left[0]} and {right[0]} are not"

    # two chains merged by their far ends: only following to the root joins them whole
    book = records()
    book.link("acct-001", "acct-002")
    book.link("acct-003", "acct-004")
    book.link("acct-001", "acct-003")
    assert book.same("acct-001", "acct-004") is True, "one merge joins both chains"
    assert book.groups() == [["acct-001", "acct-002", "acct-003", "acct-004"]]

    fresh = records()
    assert fresh.groups() == [], "no accounts merged yet"
    assert fresh.same("acct-009", "acct-009") is True, "an account is itself"
    assert fresh.same("acct-009", "acct-010") is False, "two accounts nobody merged are two people"
    fresh.link("acct-005", "acct-006")
    fresh.link("acct-005", "acct-006")
    assert fresh.groups() == [["acct-005", "acct-006"]], "the same merge twice changes nothing"
