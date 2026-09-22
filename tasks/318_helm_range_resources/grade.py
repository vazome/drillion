"""What one sitting of 318 asks for, and what counts as having answered it.

Two renders with lists of different lengths, so a template that writes out the default
two Services by hand, or loops a fixed number of times, fails the other one."""

RELEASES = ["checkout", "billing", "inventory", "search", "ledger"]
LISTENERS = [("http", 8080), ("admin", 9090), ("metrics", 9100), ("grpc", 50051)]


def brief(r):
    """A brief holds scalars only, so each list travels as `name:port,name:port`."""
    one, two = r.sample(RELEASES, 2)

    def listed(count):
        return ",".join(f"{n}:{p}" for n, p in r.sample(LISTENERS, count))

    return {
        "release": one,
        "listeners": listed(r.choice([1, 3])),
        "other_release": two,
        "other_listeners": listed(r.choice([2, 4])),
    }


def _unpacked(text):
    return [
        {"name": name, "port": int(port)}
        for name, port in (item.split(":") for item in text.split(","))
    ]


def renders(b):
    return [
        {
            "release": b[f"{p}release"],
            "values": {"listeners": _unpacked(b[f"{p}listeners"])},
        }
        for p in ("", "other_")
    ]


def check(docs, b, render):
    release, listeners = render["release"], render["values"]["listeners"]
    kinds = [d.get("kind") for d in docs]
    assert kinds == ["Service"] * len(listeners), (
        f"these values list {len(listeners)} listeners, and the template rendered "
        f"{kinds}: one Service per listener"
    )
    for doc, listener in zip(docs, listeners):
        want = f"{release}-{listener['name']}"
        name = doc["metadata"]["name"]
        assert name == want, (
            f"a Service rendered as {name!r}, and for the listener {listener['name']!r} "
            f"it should be {want!r}, in the order the list gives"
        )
        selector = doc["spec"].get("selector") or {}
        assert selector == {"app": release}, (
            f"the Service {name!r} selects {selector}, and it should select "
            f"{{'app': {release!r}}}, the release's pods"
        )
        ports = [
            (p.get("port"), p.get("targetPort")) for p in doc["spec"].get("ports") or []
        ]
        want = [(listener["port"], listener["port"])]
        assert ports == want, (
            f"the Service {name!r} has ports {ports} as (port, targetPort), and it should "
            f"have {want}"
        )
