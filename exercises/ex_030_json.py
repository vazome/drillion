"""APIs answer in JSON; the nested-missing-key crash is the classic screen-share failure."""

from _lib import rng

META = {"topic": 30, "title": "json — loads, safe nested gets, dumps", "tier": 3,
        "minutes": 15, "prereqs": [18], "tags": ["files-text"]}


def solve(text):
    """WHY: A cluster API answers with the state of every node as JSON text.
    Not every node reports CPU load, and not every cluster carries a region
    tag. The platform team's dashboard script keeps crashing because it
    assumes those fields are always present. You are asked to write a
    version that produces a short summary (region plus CPU per node) and
    never crashes when a field is simply absent.

    YOU GET: `text` — a string of JSON, the raw text an HTTP API answered
    with, shaped like the example in the rules below. The test creates it
    and hands it to you; you never build it yourself.

    YOU RETURN: a string — the summary written back out as JSON text with
    two-space indent and sorted keys, exactly as shown in the rules below.

    ─── exact rules ───
    `text` is the JSON string a cluster API returned. Its shape,
    pretty-printed:

        {"cluster": {
            "name": "prod-2",
            "nodes": [
                {"name": "node-7-0",
                 "status": {"phase": "Ready",
                            "load": {"cpu": 0.42, "mem": 0.61}}},
                {"name": "node-3-1",
                 "status": {"phase": "NotReady"}}],
            "meta": {"region": "eu-central-1"}}}

    Guaranteed present: "cluster", "nodes", and each node's "name",
    "status" and "status" -> "phase". Optional: "meta" (and "region"
    inside it), "load" (and "cpu" inside it). Indexing an optional key
    that is absent must not crash your code.

    Return the STRING json.dumps(summary, indent=2, sort_keys=True) where

        summary = {"region": "eu-central-1",            # or "unknown" if absent
                   "cpu_by_node": {"node-7-0": 0.42,
                                   "node-3-1": None}}   # None when cpu missing

    For the example above that string prints as:

        {
          "cpu_by_node": {
            "node-3-1": null,
            "node-7-0": 0.42
          },
          "region": "eu-central-1"
        }
    """
    raise NotImplementedError


HINTS = [
    ("json.loads hands you plain dicts and lists — after that it is not a JSON "
    "problem, it is a dict problem. The crash comes from square-bracketing a "
    "key that is not there. Only the hops the schema marks optional need a "
    "lookup with a default; the guaranteed ones can stay as plain indexing."),
    ("data['cluster']['nodes'] is safe — the spec guarantees those. For the "
    "optional hops, chain dict.get with an empty-dict default: get('meta', {}) "
    "then get('region', 'unknown'). Note that .get with no default returns "
    "None, which is exactly what the cpu column wants. Finish with json.dumps "
    "plus its indent and sort_keys keyword arguments."),
    ("Different data, same pattern:\n"
    "    import json\n"
    "    cfg = {'svc': {'limits': {'mem': '1Gi'}}}\n"
    "    cpu = cfg['svc'].get('limits', {}).get('cpu', 'unset')\n"
    "    print(cpu)                                        # unset\n"
    "    print(json.dumps({'b': 1, 'a': 2}, sort_keys=True))  # {\"a\": 2, \"b\": 1}\n"
    "Chained .get with {} defaults never raises; the dumps arguments control "
    "the exact text you return."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    import json
    nodes = []
    for i in range(r.randint(2, 5)):
        node = {"name": f"node-{r.randint(1, 99)}-{i}",
                "status": {"phase": r.choice(["Ready", "NotReady", "Cordoned"])}}
        roll = r.random()
        if roll < 0.55:
            node["status"]["load"] = {"cpu": round(r.uniform(0.02, 0.98), 2),
                                      "mem": round(r.uniform(0.1, 0.9), 2)}
        elif roll < 0.75:
            node["status"]["load"] = {"mem": round(r.uniform(0.1, 0.9), 2)}
        nodes.append(node)
    cluster = {"name": f"prod-{r.randint(1, 9)}", "nodes": nodes}
    if r.random() < 0.6:
        meta = {}
        if r.random() < 0.75:
            meta["region"] = r.choice(["eu-central-1", "us-east-1",
                                       "ap-southeast-2"])
        cluster["meta"] = meta
    return json.dumps({"cluster": cluster})


def _reference(text):
    import json
    data = json.loads(text)
    cluster = data["cluster"]
    region = cluster.get("meta", {}).get("region", "unknown")
    cpu = {n["name"]: n["status"].get("load", {}).get("cpu")
           for n in cluster["nodes"]}
    return json.dumps({"region": region, "cpu_by_node": cpu},
                      indent=2, sort_keys=True)


def test_solve():
    r = rng()
    for _ in range(4):
        text = _gen(r)
        assert solve(text) == _reference(text)
