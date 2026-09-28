"""What one sitting of 368 asks for, and what counts as having answered it.

The schema accepts a metric with an interval and no count, which in a step never finishes,
and any step mix; both are refused here. The query is compared as text, since it is the
thing Prometheus runs."""

APPS = ["checkout", "search", "pricing", "gateway"]
TAGS = ["4.2.0", "2.9.1", "7.0.3"]
ADDRESSES = [
    "http://prometheus.monitoring.svc:9090",
    "http://prometheus-server.observability.svc:80",
]
QUERY = (
    'sum(rate(http_requests_total{service="{{args.service-name}}",code!~"5.."}[5m])) / '
    'sum(rate(http_requests_total{service="{{args.service-name}}"}[5m]))'
)


def brief(r):
    name = r.choice(APPS)
    threshold = r.choice(["0.95", "0.99"])
    return {
        "name": name,
        "image": f"ghcr.io/acme/{name}:{r.choice(TAGS)}",
        "template": f"{name}-success-rate",
        "service": name,
        "limit": r.choice([2, 3]),
        "threshold": threshold,
        "condition": f"result[0] >= {threshold}",
        "address": r.choice(ADDRESSES),
        "query": QUERY,
    }


def _template(doc, b):
    assert doc.get("kind") == "AnalysisTemplate", (
        f"the first document is a {doc.get('kind')}, and it should be the AnalysisTemplate"
    )
    name = (doc.get("metadata") or {}).get("name")
    assert name == b["template"], (
        f"the AnalysisTemplate is named {name!r}, and it should be {b['template']!r}"
    )
    spec = doc.get("spec") or {}
    assert spec.get("args") == [{"name": "service-name"}], (
        f"spec.args is {spec.get('args')!r}, and it should declare exactly one argument, "
        "service-name, with no value: the Rollout's step passes it"
    )
    metrics = spec.get("metrics") or []
    assert len(metrics) == 1, f"there are {len(metrics)} metrics, and the task asks for one"
    m = metrics[0]
    assert m.get("name") == "success-rate", (
        f"the metric is named {m.get('name')!r}, and it should be 'success-rate'"
    )
    assert m.get("interval") == "1m", (
        f"the metric's interval is {m.get('interval')!r}, and it should be '1m'"
    )
    assert m.get("count") == 5, (
        f"the metric's count is {m.get('count')!r}, and it should be 5: with an interval "
        "and no count, a metric measures until something stops it, and in a step nothing "
        "does"
    )
    assert m.get("failureLimit") == b["limit"], (
        f"failureLimit is {m.get('failureLimit')!r}, and it should be {b['limit']}"
    )
    assert m.get("successCondition") == b["condition"], (
        f"successCondition is {m.get('successCondition')!r}, and it should be "
        f"{b['condition']!r}"
    )
    provider = m.get("provider") or {}
    assert set(provider) == {"prometheus"}, (
        f"the provider is {sorted(provider)}, and it should be prometheus alone"
    )
    prom = provider["prometheus"] or {}
    assert prom.get("address") == b["address"], (
        f"the Prometheus address is {prom.get('address')!r}, and it should be "
        f"{b['address']!r}"
    )
    query = " ".join(str(prom.get("query", "")).split())
    assert query == b["query"], (
        f"the query is {prom.get('query')!r}, and it should be exactly {b['query']!r}"
    )


def _steps(steps):
    for i, step in enumerate(steps, 1):
        assert isinstance(step, dict) and len(step) == 1, (
            f"step {i} is {step!r}, and a step does exactly one thing"
        )
    return steps


def check_many(docs, b):
    assert len(docs) == 2, (
        f"the file holds {len(docs)} documents, and the task asks for two: the "
        "AnalysisTemplate, then the Rollout"
    )
    template, rollout = docs
    _template(template, b)

    assert rollout.get("kind") == "Rollout", (
        f"the second document is a {rollout.get('kind')}, and it should be the Rollout"
    )
    name = (rollout.get("metadata") or {}).get("name")
    assert name == b["name"], f"the Rollout is named {name!r}, and it should be {b['name']!r}"
    spec = rollout.get("spec") or {}
    assert spec.get("replicas") == 10, (
        f"the Rollout's replicas is {spec.get('replicas')!r}, and it should be 10"
    )
    selector = (spec.get("selector") or {}).get("matchLabels")
    labels = ((spec.get("template") or {}).get("metadata") or {}).get("labels") or {}
    assert selector == {"app": b["name"]} and labels.get("app") == b["name"], (
        f"the Rollout selects {selector} and labels its pods {labels}, and both should be "
        f"app: {b['name']!r}"
    )
    containers = ((spec.get("template") or {}).get("spec") or {}).get("containers") or []
    assert len(containers) == 1, (
        f"the pod template has {len(containers)} containers, and it should have one"
    )
    c = containers[0]
    assert c.get("name") == b["name"] and c.get("image") == b["image"], (
        f"the container is {c.get('name')!r} running {c.get('image')!r}, and it should be "
        f"{b['name']!r} running {b['image']!r}"
    )
    canary = (spec.get("strategy") or {}).get("canary") or {}
    steps = _steps(canary.get("steps") or [])
    want = [
        {"setWeight": 20},
        {
            "analysis": {
                "templates": [{"templateName": b["template"]}],
                "args": [{"name": "service-name", "value": b["service"]}],
            }
        },
        {"setWeight": 50},
        {"pause": {"duration": "10m"}},
    ]
    assert steps == want, f"the steps are {steps}, and they should be {want}"
