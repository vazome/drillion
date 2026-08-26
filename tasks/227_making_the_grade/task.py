def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    raw = [round(r.uniform(0, 100), 2) for _ in range(r.randint(0, 10))]
    if r.random() < 0.4:                        # exact halves, where round() surprises
        raw = [n + 0.5 for n in r.sample(range(100), r.randint(1, 6))]
    scores = [r.randrange(0, 101) for _ in range(r.randint(1, 10))]
    return raw, scores, r.randrange(0, 101)


def _reference():
    def round_scores(student_scores):
        rounded = []
        while student_scores:
            rounded.append(round(student_scores.pop()))
        return rounded

    def count_failed_students(student_scores):
        non_passing = 0
        for score in student_scores:
            if score <= 40:
                non_passing += 1
        return non_passing

    def above_threshold(student_scores, threshold):
        above = []
        for score in student_scores:
            if score >= threshold:
                above.append(score)
        return above

    return {"round_scores": round_scores, "count_failed_students": count_failed_students,
            "above_threshold": above_threshold}


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    for _ in range(6):
        raw, scores, threshold = _gen(r)
        assert (sorted(got["round_scores"](list(raw)))
                == sorted(want["round_scores"](list(raw)))), f"round_scores({raw})"
        assert (got["count_failed_students"](list(scores))
                == want["count_failed_students"](list(scores))), f"count_failed_students({scores})"
        assert (got["above_threshold"](list(scores), threshold)
                == want["above_threshold"](list(scores), threshold)), \
            f"above_threshold({scores}, {threshold})"

    # canonical cases from exercism's loops_test.py
    for scores, expected in [([], []), ([0.5], [0]), ([1.5], [2]),
                             ([90.33, 40.5, 55.44, 70.05, 30.55, 25.45, 80.45, 95.3, 38.7, 40.3],
                              [90, 40, 55, 70, 31, 25, 80, 95, 39, 40]),
                             ([50, 36.03, 76.92, 40.7, 43, 78.29, 63.58, 91, 28.6, 88.0],
                              [50, 36, 77, 41, 43, 78, 64, 91, 29, 88])]:
        assert sorted(got["round_scores"](list(scores))) == sorted(expected), \
            f"round_scores({scores})"
    assert all(isinstance(score, int)
               for score in got["round_scores"]([90.33, 40.5, 55.44])), \
        "round_scores must return ints — round(n, 0) gives a float"
    assert got["count_failed_students"]([89, 85, 42, 57, 90, 100, 95, 48, 70, 96]) == 0
    assert got["count_failed_students"]([40, 40, 35, 70, 30, 41, 90]) == 4
    for scores, threshold, expected in [
            ([40, 39, 95, 80, 25, 31, 70, 55, 40, 90], 98, []),
            ([88, 29, 91, 64, 78, 43, 41, 77, 36, 50], 80, [88, 91]),
            ([100, 89], 100, [100]),
            ([88, 29, 91, 64, 78, 43, 41, 77, 36, 50], 78, [88, 91, 78]),
            ([], 80, [])]:
        assert got["above_threshold"](list(scores), threshold) == expected, \
            f"above_threshold({scores}, {threshold})"
