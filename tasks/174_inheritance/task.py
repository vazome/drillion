def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    services = ["api", "worker", "web", "cron", "db"]
    texts = ["disk full", "conn reset", "slow query", "certificate expiring"]
    return (r.choice(services), r.choice(texts),
            f"{r.choice(['ops', 'sre', 'oncall'])}@{r.choice(['x.io', 'corp.net'])}")


def _reference():
    class Alert:
        def __init__(self, service, text):
            self.service, self.text = service, text

        def prefix(self):
            return f"[{self.service}]"

        def render(self):
            return f"{self.prefix()} {self.text}"

    class PagerAlert(Alert):
        def prefix(self):
            return "PAGE " + super().prefix()

    class EmailAlert(Alert):
        def __init__(self, service, text, to):
            super().__init__(service, text)
            self.to = to

        def render(self):
            return f"{super().render()} -> {self.to}"

    return Alert, PagerAlert, EmailAlert


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    assert len(got) == 3, "return the three classes as (Alert, PagerAlert, EmailAlert)"
    for _ in range(6):
        service, text, to = _gen(r)
        for mine, theirs, args in ((got[0], want[0], (service, text)),
                                   (got[1], want[1], (service, text)),
                                   (got[2], want[2], (service, text, to))):
            assert mine(*args).render() == theirs(*args).render(), f"{theirs.__name__} {args}"
    alert, pager, email = got
    assert issubclass(pager, alert) and issubclass(email, alert), "both must subclass Alert"
    assert "render" not in vars(pager), "PagerAlert must inherit render, not define its own"
    assert vars(email("a", "b", "c")).keys() == {"service", "text", "to"}, "store all three"
