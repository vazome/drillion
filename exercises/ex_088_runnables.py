"""LCEL: `|` glues small steps into one thing you can call."""

from _lib import rng
from langchain_core.runnables import RunnableLambda, RunnableSequence

META = {"topic": 88, "title": "runnables — build a chain with |", "tier": 3,
        "minutes": 15, "prereqs": [], "tags": ["llm", "langchain"]}


def solve():
    """WHY: LangChain is a library for wiring steps together around an AI
    model, and its core idea is that small steps get joined into one
    pipeline with a single operator. Teams use it to build things like "read
    a metric line, decide whether it is slow, write the report line". Each
    step is small and can be swapped on its own, and the finished pipeline
    can handle one item or a whole list with no extra code. Interviewers ask
    for this to see that you understand the joining idea, not just one big
    function.

    YOU GET: nothing — you build the thing from scratch.

    YOU RETURN: the pipeline itself (three joined steps), not a result. The
    test will feed it lines like "svc=api latency=250" and expect "api 250ms
    SLOW" back, and it checks that the chain really is three separate steps.

    ─── exact rules ───
    A "chain" in LangChain is small steps joined by the `|` operator.

    Every step is a Runnable, which just means it has the same handful of
    methods: .invoke(one_input) and .batch(list_of_inputs). Join two with `|`
    and you get another Runnable, so the whole pipeline has those methods too
    and you never wrote a loop.

    Return a chain of THREE RunnableLambda steps that turns one raw metric
    line into one report line.

        "svc=api latency=250"   ->  "api 250ms SLOW"
        "svc=auth latency=90"   ->  "auth 90ms ok"

    The three steps, in order:

      1. parse      "svc=api latency=250" -> {"svc": "api", "latency": 250}
                    a line is always two key=value pairs in that order, and
                    latency is a whole number
      2. transform  add a "slow" key: True when latency is over 200, else False
                    (exactly 200 is not slow)
      3. format     "<svc> <latency>ms SLOW" when slow, "<svc> <latency>ms ok"
                    otherwise

    Wrap each function in RunnableLambda and join them with `|`. Return the
    chain itself, not a result. The test calls .invoke(line) on it, calls
    .batch(lines), and checks it really is three pieces joined with `|` — one
    big RunnableLambda doing all three jobs is the thing this drills against.
    """
    raise NotImplementedError


HINTS = [
    ("A chain is not a special object you configure. It is three ordinary "
    "functions with `|` between them. The reason to bother splitting them up: "
    "once joined, the pipeline has the same interface as each piece, so "
    ".invoke for one item and .batch for a list both come for free, and you "
    "can swap step 2 without touching 1 or 3. One function doing everything "
    "gives up all of that."),
    ("Write the three plain functions first — parse, transform, format — each "
    "taking one argument and returning one value, and check them by hand. "
    "Then wrap each in RunnableLambda(...) and join with |. For parse: "
    "line.split() gives you the two pairs, then split each on '=', and int() "
    "the latency so it compares as a number."),
    ("Different data — a two-step chain that cleans, then labels:\n"
    "    from langchain_core.runnables import RunnableLambda\n"
    "    clean = RunnableLambda(lambda s: s.strip().lower())\n"
    "    label = RunnableLambda(lambda s: f'user said: {s}')\n"
    "    chain = clean | label\n"
    "    print(chain.invoke('  HELLO  '))       # user said: hello\n"
    "    print(chain.batch(['  A ', ' B ']))    # ['user said: a', 'user said: b']\n"
    "Yours is the same shape with three steps, and a dict rather than a "
    "string travelling between them."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

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
