def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import pytest
from _lib import rng


def _gen(r):
    return (
        r.choice(["disk full", "conn reset", "slow query", "cert expiring", "queue backed up"]),
        r.choice(["api", "worker", "web", "cron"]),
    )


def _reference():
    import abc

    class Backend(abc.ABC):
        @abc.abstractmethod
        def deliver(self, text):
            """Send one line, and return what was sent."""

        @property
        @abc.abstractmethod
        def name(self):
            """What this backend is called in a log line."""

        def notify(self, service, text):
            return self.deliver(f"[{service}] {text}")

        def describe(self):
            return f"{self.name} backend"

    class Pager(Backend):
        name = "pager"

        def deliver(self, text):
            return f"PAGE {text}"

    return Backend, Pager


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    assert len(got) == 2, "return the two classes as (Backend, Pager)"
    backend, pager = got
    _, want_pager = want

    for _ in range(6):
        text, service = _gen(r)
        assert pager().notify(service, text) == want_pager().notify(service, text)
    assert pager().describe() == want_pager().describe()

    import abc

    assert isinstance(backend, abc.ABCMeta), "Backend must be an abc.ABC"
    assert issubclass(pager, backend), "Pager must subclass Backend"

    with pytest.raises(TypeError):
        backend()

    # a backend that forgot half the contract must fail at construction, not at 3am
    class HalfBuilt(backend):
        def deliver(self, text):
            return text

    with pytest.raises(TypeError):
        HalfBuilt()

    class Complete(backend):
        name = "email"

        def deliver(self, text):
            return f"mail: {text}"

    assert Complete().notify("api", "disk full") == "mail: [api] disk full"
    assert Complete().describe() == "email backend"
    # `notify` and `describe` are the base's, and a subclass gets them for free
    assert "notify" not in vars(pager) and "describe" not in vars(pager)
