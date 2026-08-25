"""if / elif / else — three reactor decisions, each a different shape of branch."""
# SOURCE: exercism/python concept/meltdown-mitigation (MIT, adapted)
# READ FIRST:
#   https://docs.python.org/3/tutorial/controlflow.html#more-control-flow-tools  — if / elif /
#       else: the first branch whose test is True wins, and the rest are never even evaluated
#   https://realpython.com/python-conditional-statements/  — chained comparisons (`0 <= x < 10`)
#       and when a ladder of elif beats a pile of separate ifs
#   CONCEPT: conditionals — Python has no case/switch before 3.10; a chain of elif is how you
#       write one, and every test must resolve to True or False.

from _lib import rng

META = {"topic": 209, "title": "conditionals — reactor meltdown control", "minutes": 15,
        "prereqs": [200, 203], "tags": ["exercism", "conditionals", "core"]}


def solve():
    """WHY: You are writing the control software for a nuclear reactor. A
    reactor only produces power while it sits in a narrow band called
    criticality: below it the core gets damaged, above it you get a meltdown.
    The sensors feed you raw numbers — temperature, neutron count, voltage,
    current — and the control room needs three plain answers off them: is the
    core balanced right now, how efficiently is it running, and should the rods
    go in or out. Each answer is a different shape of decision: one yes/no, one
    four-way band, one three-way band. Getting the `<` versus `<=` right is the
    entire job; on this machine an off-by-one boundary is not a cosmetic bug.

    YOU GET: nothing. Every reading arrives as an argument to one of your
    functions. Readings can be whole numbers or decimals.

    YOU RETURN: a dict with these three functions.

      "is_criticality_balanced" — takes `temperature` (kelvin, e.g. 750) and
      `neutrons_emitted` (per second, e.g. 600). Returns True only when all
      three hold: temperature below 800, neutrons above 500, and the two
      multiplied together below 500000. Otherwise False.

      "reactor_efficiency" — takes `voltage`, `current` and
      `theoretical_max_power` (the output that would count as 100%). Generated
      power is voltage times current; efficiency is that as a percentage of the
      theoretical max. Returns the band as a string: 'green' at 80% or more,
      'orange' below 80% but at least 60%, 'red' below 60% but at least 30%,
      'black' below 30%.

      "fail_safe" — takes `temperature`, `neutrons_produced_per_second` and
      `threshold`. Multiply the first two to get the reactor's output. Returns
      'LOW' when that output is under 90% of the threshold (rods must come out),
      'NORMAL' while it is anywhere from 90% to 110% of the threshold, and
      'DANGER' above that (shut down now).

    ─── exact rules ───
    The dict keys are exactly the three strings above. Thresholds and
    theoretical maxima are never zero. Percentages are rarely whole numbers, so
    read every boundary above carefully: "at least" includes the boundary,
    "below" does not.

        is_criticality_balanced(750, 600)     ->  True
        is_criticality_balanced(800, 500)     ->  False  (800 is not below 800)
        reactor_efficiency(10, 799, 10000)    ->  'orange'  (79.9%, just under green)
        fail_safe(10, 901, 10000)             ->  'NORMAL'  (90.1% of threshold)
        fail_safe(10, 1101, 10000)            ->  'DANGER'  (110.1%, over the band)
    """
    raise NotImplementedError


HINTS = [
    ("Three different shapes. The first is one condition made of three parts that "
    "must all hold — no branching needed at all, just the combined test. The other "
    "two are ladders: order the branches from one end of the scale to the other so "
    "that by the time you test a band, everything above it has already been ruled "
    "out and you only need ONE comparison per branch."),
    ("Write the ladders top-down, highest band first, and each `elif` then only "
    "needs the lower edge of its band — the upper edge is already excluded by the "
    "branch above. The last band needs no test at all: `else` is everything left "
    "over, which is also what saves you when a reading is 0. Percentages: compute "
    "the percentage once into a variable before the ladder, so the arithmetic "
    "cannot drift between branches."),
    ("Different data, same shape. Grading a support ticket's response time against "
    "a 60-minute SLA:\n"
    "    used = (minutes_taken / 60) * 100\n"
    "    if used <= 50:\n"
    "        band = 'fast'\n"
    "    elif used <= 100:\n"
    "        band = 'ok'\n"
    "    else:\n"
    "        band = 'breached'\n"
    "    return band\n"
    "One ladder, one comparison per branch, one `else` for the rest. 'ok' covers "
    "50 to 100 inclusive without either branch mentioning 50 twice."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    temperature = round(r.choice([r.uniform(300, 790), r.uniform(500, 1000)]), 2)
    neutrons_emitted = round(r.choice([r.uniform(505, 900), r.uniform(300, 1200)]), 2)

    theoretical_max_power = r.choice([10000, 15000, 40000, 90000])
    voltage = r.randint(5, 25)
    target = r.choice([r.uniform(81, 99.5), r.uniform(61, 79),
                       r.uniform(31, 59), r.uniform(0, 29)])
    current = round(theoretical_max_power * target / 100 / voltage, 3)

    threshold = r.choice([5000, 10000, 250000, 1000000])
    ratio = r.choice([r.uniform(0.1, 0.88), r.uniform(0.92, 1.08), r.uniform(1.13, 3.0)])
    neutrons_produced = round(threshold * ratio / temperature, 3)

    return (temperature, neutrons_emitted, voltage, current, theoretical_max_power,
            threshold, neutrons_produced)


def _reference():
    def is_criticality_balanced(temperature, neutrons_emitted):
        return (temperature < 800 and neutrons_emitted > 500
                and temperature * neutrons_emitted < 500000)

    def reactor_efficiency(voltage, current, theoretical_max_power):
        percentage = (voltage * current / theoretical_max_power) * 100
        if percentage >= 80:
            return "green"
        if percentage >= 60:
            return "orange"
        if percentage >= 30:
            return "red"
        return "black"

    def fail_safe(temperature, neutrons_produced_per_second, threshold):
        percentage = (temperature * neutrons_produced_per_second / threshold) * 100
        if percentage < 90:
            return "LOW"
        if percentage <= 110:
            return "NORMAL"
        return "DANGER"

    return {"is_criticality_balanced": is_criticality_balanced,
            "reactor_efficiency": reactor_efficiency, "fail_safe": fail_safe}


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    for _ in range(6):
        temp, emitted, voltage, current, max_power, threshold, produced = _gen(r)
        assert (got["is_criticality_balanced"](temp, emitted)
                == want["is_criticality_balanced"](temp, emitted))
        assert (got["reactor_efficiency"](voltage, current, max_power)
                == want["reactor_efficiency"](voltage, current, max_power))
        assert (got["fail_safe"](temp, produced, threshold)
                == want["fail_safe"](temp, produced, threshold))

    # canonical cases from exercism's conditionals_test.py
    for temp, emitted, expected in [(750, 650, True), (799, 501, True), (800, 500, False),
                                    (625, 800, False), (499.99, 1000, True)]:
        assert got["is_criticality_balanced"](temp, emitted) == expected
    for current, expected in [(1000, "green"), (800, "green"), (799, "orange"),
                              (600, "orange"), (599, "red"), (300, "red"),
                              (299, "black"), (0, "black")]:
        assert got["reactor_efficiency"](10, current, 10000) == expected
    for produced, expected in [(399, "LOW"), (899, "LOW"), (901, "NORMAL"),
                               (1099, "NORMAL"), (1101, "DANGER"), (1200, "DANGER")]:
        assert got["fail_safe"](10, produced, 10000) == expected
