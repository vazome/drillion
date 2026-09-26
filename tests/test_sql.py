"""SQL grading: every rule a SQL task shows is one its grader enforces, through the real
pipeline (PGlite in the sandbox, as a submission is), plus the comparison on its own."""

import importlib.util
import random
import uuid
from decimal import Decimal

import pytest

from drillion import catalogue, grading, kinds, manifest, pglite, runner

needs_pglite = pytest.mark.skipif(
    pglite.installed() is None,
    reason="PGlite is not installed: run `drillion doctor --fetch`",
)
SEEDS = [0, 1, 2]
# (what in the answer key, what to put instead); `{name}` placeholders are the brief's.
# Each row breaks one rule the task shows, and must fail.
BREAKS = {
    "324_sql_first_select": [
        ("joined DESC", "joined"),
        ("\nLIMIT {n}", ""),
        ("city = '{city}'", "city <> '{city}'"),
        ("SELECT name, joined", "SELECT joined, name"),
        ("ORDER BY joined DESC, name", "ORDER BY name"),
    ],
    "325_sql_group_count": [
        ("WHERE status = 'paid'\n", ""),
        (">= {at_least}", "> {at_least}"),
        ("HAVING count(*) >= {at_least}\n", ""),
        ("count(*) AS paid_orders", "count(*)"),
        ("paid_orders DESC, customer_id", "customer_id"),
    ],
    "326_sql_inner_join": [
        ("c.id = o.customer_id", "c.id = o.id"),
        ("WHERE c.city = '{city}'\n", ""),
        ("o.id AS order_id", "o.id"),
        ("c.name, o.status", "o.status, c.name"),
    ],
    "327_sql_left_join_null": [
        ("LEFT JOIN", "JOIN"),
        (
            " AND o.status <> 'refunded'\nWHERE c.city = '{city}'",
            "\nWHERE c.city = '{city}' AND o.status <> 'refunded'",
        ),
        ("COALESCE(sum(o.total), 0)", "sum(o.total)"),
        ("count(o.id)", "count(*)"),
    ],
    "328_sql_never_referred": [
        (
            "NOT EXISTS (\n    SELECT 1 FROM customers AS r WHERE r.referred_by = c.id\n  )",
            "c.id NOT IN (SELECT referred_by FROM customers)",
        ),
        ("c.city = '{city}'\n  AND ", ""),
        ("NOT EXISTS", "EXISTS"),
    ],
    "329_sql_cte_above_average": [
        ("(SELECT avg(spent) FROM spend)", "(SELECT avg(total) FROM orders)"),
        ("  WHERE status = '{status}'\n", ""),
        ("spent DESC, customer_id", "customer_id"),
    ],
    "330_sql_top_n_per_city": [
        (
            "row_number() OVER (PARTITION BY c.city ORDER BY o.total DESC, o.id)",
            "rank() OVER (PARTITION BY c.city ORDER BY o.total DESC)",
        ),
        ("PARTITION BY c.city ", ""),
        ("place <= {n}", "place < {n}"),
        ("o.total DESC", "o.total"),
    ],
    "331_sql_running_total": [
        ("sum(revenue) OVER (ORDER BY day)", "sum(revenue) OVER ()"),
        ("lag(revenue)", "lead(revenue)"),
        ("WHERE status <> 'refunded'\n    AND ", "WHERE "),
        (
            (
                "sum(revenue) OVER (ORDER BY day) AS running_total,\n"
                "       revenue - lag(revenue) OVER (ORDER BY day) AS change"
            ),
            (
                "(SELECT sum(d.revenue) FROM daily AS d WHERE d.day <= daily.day)"
                " AS running_total,\n"
                "       revenue - (SELECT d.revenue FROM daily AS d WHERE d.day < daily.day"
                " ORDER BY d.day DESC LIMIT 1) AS change"
            ),
        ),
    ],
    "332_sql_days_without_orders": [
        ("LEFT JOIN", "JOIN"),
        ("count(o.id)", "count(*)"),
        (" - INTERVAL '1 day'", ""),
    ],
    "333_sql_latest_per_customer": [
        ("placed_at DESC, id DESC", "placed_at, id"),
        ("DISTINCT ON (customer_id) ", ""),
        ("WHERE status = '{status}'\n", ""),
        ("id AS order_id", "id"),
    ],
    "334_sql_jsonb_attributes": [
        ("attrs ->> 'size'", "attrs -> 'size'"),
        ("\n  AND (attrs ->> 'stock')::int > 0", ""),
        ('"color": "{color}"', '"color": "none"'),
    ],
    "335_sql_upsert_settings": [
        ("settings.prefs || excluded.prefs", "excluded.prefs"),
        (
            (
                "DO UPDATE\nSET prefs = settings.prefs || excluded.prefs,\n"
                "    updated_on = excluded.updated_on"
            ),
            "DO NOTHING",
        ),
        ("updated_on = excluded.updated_on", "updated_on = settings.updated_on"),
        (
            (
                "\nON CONFLICT (user_id) DO UPDATE\n"
                "SET prefs = settings.prefs || excluded.prefs,\n"
                "    updated_on = excluded.updated_on"
            ),
            "",
        ),
    ],
    "336_sql_first_schema": [
        ("name text NOT NULL UNIQUE", "name text NOT NULL"),
        (" ON DELETE CASCADE", ""),
        (" DEFAULT '{role}'", ""),
        (" CHECK (role IN ('owner', '{role}'))", ""),
        ("email text NOT NULL UNIQUE", "email text UNIQUE"),
        ("name text NOT NULL UNIQUE", "name varchar(100) NOT NULL UNIQUE"),
    ],
    "337_sql_safe_migration": [
        ("\n  ALTER COLUMN plan SET DEFAULT 'free',", ""),
        ("  ALTER COLUMN plan SET NOT NULL,\n", ""),
        (
            ",\n  ADD CONSTRAINT accounts_plan_known CHECK (plan IN ('free', '{paid}'))",
            "",
        ),
        ("THEN '{paid}'", "THEN 'free'"),
        ("ADD COLUMN plan text;", "ADD COLUMN plan text NOT NULL;"),
    ],
    "338_sql_updated_at_trigger": [
        ("\nWHEN (OLD.{watched} IS DISTINCT FROM NEW.{watched})", ""),
        ("BEFORE UPDATE", "AFTER UPDATE"),
        ("FOR EACH ROW", "FOR EACH STATEMENT"),
        (
            "OLD.{watched} IS DISTINCT FROM NEW.{watched}",
            "OLD.{other} IS DISTINCT FROM NEW.{other}",
        ),
    ],
}


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


def _sql_tasks():
    return {
        s: m for s, m in catalogue.tasks().items() if m.get("kind") == catalogue.SQL
    }


def _grade(meta, brief, text, seed=0):
    """The real child, grading `text` as the learner's task.sql. It sits under tasks/, the
    one tree the sandbox reads, under a unique name so parallel workers stay apart."""
    path = meta["dir"] / f"_test_{uuid.uuid4().hex}.sql"
    path.write_text(text, encoding="utf-8")
    try:
        passed, diagnostics, *_ = runner.run_manifest(
            meta, brief, learner=path, **kinds.of(meta).extra(meta, brief, seed)
        )
    finally:
        path.unlink()
    return passed, diagnostics


def _filled(part, brief):
    for key, value in brief.items():
        part = part.replace(f"{{{key}}}", str(value))
    return part


@needs_pglite
def test_every_sql_task_has_its_rules_listed():
    assert set(_sql_tasks()) == set(BREAKS)


@needs_pglite
@pytest.mark.parametrize("slug", sorted(BREAKS))
@pytest.mark.parametrize("seed", SEEDS)
def test_the_answer_key_passes(slug, seed):
    meta = _sql_tasks()[slug]
    brief = manifest.generate_brief(meta, seed)
    key = kinds.of(meta).answer_key(meta, brief)
    assert _grade(meta, brief, key, seed) == (True, [])


@needs_pglite
@pytest.mark.parametrize(
    ("slug", "row"),
    [
        pytest.param(slug, row, id=f"{slug[:3]}-{i}")
        for slug, rows in sorted(BREAKS.items())
        for i, row in enumerate(rows)
    ],
)
def test_every_broken_rule_fails(slug, row):
    meta = _sql_tasks()[slug]
    brief = manifest.generate_brief(meta, 0)
    key = kinds.of(meta).answer_key(meta, brief)
    old, new = (_filled(part, brief) for part in row)
    assert old in key, (slug, old)
    passed, diagnostics = _grade(meta, brief, key.replace(old, new))
    assert not passed and diagnostics, (slug, old)


def _module(meta):
    spec = importlib.util.spec_from_file_location(
        "g" + uuid.uuid4().hex, meta["dir"] / "grade.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@needs_pglite
def test_a_hard_coded_answer_fails_on_the_hidden_dataset():
    meta = _sql_tasks()["324_sql_first_select"]
    brief = manifest.generate_brief(meta, 0)
    people = _module(meta).rows(random.Random("rows:0"), brief)["customers"]
    shown = sorted(
        (c for c in people if c["city"] == brief["city"]),
        key=lambda c: (-c["joined"].toordinal(), c["name"]),
    )
    values = ", ".join(
        f"('{c['name']}', DATE '{c['joined']}')" for c in shown[: brief["n"]]
    )
    passed, diagnostics = _grade(
        meta, brief, f"SELECT * FROM (VALUES {values}) AS v (name, joined)"
    )
    assert not passed and "hidden" in diagnostics[0]["message"]
    assert not any(c["name"] in diagnostics[0]["message"] for c in shown)


@needs_pglite
def test_a_syntax_error_marks_its_own_line():
    meta = _sql_tasks()["324_sql_first_select"]
    brief = manifest.generate_brief(meta, 0)
    passed, diagnostics = _grade(
        meta, brief, "SELECT name\nFROM customers\nWHER city = 'x'"
    )
    assert not passed
    assert diagnostics[0]["file"] == "task.sql" and diagnostics[0]["line"] == 3
    assert "42601" in diagnostics[0]["message"]


@needs_pglite
def test_a_query_that_never_ends_is_the_learners_failure(monkeypatch):
    monkeypatch.setattr(manifest, "VALIDATOR_SECONDS", 3)
    meta = _sql_tasks()["324_sql_first_select"]
    brief = manifest.generate_brief(meta, 0)
    endless = (
        "WITH RECURSIVE r (n) AS (SELECT 1 UNION ALL SELECT n + 1 FROM r) "
        "SELECT count(*) FROM r"
    )
    passed, diagnostics = _grade(meta, brief, endless)
    assert not passed and "did not finish" in diagnostics[0]["message"]


@needs_pglite
def test_what_the_learner_drops_is_back_for_the_next_pass():
    """The key ran first and its rows already left the database; the learner's hidden pass
    starts from the schema again, so a DROP after a right answer still passes."""
    meta = _sql_tasks()["324_sql_first_select"]
    brief = manifest.generate_brief(meta, 0)
    key = kinds.of(meta).answer_key(meta, brief)
    assert _grade(meta, brief, key + "\nDROP TABLE customers;") == (True, [])


@needs_pglite
def test_selfcheck_fails_a_key_that_cannot_tell_a_hard_coded_answer():
    """A key returning the same rows on both datasets would let a copied answer pass."""
    meta = _sql_tasks()["324_sql_first_select"]
    brief = manifest.generate_brief(meta, 0)
    constant = "SELECT 'Ada' AS name, DATE '2026-01-01' AS joined"
    extra = kinds.of(meta).extra(meta, brief, 0, selfcheck=True)
    extra["sql"]["key"] = constant
    path = meta["dir"] / f"_test_{uuid.uuid4().hex}.sql"
    path.write_text(constant, encoding="utf-8")
    try:
        passed, diagnostics, *_ = runner.run_manifest(
            meta, brief, learner=path, **extra
        )
    finally:
        path.unlink()
    assert not passed and "same rows on both datasets" in diagnostics[0]["message"]
