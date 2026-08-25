def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng
from langchain_core.runnables import RunnableLambda, RunnableSequence


def _gen(r):
    names = ["api", "auth", "cache", "queue", "web", "db", "search", "gw"]
    picked = r.sample(names, r.randint(4, 6))
    # 200 and 201 are always in the batch: the boundary is what gets written
    # as >= by mistake, so every seed has to test it
    latencies = [200, 201] + [r.choice([r.randint(1, 199), r.randint(201, 900)])
                              for _ in picked[2:]]
    r.shuffle(latencies)
    return [f"svc={name} latency={latency}"
            for name, latency in zip(picked, latencies)]


def _reference():
    def parse(line):
        fields = dict(pair.split("=") for pair in line.split())
        return {"svc": fields["svc"], "latency": int(fields["latency"])}

    def transform(record):
        return {**record, "slow": record["latency"] > 200}

    def format_(record):
        state = "SLOW" if record["slow"] else "ok"
        return f"{record['svc']} {record['latency']}ms {state}"

    return RunnableLambda(parse) | RunnableLambda(transform) | RunnableLambda(format_)


def test_solve():
    r = rng()
    chain = solve()
    reference = _reference()

    assert isinstance(chain, RunnableSequence), (
        "join the steps with | — that is what makes a chain (a RunnableSequence)"
    )
    assert len(chain.steps) >= 3, (
        f"chain has {len(chain.steps)} step(s); it must be three separate "
        f"RunnableLambdas joined with |"
    )

    for _ in range(4):
        lines = _gen(r)
        for line in lines:
            assert chain.invoke(line) == reference.invoke(line), f"wrong for {line!r}"
        assert chain.batch(lines) == reference.batch(lines), (
            ".batch must give the same answers, in input order"
        )
