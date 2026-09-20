"""What one sitting of 271 asks for, and what counts as having answered it.

The schema has already run by the time `check` does, so the shape is sound and only the
requirements are left. Every message here is what the learner reads, so each one names the
field and what it should have held."""

NAMES = ["api-key", "db-credentials", "provider-token"]
VALUES = [
    "s3cr3t-tunnel-7f3a",
    "k9-watchtower-22",
    "paper-clip-staple-88",
    "harbor-light-401",
]


def brief(r):
    return {
        "name": r.choice(NAMES),
        "value": r.choice(VALUES),
    }


def check(doc, b):
    assert doc.get("kind") == "Secret", (
        f"this is a {doc.get('kind')}, and the task asks for a Secret"
    )
    name = doc.get("metadata", {}).get("name")
    assert name == b["name"], (
        f"metadata.name is {name!r}, and it should be {b['name']!r}"
    )

    assert doc.get("type") == "Opaque", (
        f"type is {doc.get('type')!r}, and a Secret of ordinary keys and passwords is "
        "type Opaque"
    )
    assert "data" not in doc or not doc.get("data"), (
        "the Secret carries a data field, and this task asks for stringData: write the "
        "plain text and let the API do the encoding"
    )
    plain = doc.get("stringData") or {}
    assert plain.get("API_KEY") == b["value"], (
        f"stringData.API_KEY is {plain.get('API_KEY')!r}, and it should be the plain "
        f"text {b['value']!r}, no encoding of your own"
    )
