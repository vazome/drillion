"""What one sitting of 288 asks for, and what counts as having answered it.

The Secret is checked by decoding it: whatever the template did, the bytes that come back
out of `data` have to be the values. Both renders use values that need quoting once
encoded, so a template that encodes without quoting, or quotes without encoding, fails."""

import base64

RELEASES = ["orders", "billing", "reports", "search"]
USERS = ["app", "orders_rw", "reporter", "svc-search"]


def brief(r):
    one, two = r.sample(RELEASES, 2)
    first, second = r.sample(USERS, 2)
    return {
        "release": one,
        "username": first,
        "password": "".join(r.choice("abcdefghjkmnpqrstuvwxyz23456789") for _ in range(16)),
        "other_release": two,
        "other_username": second,
        "other_password": "".join(r.choice("ABCDEFGHJKMNPQRSTUVWXYZ") for _ in range(12)),
    }


def renders(b):
    return [
        {
            "release": b["release"],
            "values": {"auth": {"username": b["username"], "password": b["password"]}},
        },
        {
            "release": b["other_release"],
            "values": {
                "auth": {"username": b["other_username"], "password": b["other_password"]}
            },
        },
    ]


def check(docs, b, render):
    kinds = [d.get("kind") for d in docs]
    assert kinds == ["Secret"], f"the template should render one Secret, not {kinds}"
    doc, auth = docs[0], render["values"]["auth"]
    want = f"{render['release']}-auth"
    assert doc["metadata"]["name"] == want, (
        f"metadata.name rendered as {doc['metadata']['name']!r}, and it should be {want!r}"
    )
    assert doc.get("type") == "Opaque", f"the type is {doc.get('type')!r}, not Opaque"
    assert "stringData" not in doc, (
        "this task asks for data, base64 encoded by the template, not stringData"
    )
    data = doc.get("data") or {}
    assert set(data) == {"username", "password"}, (
        f"data holds {sorted(data)}, and it should hold username and password"
    )
    for key in ("username", "password"):
        try:
            got = base64.b64decode(str(data[key]), validate=True).decode()
        except ValueError:
            raise AssertionError(
                f"data.{key} is {data[key]!r}, which is not base64: the value has to pass "
                "through b64enc on its way in"
            ) from None
        assert got == auth[key], (
            f"data.{key} decodes to {got!r}, and these values set it to {auth[key]!r}"
        )
