def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import inspect

from _lib import rng

_NAMES = ["Aimee", "Blair", "James", "Paul", "Chelsea", "Logan", "Anna", "Barb", "Charlie",
          "Alex", "Peter", "Zoe", "Jim", "Franklin", "Bradley", "Jeff", "Rae", "Ada", "Nour"]


def _gen(r):
    pool = r.sample(_NAMES, r.randint(4, 9))
    grades = [r.randint(1, 7) for _ in pool]
    enrolments = list(zip(pool, grades))
    for _ in range(r.randint(1, 3)):
        name, grade = r.choice(enrolments)
        spot = r.randrange(len(enrolments) + 1)
        enrolments.insert(spot, (name, r.choice([grade, r.randint(1, 7)])))
    split = r.randrange(1, len(enrolments))
    queries = sorted({r.randint(1, 8) for _ in range(3)})
    return enrolments, split, queries


def _reference():
    class School:
        def __init__(self):
            self._grade_of = {}
            self._outcomes = []

        def add_student(self, name, grade):
            enrolled = name not in self._grade_of
            if enrolled:
                self._grade_of[name] = grade
            self._outcomes.append(enrolled)

        def added(self):
            outcomes, self._outcomes = self._outcomes, []
            return outcomes

        def roster(self):
            return [name for _, name in sorted((grade, name)
                                               for name, grade in self._grade_of.items())]

        def grade(self, grade_number):
            return sorted(name for name, grade in self._grade_of.items()
                          if grade == grade_number)

    return School


def test_solve():
    r = rng()
    School = solve()
    assert inspect.isclass(School), "solve() must return a class"
    Reference = _reference()
    for _ in range(5):
        enrolments, split, queries = _gen(r)
        mine, theirs = School(), Reference()
        for index, (name, grade) in enumerate(enrolments, start=1):
            mine.add_student(name=name, grade=grade)
            theirs.add_student(name=name, grade=grade)
            if index == split:
                assert mine.added() == theirs.added(), \
                    f"added() after the first {split} of {enrolments!r}"
        assert mine.added() == theirs.added(), f"added() for the rest of {enrolments!r}"
        assert mine.added() == [], f"added() must drain: second call after {enrolments!r}"
        assert mine.roster() == theirs.roster(), f"roster() for {enrolments!r}"
        assert mine.roster() == theirs.roster(), f"roster() must be repeatable for {enrolments!r}"
        for number in queries:
            assert mine.grade(number) == theirs.grade(number), \
                f"grade({number}) for {enrolments!r}"
            assert mine.grade(number) == theirs.grade(number), \
                f"grade({number}) must be repeatable for {enrolments!r}"

    # canonical cases (exercism/python practice/grade-school)
    assert School().roster() == []
    assert School().grade(1) == []

    school = School()
    for name, grade in [("Blair", 2), ("James", 2), ("James", 2), ("Paul", 2)]:
        school.add_student(name=name, grade=grade)
    assert school.added() == [True, True, False, True]
    assert school.roster() == ["Blair", "James", "Paul"]
    assert school.grade(2) == ["Blair", "James", "Paul"]

    school = School()
    for name, grade in [("Blair", 2), ("James", 2), ("James", 3), ("Paul", 3)]:
        school.add_student(name=name, grade=grade)
    assert school.added() == [True, True, False, True]
    assert school.grade(2) == ["Blair", "James"]
    assert school.grade(3) == ["Paul"]

    school = School()
    for name, grade in [("Peter", 2), ("Anna", 1), ("Barb", 1), ("Zoe", 2),
                        ("Alex", 2), ("Jim", 3), ("Charlie", 1)]:
        school.add_student(name=name, grade=grade)
    assert school.roster() == ["Anna", "Barb", "Charlie", "Alex", "Peter", "Zoe", "Jim"]

    school = School()
    for name, grade in [("Franklin", 5), ("Bradley", 5), ("Jeff", 1)]:
        school.add_student(name=name, grade=grade)
    assert school.grade(5) == ["Bradley", "Franklin"]
    assert school.grade(1) == ["Jeff"]
