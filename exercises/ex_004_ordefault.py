"""`x or default` is everywhere in config code — and it eats real zeros."""

from _lib import rng

META = {"topic": 4, "title": "defaults without swallowing 0 and ''", "tier": 3,
        "minutes": 8, "prereqs": [], "tags": ["core"]}


def solve(port, name):
    """WHY: Your deployment script reads settings from a config file. When a
    setting is missing it should fall back to a sensible default. But
    "missing" is not the same as "set to zero" or "set to empty": a port of 0
    means "let the operating system pick a free port", and an empty name is a
    deliberate choice. A script that treats those real values as missing
    quietly overrides what the engineer asked for, and that kind of silent
    override causes confusing outages.

    YOU GET: `port` — either None (not set), 0, or a number like 8080.
    `name` — either None (not set), "" (empty text), or a word like "api".
    The test creates them and hands them to you; you never build them
    yourself.

    YOU RETURN: a pair (port, name) where None has been replaced with the
    default, and every other value, including 0 and "", comes back untouched.

    ─── exact rules ───
    Apply defaults to two settings and return the tuple (port, name).

        port: if it is None, use 8080. But 0 is a REAL value (it means
              "let the OS pick a free port") and must come through untouched.
        name: if it is None, use "worker". But "" is a real value too.

        (None, "")  ->  (8080, "")
        (0, None)   ->  (0, "worker")

    The tempting one-liner `port or 8080` fails this test — the data
    includes 0 and "" on purpose. One ternary per value does it.
    """
    raise NotImplementedError


HINTS = [
    ("`or` returns the first truthy operand. 0 and '' are falsy, so "
    "`port or 8080` throws a legitimate 0 away. The question you actually "
    "want to ask is 'is it None', not 'is it truthy'."),
    ("A conditional expression reads value-if-kept, then the condition, then "
    "the fallback: keep the original when it is not None, otherwise the "
    "default. Write one per setting and return both in a tuple."),
    ("Different data, same trap:\n"
    "    retries = 0                # a real setting: 'never retry'\n"
    "    wrong = retries or 3\n"
    "    right = retries if retries is not None else 3\n"
    "    print(wrong, right)        # 3 0\n"
    "`or` is only safe when falsy values genuinely mean 'unset'."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    ports = [None, 0, r.randint(1024, 65535)]
    names = [None, "", r.choice(["api", "db", "cache", "cron", "sync"])]
    cases = [(p, n) for p in ports for n in names]
    r.shuffle(cases)
    return cases


def _reference(port, name):
    port = port if port is not None else 8080
    name = name if name is not None else "worker"
    return (port, name)


def test_solve():
    r = rng()
    for _ in range(4):
        for port, name in _gen(r):
            assert solve(port, name) == _reference(port, name)
