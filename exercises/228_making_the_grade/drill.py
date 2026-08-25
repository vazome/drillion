def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

# highest scores for which "step four times from 41" and Exercism's
# range(41, highest, increment) agree — the increment never rounds down far enough
# to squeeze a fifth threshold in
_HIGHEST = (75, 76, 77, 78, 79, 80, 81, 83, 84, 85, 86, 87, 88, 89, 91, 92, 93, 94,
            95, 96, 97, 99, 100)

_STUDENTS = ["Joci", "Sara", "Kora", "Jan", "John", "Bern", "Fred", "Rui", "Betty",
             "Yoshi", "Rose", "Vlad", "Alex", "Lilliana", "Raiana", "Paul", "Ernest"]


def _gen(r):
    names = r.sample(_STUDENTS, r.randint(1, 8))
    scores = sorted((r.randrange(40, 101) for _ in names), reverse=True)
    info = [[name, 100 if r.random() < 0.25 else r.randrange(20, 100)]
            for name in r.sample(_STUDENTS, r.randint(0, 8))]
    return r.choice(_HIGHEST), scores, names, info


def _reference():
    def letter_grades(highest):
        increment = round((highest - 40) / 4)
        return [41 + increment * band for band in range(4)]

    def student_ranking(student_scores, student_names):
        results = []
        for index, name in enumerate(student_names):
            results.append(f"{index + 1}. {name}: {student_scores[index]}")
        return results

    def perfect_score(student_info):
        result = []
        for student in student_info:
            if student[1] == 100:
                result = student
                break
        return result

    return {"letter_grades": letter_grades, "student_ranking": student_ranking,
            "perfect_score": perfect_score}


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    for _ in range(6):
        highest, scores, names, info = _gen(r)
        assert (got["letter_grades"](highest)
                == want["letter_grades"](highest)), f"letter_grades({highest})"
        assert (got["student_ranking"](list(scores), list(names))
                == want["student_ranking"](list(scores), list(names))), \
            f"student_ranking({scores}, {names})"
        assert (got["perfect_score"]([list(pair) for pair in info])
                == want["perfect_score"]([list(pair) for pair in info])), \
            f"perfect_score({info})"

    # canonical cases from exercism's loops_test.py
    for highest, expected in [(100, [41, 56, 71, 86]), (97, [41, 55, 69, 83]),
                              (85, [41, 52, 63, 74]), (92, [41, 54, 67, 80]),
                              (81, [41, 51, 61, 71])]:
        assert got["letter_grades"](highest) == expected, f"letter_grades({highest})"
    assert got["student_ranking"]([82], ["Betty"]) == ["1. Betty: 82"]
    assert (got["student_ranking"]([88, 73], ["Paul", "Ernest"])
            == ["1. Paul: 88", "2. Ernest: 73"])
    assert (got["student_ranking"]([100, 98, 92, 86, 70, 68, 67, 60],
                                   ["Rui", "Betty", "Joci", "Yoshi", "Kora", "Bern",
                                    "Jan", "Rose"])
            == ["1. Rui: 100", "2. Betty: 98", "3. Joci: 92", "4. Yoshi: 86",
                "5. Kora: 70", "6. Bern: 68", "7. Jan: 67", "8. Rose: 60"])
    for info, expected in [
            ([["Joci", 100], ["Vlad", 100], ["Raiana", 100]], ["Joci", 100]),
            ([["Jill", 30], ["Paul", 73]], []),
            ([], []),
            ([["Yoshi", 52], ["Jan", 86], ["Raiana", 100], ["Betty", 60], ["Joci", 100]],
             ["Raiana", 100])]:
        assert got["perfect_score"]([list(pair) for pair in info]) == expected, \
            f"perfect_score({info})"
