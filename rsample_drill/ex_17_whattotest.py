"""Coverage percentage is easy to game; knowing which lines deserve a test is the real skill."""
# READ FIRST:
#   https://martinfowler.com/bliki/TestPyramid.html  — many small unit tests, few big end-to-end ones
#   https://realpython.com/pytest-python-testing/  — the pytest tutorial; 'Fixtures' and 'Marks' sections
# (copy of exercises/ex_061_whattotest.py — same file, just placed in the take-home order)

from _lib import rng

META = {"topic": 17, "title": "what to actually test in an ops script",
        "tier": 3, "minutes": 8, "prereqs": []}


def solve(units):
    """WHY: Your team has a big ops script and a rule that "everything must
    have tests". Writing a test for every single function wastes days and
    produces brittle tests that break on every rename. The tech lead wants a
    consistent triage: functions that make decisions get tests; thin
    wrappers around a library call, plain config constants, and
    straight-line glue code are skipped, unless the glue starts branching,
    which makes it decision-making again. You encode that rule so the team
    can apply it to a list of functions.

    YOU GET: `units` — a list of dicts, one per function in the script, like
    {"name": "parse_uptime", "kind": "logic", "branches": 3}, where kind is
    "logic", "wrapper", "config" or "glue" and branches is how many if/else
    paths it has. Names are unique. The test creates it and hands it to
    you.

    YOU RETURN: a dict mapping each name to the string "test" or "skip".

    ─── exact rules ───
    Decide which pieces of a script are worth writing a test for.

    Each unit describes one function in the script:

        {"name": "parse_uptime", "kind": "logic", "branches": 3}

    kind is one of "logic", "wrapper", "config" or "glue", and branches
    is how many if/else paths it contains. Return a dict mapping each
    name to "test" or "skip". Names are unique.

    The rule:
      - "logic"   -> "test", always
      - "wrapper" -> "skip"
      - "config"  -> "skip"
      - "glue"    -> "test" if branches >= 2, else "skip"

        [{"name": "parse_uptime", "kind": "logic", "branches": 3},
         {"name": "get_bucket", "kind": "wrapper", "branches": 0},
         {"name": "route_alert", "kind": "glue", "branches": 2},
         {"name": "run_all", "kind": "glue", "branches": 0}]
        ->  {"parse_uptime": "test", "get_bucket": "skip",
             "route_alert": "test", "run_all": "skip"}

    Why the rule looks like that:

    logic is code that decides something you wrote the rules for —
    parsing a line, comparing against a threshold, choosing whether to
    retry. It has edge cases, and edge cases are what tests are for.

    wrapper is a function whose body is one library call plus a return.
    A test there asserts that boto3 still works, which is not your
    problem, and it breaks every time you touch the signature. It also
    needs a mock to run at all, so the test is mostly mock setup.

    config is constants and defaults. The test would restate the value,
    so it passes right up until someone changes both together.

    glue wires calls into an order. With no branches there is nothing
    to get wrong that an end-to-end run would not catch louder. Once it
    is picking between paths, that choice is your logic again, and it
    is worth pinning down.
    """
    raise NotImplementedError


HINTS = [
    ("The question sitting behind the rule: if this broke, would a test have "
    "caught it, and would that test break for any other reason. A function "
    "that only forwards to a library fails on both counts — it breaks when "
    "you rename an argument, not when the behaviour is wrong. Code that "
    "decides something passes on both."),
    ("One dict, built in a loop over units. Two of the four kinds are always "
    "skip and one is always test, so only glue needs to look at branches. "
    "Order the if/elif so the glue case comes last and the rest fall through "
    "to a single skip. Key the dict by unit['name']."),
    ("Different data — same shape of decision, routing health checks:\n"
    "    checks = [{'n': 'disk', 'sev': 'page'},\n"
    "              {'n': 'cache_hit', 'sev': 'info'}]\n"
    "    action = {}\n"
    "    for c in checks:\n"
    "        if c['sev'] == 'page':\n"
    "            action[c['n']] = 'wake someone'\n"
    "        else:\n"
    "            action[c['n']] = 'dashboard'\n"
    "    print(action)    # {'disk': 'wake someone', 'cache_hit': 'dashboard'}\n"
    "Yours has four kinds feeding two labels, and one of them needs a second "
    "look at a number before it picks."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

_STEMS = {
    "logic": ["parse_uptime", "pick_replicas", "threshold_breached", "normalise_tag"],
    "wrapper": ["get_object", "put_metric", "list_pods", "read_secret"],
    "config": ["DEFAULTS", "REGIONS", "TIMEOUT_SECONDS", "LOG_FORMAT"],
    "glue": ["run_rollout", "sync_all", "handle_event", "main"],
}


def _gen(r):
    units = []
    for i in range(r.randint(4, 8)):
        kind = r.choice(["logic", "wrapper", "config", "glue", "glue"])
        branches = 0 if kind == "config" else r.randint(0, 4)
        units.append({"name": f"{r.choice(_STEMS[kind])}_{i}",   # _i keeps names unique
                      "kind": kind, "branches": branches})
    return units


def _reference(units):
    decisions = {}
    for u in units:
        if u["kind"] == "logic":
            decisions[u["name"]] = "test"
        elif u["kind"] == "glue":
            decisions[u["name"]] = "test" if u["branches"] >= 2 else "skip"
        else:
            decisions[u["name"]] = "skip"
    return decisions


def test_solve():
    r = rng()
    for _ in range(4):
        units = _gen(r)
        assert solve(units) == _reference(units)
