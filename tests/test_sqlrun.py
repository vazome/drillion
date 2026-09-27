"""sqlrun.mjs on its own: passes on one PGlite, each starting from the schema alone."""

import json
import subprocess

import pytest

from drillion import pglite

pytestmark = pytest.mark.skipif(
    pglite.installed() is None,
    reason="PGlite is not installed: run `drillion doctor --fetch`",
)

SCHEMA = "CREATE TABLE t (id integer PRIMARY KEY, v numeric, j jsonb, d date);"


def _run(tmp_path, passes, schema=SCHEMA):
    job = tmp_path / "job.json"
    job.write_text(
        json.dumps({"pglite": str(pglite.home()), "schema": schema, "passes": passes})
    )
    out = tmp_path / "out.json"
    subprocess.run(
        [
            str(pglite.node()),
            *pglite.NODE_FLAGS,
            str(pglite.RUNNER),
            str(job),
            str(out),
        ],
        check=True,
        capture_output=True,
        timeout=60,
    )
    return json.loads(out.read_text())["passes"]


def _pass(sql, rows=None, probes=(), explain=False):
    return {"rows": rows or {}, "sql": sql, "probes": list(probes), "explain": explain}


def test_values_come_back_as_postgres_text(tmp_path):
    rows = {"t": [{"id": 1, "v": "2.50", "j": '{"a": 1}', "d": "2026-01-02"}]}
    [p] = _run(
        tmp_path,
        [
            _pass(
                "SELECT id, v, j, d, 9007199254740993::bigint AS b, true AS t FROM t",
                rows,
            )
        ],
    )
    assert p["result"] == {
        "fields": ["id", "v", "j", "d", "b", "t"],
        "rows": [["1", "2.50", '{"a": 1}', "2026-01-02", "9007199254740993", "t"]],
        "count": 1,
    }


def test_each_pass_starts_from_the_schema_alone(tmp_path):
    first, second = _run(
        tmp_path,
        [
            _pass("DROP TABLE t; CREATE SCHEMA extra; SET search_path = extra;"),
            _pass(
                "SELECT count(*) AS n FROM public.t; "
                "SELECT nspname FROM pg_namespace WHERE nspname = 'extra'"
            ),
        ],
    )
    assert first["error"] is None
    assert second["error"] is None and second["result"]["rows"] == []


def test_an_error_carries_its_code_and_position(tmp_path):
    [p] = _run(tmp_path, [_pass("SELECT 1;\nSELEC 2")])
    assert p["error"]["code"] == "42601" and p["error"]["position"] == 11


def test_probes_run_after_and_never_see_each_other(tmp_path):
    [p] = _run(
        tmp_path,
        [
            _pass(
                "INSERT INTO t (id) VALUES (1)",
                probes=[
                    ["dup", "INSERT INTO t (id) VALUES (1)"],
                    [
                        "insert",
                        "INSERT INTO t (id) VALUES (2); SELECT count(*) AS n FROM t",
                    ],
                    ["after", "SELECT count(*) AS n FROM t"],
                ],
            )
        ],
    )
    assert p["result"] is None
    assert p["probes"]["dup"]["error"]["code"] == "23505"
    assert p["probes"]["insert"]["rows"] == [["2"]]
    assert p["probes"]["after"]["rows"] == [["1"]], "the insert probe was rolled back"


def test_a_plan_is_returned_when_asked(tmp_path):
    [p] = _run(
        tmp_path,
        [_pass("SELECT id, row_number() OVER (ORDER BY id) FROM t", explain=True)],
    )
    assert "WindowAgg" in p["plan"]


def test_a_broken_schema_is_a_setup_error(tmp_path):
    [p] = _run(tmp_path, [_pass("SELECT 1")], schema="CREATE TABL x")
    assert p["setup"]["code"] == "42601"
