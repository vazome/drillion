"""What one sitting of 285 asks for, and what counts as having answered it.

The two renders carry different keys, not only different values, so only a template that
loops over whatever `config` holds renders both. Numbers and booleans are among the values
on purpose: a ConfigMap only holds strings, and kubeconform refuses anything else."""

RELEASES = ["shop", "blog", "forum", "status"]
LEVELS = ["debug", "info", "warn", "error"]


def brief(r):
    one, two = r.sample(RELEASES, 2)
    return {
        "release": one,
        "level": r.choice(LEVELS),
        "connections": r.randint(10, 500),
        "search": r.choice([True, False]),
        "other_release": two,
        "timeout": r.randint(5, 60),
        "region": r.choice(["eu-west-1", "us-east-2", "ap-south-1"]),
    }


def renders(b):
    return [
        {
            "release": b["release"],
            "values": {
                "config": {
                    "LOG_LEVEL": b["level"],
                    "MAX_CONNECTIONS": b["connections"],
                    "FEATURE_SEARCH": b["search"],
                }
            },
        },
        {
            "release": b["other_release"],
            "values": {"config": {"TIMEOUT_SECONDS": b["timeout"], "REGION": b["region"]}},
        },
    ]


def _text(value):
    """What a value reads as once quoted: YAML's spelling for a boolean, not Python's."""
    return str(value).lower() if isinstance(value, bool) else str(value)


def check(docs, b, render):
    kinds = [d.get("kind") for d in docs]
    assert kinds == ["ConfigMap"], f"the template should render one ConfigMap, not {kinds}"
    doc = docs[0]
    want = f"{render['release']}-config"
    assert doc["metadata"]["name"] == want, (
        f"metadata.name rendered as {doc['metadata']['name']!r}, and it should be {want!r}"
    )
    data = doc.get("data") or {}
    config = render["values"]["config"]
    assert set(data) == set(config), (
        f"the ConfigMap holds the keys {sorted(data)}, and these values hold "
        f"{sorted(config)}: every entry of .Values.config becomes one key, and no other"
    )
    for key, value in config.items():
        assert data[key] == _text(value), (
            f"data.{key} rendered as {data[key]!r}, and it should be {_text(value)!r}"
        )
