"""SQL grading: every rule a SQL task shows is one its grader enforces, through the real
pipeline (PGlite in the sandbox, as a submission is), plus the comparison on its own."""

from decimal import Decimal

from drillion import grading


def r(fields, *rows):
    return {"fields": list(fields), "rows": [list(x) for x in rows], "count": len(rows)}


def test_numbers_compare_as_decimals_and_nothing_else_does():
    assert grading.sql_value("2.50") == grading.sql_value("2.5") == Decimal("2.5")
    assert grading.sql_value(" 1") == " 1" and grading.sql_value("1_000") == "1_000"
    assert grading.sql_value("NaN") == "NaN" and grading.sql_value(None) is None


def test_the_first_difference_is_named():
    key = r(["a", "b"], ["1", "x"], ["2", "y"])
    assert grading.differ(key, r(["a", "b"], ["2", "y"], ["1.0", "x"]), False) is None
    assert grading.differ(key, r(["a"], ["1"], ["2"]), False)[0] == "columns"
    assert grading.differ(key, r(["a", "b"], ["1", "x"]), False)[0] == "count"
    what, message = grading.differ(key, r(["a", "b"], ["1", "x"], ["2", "z"]), False)
    assert what == "row" and "(2, y)" in message
    what, message = grading.differ(key, r(["a", "b"], ["2", "y"], ["1", "x"]), True)
    assert what == "order" and message.startswith("row 1:")
    assert grading.differ(key, None, False)[0] == "none"


def test_a_probe_that_must_fail_compares_on_its_code():
    def fails(code, message="m"):
        return {"error": {"code": code, "message": message, "position": None}}

    want = fails("23505", 'duplicate key "teams_name_key"')
    assert grading.probe_differ(want, fails("23505", "other name")) is None
    assert "succeeded" in grading.probe_differ(want, r(["n"], ["1"]))
    assert "23502" in grading.probe_differ(r(["n"], ["1"]), fails("23502"))


def test_a_table_reads_like_psql_and_says_what_it_cut():
    text = grading.table(r(["name", "n"], ["Ada", "1"], ["Grace", None]))
    assert text.splitlines() == [
        "name  | n",
        "------+-----",
        "Ada   | 1",
        "Grace | NULL",
        "(2 rows)",
    ]
    many = grading.table(r(["n"], *[[str(i)] for i in range(25)]))
    assert many.endswith("(25 rows, 5 not shown)")


def test_a_position_is_a_line_in_the_learners_file():
    assert grading.line_of("SELECT 1;\nSELEC 2", 11) == 2
    assert grading.line_of("SELECT 1", 1) == 1
