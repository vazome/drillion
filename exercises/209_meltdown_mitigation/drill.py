def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


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
