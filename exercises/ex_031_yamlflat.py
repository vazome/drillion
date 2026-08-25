"""Half of DevOps config is YAML. PyYAML is not installed here, so this drills
the concept by hand on the flat subset — in real code it is one yaml.safe_load call."""

from _lib import rng

META = {"topic": 31, "title": "YAML, the concept — flat key: value block by hand",
        "tier": 3, "minutes": 12, "prereqs": [28]}


def solve(text):
    """WHY: Deployment settings live in a small text file: one setting per line
    as "key: value", with comments and blank lines in between. The deploy
    tool needs those settings as real typed values (3 as a number, false as
    a yes/no flag), not as text. The usual library for this format is not
    installed here, so you parse the simple flat form by hand. The trap: a
    value like an image tag nginx:1.25 contains a colon of its own.

    YOU GET: `text` — a multi-line string of settings, like the block shown
    in the rules below. The test creates it and hands it to you; you never
    build it yourself.

    YOU RETURN: a dict mapping each key to its typed value, like
    {"replicas": 3, "debug": False, "name": "api"}.

    ─── exact rules ───
    `text` is a flat YAML-style mapping — the honest subset you can parse
    without a library:

        # deploy config
        replicas: 3
        image: nginx:1.25

        debug: false
        name : api

    Return it as a dict with typed values:

        {"replicas": 3, "image": "nginx:1.25", "debug": False, "name": "api"}

    Rules:
      - skip blank lines and lines whose stripped form starts with "#"
      - split each remaining line at the FIRST colon only; strip both halves
      - convert values: "true" -> True, "false" -> False, all digits -> int,
        anything else stays a string

    Real YAML adds nesting, lists, anchors and sharper typing edges — which
    is exactly why real scripts call yaml.safe_load instead of doing this.
    """
    raise NotImplementedError


HINTS = [
    ("This is the YAML idea without the library: a mapping is lines of key, "
    "colon, value, with comments and blanks to ignore. The trap is that a "
    "value can contain a colon too — an image tag like nginx:1.25 — so "
    "cutting at every colon destroys data. And YAML is typed: 3 and true are "
    "not strings."),
    ("splitlines walks the block. strip plus startswith('#') filters the "
    "noise. partition(':') splits at the first colon only — that is why it "
    "beats split here. For typing: compare the value against 'true' and "
    "'false', then try isdigit for ints, otherwise keep the string."),
    ("Different data, same moves:\n"
    "    line = 'listen: 0.0.0.0:8080'\n"
    "    key, _, value = line.partition(':')\n"
    "    print(key.strip(), '|', value.strip())   # listen | 0.0.0.0:8080\n"
    "    print('42'.isdigit(), 'id42'.isdigit())  # True False\n"
    "In real code this whole exercise is yaml.safe_load(text) — and never "
    "plain yaml.load, which can construct arbitrary Python objects from "
    "untrusted input."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    ints = [("replicas", r.randint(1, 12)), ("port", r.randint(1024, 9999)),
            ("timeout", r.randint(5, 120))]
    bools = [("debug", r.choice(["true", "false"])),
             ("tls", r.choice(["true", "false"]))]
    strs = [("name", r.choice(["api", "worker", "gateway"])),
            ("env", r.choice(["prod", "staging"])),
            ("image", f"nginx:1.{r.randint(18, 27)}"),
            ("listen", f"0.0.0.0:{r.randint(1024, 9999)}")]
    pairs = (r.sample(ints, r.randint(1, 3)) + r.sample(bools, r.randint(1, 2))
             + r.sample(strs, r.randint(2, 4)))
    r.shuffle(pairs)
    lines = [f"# {r.choice(['deploy config', 'generated', 'do not edit'])}"]
    for k, v in pairs:
        if r.random() < 0.2:
            lines.append("")
        if r.random() < 0.15:
            lines.append(f"# {k} below")
        lines.append(f"{k}{r.choice([': ', ': ', ' : ', ':  '])}{v}")
    return "\n".join(lines)


def _reference(text):
    out = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if value == "true":
            out[key] = True
        elif value == "false":
            out[key] = False
        elif value.isdigit():
            out[key] = int(value)
        else:
            out[key] = value
    return out


def test_solve():
    r = rng()
    for _ in range(4):
        text = _gen(r)
        assert solve(text) == _reference(text)
