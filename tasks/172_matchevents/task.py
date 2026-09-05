def solve(events: list[dict]):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    services = ["api", "worker", "web", "cron"]
    texts = ["disk full", "conn reset", "slow query", "certificate expiring"]
    events = []
    for i in range(r.randint(4, 9)):
        kind = r.choice(["deploy", "deploy", "scale", "alert", "alert", "note"])
        ev = {"type": kind, "ts": f"10:{i:02d}"}
        if kind == "deploy":
            ev["service"] = r.choice(services)
            if r.random() < 0.6:
                ev["version"] = f"{r.randint(1, 3)}.{r.randint(0, 9)}.{r.randint(0, 9)}"
        elif kind == "scale":
            ev["service"] = r.choice(services)
            ev["replicas"] = r.choice([0, 1, 2, 5])
        elif kind == "alert":
            ev["level"] = r.choice(["critical", "warning", "info"])
            ev["text"] = r.choice(texts)
        else:
            ev["text"] = r.choice(texts)
        events.append(ev)
    return events


def _reference(events):
    lines = []
    for event in events:
        match event:
            case {"type": "deploy", "service": s, "version": v}:
                lines.append(f"deploy {s} to {v}")
            case {"type": "deploy", "service": s}:
                lines.append(f"deploy {s} to latest")
            case {"type": "scale", "service": s, "replicas": 0}:
                lines.append(f"stop {s}")
            case {"type": "scale", "service": s, "replicas": n}:
                lines.append(f"scale {s} to {n} replicas")
            case {"type": "alert", "level": "critical", "text": t}:
                lines.append(f"PAGE: {t}")
            case {"type": "alert", "text": t}:
                lines.append(f"log: {t}")
            case _:
                lines.append("ignored")
    return lines


def test_solve():
    r = rng()
    cases = [[{"type": "scale", "service": "api", "replicas": 0, "ts": "10:00"},
              {"type": "note", "text": "hi", "ts": "10:01"}], []]
    for _ in range(6):
        cases.append(_gen(r))
    for events in cases:
        assert solve(events) == _reference(events), f"events={events}"
