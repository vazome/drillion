"""Tests for the drill core in study.py and the API in web.py. Plain functions,
no fixtures.

The expensive ones sweep every exercise file: splice/stub/spec must be exactly
reversible or a save would corrupt a drill. The API tests drive the real app
over ASGI, against a throwaway copy of one drill.
"""

import ast
import asyncio
import inspect
import shutil
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path

import httpx
import pytest

import study
import web

FILES = sorted(study.EXDIR.glob("ex_*.py"))
SRC = (study.EXDIR / "ex_001_fstrings.py").read_text()

SPEC = '    """WHY: the spec the editor never shows.\n\n    YOU RETURN: x.\n    """'


def _parts(src=SRC):
    """(region body, editor text, spec source) of a pristine file."""
    body = study.cut(src).body
    spec = study.strip_spec(body)
    return body, spec.editor, spec.spec_src


def _solved(src=SRC, code="return ''"):
    """`src` with the region's `raise` replaced by real code."""
    return study.splice(src, study.cut(src).body.replace("raise NotImplementedError", code))


def _exs():
    """A tiny catalogue: ex_b needs ex_a, which is not in the rsample track."""
    return {"ex_a": {"topic": 1, "minutes": 5, "prereqs": [], "tags": ["core"]},
            "ex_b": {"topic": 2, "minutes": 5, "prereqs": [1], "tags": ["core", "rsample"]},
            "ex_c": {"topic": 3, "minutes": 5, "prereqs": [], "tags": ["rsample"]}}


def _st(**kw):
    return {"focus": None, "cards": {}, "open": {}, "log": [], "archive": {}, **kw}


# ------------------------------------------------------------ region: all files
def test_splice_puts_every_file_back_exactly():
    assert len(FILES) >= 79
    for f in FILES:
        src = f.read_text()
        assert study.splice(src, study.cut(src).body) == src, f.name


def test_stub_is_identity_on_pristine_files():
    drafts = set(study.load()["open"])           # an open attempt means the file holds live work
    for f in FILES:
        if f.stem in drafts:
            continue
        body = study.cut(f.read_text()).body
        assert study.stub(body) == body, f.name


def test_spec_survives_the_round_trip_on_every_file():
    for f in FILES:
        body, editor, spec_src = _parts(f.read_text())
        assert ast.get_docstring(study._solve(ast.parse(editor))) is None, f.name
        assert study.merge_spec(editor, spec_src) == body, f.name


def test_strip_spec_reports_the_docstring_it_removed():
    body, editor, spec_src = _parts()
    spec = study.strip_spec(body)
    assert spec.doc_offset == len(spec_src.split("\n"))
    assert len(editor.split("\n")) + spec.doc_offset == len(body.split("\n"))
    assert spec.spec_text == inspect.cleandoc(ast.literal_eval(spec_src.strip()))


def test_strip_spec_survives_a_solve_without_a_docstring():
    spec = study.strip_spec("def solve(x):\n    return x")
    assert spec.editor == "def solve(x):\n    return x"
    assert spec.spec_src is None and spec.doc_offset == 0
    assert study.merge_spec(spec.editor, spec.spec_src) == spec.editor


# ------------------------------------------------------------ merge edge cases
def test_merge_rejects_a_one_line_def():
    with pytest.raises(study.Invalid):
        study.merge_spec("def solve(x): return x", SPEC)


def test_merge_rejects_a_body_hiding_on_the_signature_line():
    with pytest.raises(study.Invalid):
        study.merge_spec("def solve(\n    x,\n): return x", SPEC)


def test_merge_accepts_a_two_space_body():
    out = study.merge_spec("def solve(x):\n  return x", SPEC)
    assert '\n  """WHY' in out and "\n  YOU RETURN" in out
    assert ast.get_docstring(study._solve(ast.parse(out))).startswith("WHY:")


def test_a_two_space_save_survives_a_second_save():
    """The spec goes back at the learner's own indentation, so the next save must
    not assume the pristine four spaces."""
    body, editor, spec_src = _parts()
    once = study.merge_spec(editor.replace("    raise NotImplementedError", "  return ''"), spec_src)
    again = study.strip_spec(once)
    assert again.spec_text == study.strip_spec(body).spec_text     # the spec text is unchanged
    assert study.merge_spec(again.editor, again.spec_src) == once  # and stable from here on


def test_merge_accepts_a_tab_body():
    out = study.merge_spec("def solve(x):\n\treturn x", SPEC)
    assert '\n\t"""WHY' in out
    assert ast.get_docstring(study._solve(ast.parse(out))).startswith("WHY:")


def test_merge_drops_a_pasted_docstring():
    out = study.merge_spec('def solve(x):\n    """stale copy."""\n    return x * 2', SPEC)
    assert "stale copy" not in out and out.count('"""') == 2
    assert out.endswith("    return x * 2")


def test_merge_rejects_a_body_that_is_only_a_pasted_docstring():
    with pytest.raises(study.Invalid):
        study.merge_spec('def solve(x):\n    """stale copy."""', SPEC)


def test_merge_accepts_a_comment_first_body():
    out = study.merge_spec("def solve(x):\n    # plan: double it\n    return x * 2", SPEC)
    assert "# plan: double it" in out
    assert ast.get_docstring(study._solve(ast.parse(out))).startswith("WHY:")


def test_merge_keeps_a_decorator_and_the_code_above_solve():
    out = study.merge_spec("import functools\n\n\n@functools.cache\ndef solve(x):\n    return x", SPEC)
    assert "@functools.cache" in out and out.startswith("import functools")
    assert ast.get_docstring(study._solve(ast.parse(out))).startswith("WHY:")


# ------------------------------------------------------------ the write gate
def test_validate_accepts_a_normal_edit():
    _, editor, spec_src = _parts()
    new = study.validate(editor.replace("raise NotImplementedError", "return ''"), spec_src, SRC)
    ast.parse(new)
    assert '"""WHY' in new and "def _reference(" in new and "return ''" in new
    assert new.split("\n")[:6] == SRC.split("\n")[:6]


def test_validate_reports_the_line_of_a_syntax_error():
    _, _, spec_src = _parts()
    with pytest.raises(study.Invalid) as e:
        study.validate("def solve(rows)\n    return ''", spec_src, SRC)
    assert e.value.line == 1


def test_validate_rejects_bad_regions():
    _, _, spec_src = _parts()
    bad = {
        "empty": "   \n",
        "no solve": "def helper(x):\n    return x",
        "two solves": "def solve(x):\n    return x\n\n\ndef solve(y):\n    return y",
        "machinery": "def _reference(rows):\n    return ''\n\n\ndef solve(rows):\n    return ''",
        "test": "def test_x():\n    pass\n\n\ndef solve(rows):\n    return ''",
        "peeking": "def solve(rows):\n    return _reference(rows)",
    }
    for why, edited in bad.items():
        try:
            study.validate(edited, spec_src, SRC)
        except study.Invalid:
            continue
        raise AssertionError(f"validate accepted {why}")


def test_validate_refuses_to_drop_the_docstring():
    with pytest.raises(study.Invalid):
        study.validate("def solve(rows):\n    return ''", None, SRC)


def test_stub_keeps_given_code():
    for name, needle in (("ex_036_env.py", "TRUTHY = {"), ("ex_044_customexc.py", "class ConfigError")):
        body = study.cut((study.EXDIR / name).read_text()).body
        stubbed = study.stub(body.replace("raise NotImplementedError", "return {}"))
        assert needle in stubbed and "return {}" not in stubbed
        assert stubbed.endswith("    raise NotImplementedError")
        assert ast.get_docstring(study._solve(ast.parse(stubbed))).startswith("WHY:")


def test_has_given_spots_code_above_solve():
    assert study.has_given(study.cut((study.EXDIR / "ex_036_env.py").read_text()).body)
    assert not study.has_given(study.cut(SRC).body)


def test_etag_tracks_only_the_learner_region():
    assert len(study.etag(SRC)) == 12
    assert study.etag(SRC) == study.etag(SRC.replace('"""f-string', '"""FSTRING'))
    assert study.etag(SRC) != study.etag(_solved())


def test_write_region_is_atomic_and_keeps_the_docstring():
    tmp = Path(tempfile.mkdtemp())
    try:
        path = tmp / "ex_001_fstrings.py"
        path.write_text(SRC)
        study.write_region(path, _solved())
        assert "return ''" in path.read_text() and '"""WHY' in path.read_text()
        assert not list(tmp.glob("*.tmp"))
        with pytest.raises(study.Invalid):
            study.write_region(path, study.splice(SRC, _parts()[1]))
        assert '"""WHY' in path.read_text()
    finally:
        shutil.rmtree(tmp)


# ------------------------------------------------------------ catalogue
def test_exercises_reads_every_file_by_ast():
    exs = study.exercises()
    assert len(exs) == len(FILES)
    m = exs["ex_001_fstrings"]
    assert m["topic"] == 1 and m["minutes"] == 10 and len(m["hints"]) == 3
    assert m["path"].name == "ex_001_fstrings.py" and isinstance(m["tags"], list)
    lines = SRC.split("\n")
    assert lines[m["region_start"] - 1].startswith("def solve(")
    assert lines[m["hints_line"] - 1].startswith("HINTS")


def test_read_first_reads_the_comment_block_after_the_docstring():
    file = ('"""Doc."""\n\n{}\n\nMETA = {{"topic": 1}}\n\n\n'
            'def solve():\n    """s."""\n    raise NotImplementedError\n\n\nHINTS = []\n')
    assert study.read_first(file.format("# READ FIRST:\n#   https://x\n#   https://y")) == [
        "READ FIRST:", "  https://x", "  https://y"]
    assert study.read_first(file.format("# just a note")) == []     # only the READ FIRST block
    assert study.read_first(file.format("import os")) == []
    assert study.read_first(file.format(                                   # exercism attribution
        "# SOURCE: exercism/python practice/leap (MIT, adapted)\n# READ FIRST:\n#   https://x")) == [
        "READ FIRST:", "  https://x"]


def test_solution_returns_only_the_reference():
    text = study._solution(study.EXDIR / "ex_001_fstrings.py")
    assert text.startswith("def _reference(") and "def test_" not in text


# ------------------------------------------------------------ pytest output
CANNED = """\
=================================== FAILURES ===================================
__________________________________ test_solve __________________________________

    def test_solve():
>       assert solve(list(rows)) == _reference(rows)

exercises/ex_001_fstrings.py:78:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

>       raise NotImplementedError
E       NotImplementedError

exercises/ex_001_fstrings.py:38: NotImplementedError
=========================== short test summary info ============================
FAILED exercises/ex_001_fstrings.py::test_solve - NotImplementedError
"""


def test_summarise_maps_the_region_to_editor_lines():
    out = study.summarise(CANNED, region_start=9, doc_offset=28, hints_line=41)
    assert out["headline"] == ["E       NotImplementedError"]
    assert "line 2: NotImplementedError" in out["output"]          # the learner's raise
    assert "exercises/ex_001_fstrings.py:78:" in out["output"]     # the test frame stays put


def test_summarise_falls_back_to_the_failed_line_and_caps_the_headline():
    only_failed = "FAILED exercises/ex_001_fstrings.py::test_solve - boom\n"
    assert study.summarise(only_failed, 9, 28, 41)["headline"] == [only_failed.strip()]
    noisy = "\n".join(f"E   line {i}" for i in range(9))
    assert len(study.summarise(noisy, 9, 28, 41)["headline"]) == 6


# ------------------------------------------------------------ scheduler
def test_grade_of():
    assert study.grade_of(1, 120, 10, False) == "easy"
    assert study.grade_of(2, 900, 10, False) == "pass"
    assert study.grade_of(4, 100, 10, False) == "struggled"
    assert study.grade_of(1, 10, 10, True) == "struggled"          # a peeked answer never promotes


def test_reschedule():
    c = {"box": 0, "due": "2000-01-01", "seen": 1}
    assert study.reschedule(c, "easy") == 8 and c["box"] == 2      # +2 boxes, LADDER[2]
    assert study.reschedule(c, "struggled") == 8 and c["box"] == 2  # same box, same gap
    assert study.reschedule(c, "fail") == 2 and c["box"] == 0      # -2 boxes, back to the start
    assert c["due"] == (date.today() + timedelta(days=2)).isoformat()  # noqa: DTZ011


def test_unseen_respects_prereqs():
    assert study.unseen(_st(), _exs()) == ["ex_a", "ex_c"]         # ex_b waits for topic 1
    st = _st(cards={"ex_a": {"box": 1, "due": "2000-01-01", "seen": 1}})
    assert study.unseen(st, _exs()) == ["ex_b", "ex_c"]


def test_focus_ignores_out_of_focus_prereqs():
    assert study.unseen(_st(focus="rsample"), _exs()) == ["ex_b", "ex_c"]
    assert study.unseen(_st(focus="core"), _exs()) == ["ex_a"]


def test_queue_caps_new_picks_and_skips_open_attempts():
    q = study.queue(_st(open={"ex_a": {}}), _exs())
    assert q == {"review": [], "new": ["ex_c"], "done_today": 0}
    done = [{"date": study.today(), "slug": "ex_a", "grade": "pass", "attempts": 1, "secs": 9, "new": True},
            {"date": study.today(), "slug": "ex_z", "grade": "pass", "attempts": 1, "secs": 9, "new": False}]
    q = study.queue(_st(log=done), _exs())
    assert q["done_today"] == 1 and q["new"] == ["ex_a"]            # one new pick left today


def test_queue_puts_the_most_overdue_review_first():
    st = _st(cards={"ex_a": {"box": 1, "due": "2020-01-02", "seen": 1},
                    "ex_c": {"box": 1, "due": "2020-01-01", "seen": 1}})
    assert study.queue(st, _exs())["review"] == ["ex_c", "ex_a"]
    assert study.pick(st, _exs()) == ("ex_c", "review")


# ------------------------------------------------------------ attempts
def test_touch_caps_a_long_gap():
    o = {"active": 0, "last": (datetime.now() - timedelta(seconds=600)).isoformat()}  # noqa: DTZ005
    assert study.touch(o) == 120                                   # a break is not work
    assert study.touch(o) == 120                                   # no time has passed since


def test_attempt_lifecycle():
    st, exs = _st(), _exs()
    o = study.open_attempt(st, "ex_a")
    assert o["new"] and o["attempts"] == 0 and 1000 <= o["seed"] <= 9999
    assert study.open_attempt(st, "ex_a") is o                     # reopening keeps the timer
    o["attempts"], o["active"] = 1, 30
    grade, gap, box = study.record_pass(st, "ex_a", exs["ex_a"], "def solve(x):\n    return x")
    assert (grade, gap, box) == ("easy", 8, 2)
    assert st["open"] == {} and st["cards"]["ex_a"]["seen"] == 1
    assert st["log"][-1] == {"date": study.today(), "slug": "ex_a", "grade": "easy",
                             "attempts": 1, "secs": 30, "new": True}
    assert st["archive"]["ex_a"][0]["code"].startswith("def solve(")
    assert study.open_attempt(st, "ex_a")["new"] is False           # a review, not a new pick


def test_hints_are_gated_by_active_time():
    st, hints = _st(), ["one", "two", "three"]
    o = study.open_attempt(st, "ex_a")
    assert study.next_hint(st, "ex_a", hints) == (1, "one")         # the first is free
    with pytest.raises(study.Gated) as e:
        study.next_hint(st, "ex_a", hints)
    assert 0 < e.value.wait_secs <= 120
    o["active"] = 600
    assert study.next_hint(st, "ex_a", hints) == (2, "two")
    assert study.next_hint(st, "ex_a", hints) == (3, "three")
    with pytest.raises(study.Gated):
        study.next_hint(st, "ex_a", hints)                          # exhausted: use the solution


def test_solution_unlocks_after_three_attempts_and_ten_minutes():
    st = _st()
    o = study.open_attempt(st, "ex_a")
    o.update(attempts=3, active=599)
    assert study.unlock_solution(st, "ex_a") is False
    o["active"] = 600
    assert study.unlock_solution(st, "ex_a") is True
    assert o["solution_shown"] is True


def test_abandon_archives_real_work_and_resets_the_file():
    st = _st()
    study.open_attempt(st, "ex_001_fstrings")
    assert study.abandon(st, "ex_001_fstrings", _solved()) == SRC
    assert st["open"] == {}
    kept = st["archive"]["ex_001_fstrings"][0]
    assert kept["grade"] == "abandoned" and "return ''" in kept["code"] and '"""WHY' not in kept["code"]


def test_abandon_does_not_archive_an_untouched_stub():
    st = _st()
    study.open_attempt(st, "ex_001_fstrings")
    assert study.abandon(st, "ex_001_fstrings", SRC) == SRC
    assert st["archive"] == {} and st["open"] == {}


def test_load_fills_in_the_keys_an_older_file_lacks():
    tmp, keep = Path(tempfile.mkdtemp()), study.STATE
    try:
        study.STATE = tmp / "progress.json"
        assert study.load() == {"focus": None, "cards": {}, "open": {}, "log": [], "archive": {}}
        study.save({"cards": {"ex_a": {"box": 1, "due": "2020-01-01", "seen": 1}}})
        st = study.load()
        assert st["cards"]["ex_a"]["box"] == 1                       # what was there is kept
        assert st["focus"] is None and st["open"] == {} and st["log"] == []
        assert not list(tmp.glob("*.tmp"))                           # the write was atomic
    finally:
        study.STATE = keep
        shutil.rmtree(tmp)


# ------------------------------------------------------------ the web API
SLUG = "ex_001_fstrings"
PASSING = 'return "\\n".join(f"{name:<14}{value:>12,.2f}" for name, value in rows)'


def _api(flow):
    """Run `flow(api, path)` against a throwaway copy of one drill: the API tests
    write real files, and Daniel's exercises/ and progress.json are not for that."""
    tmp, keep = Path(tempfile.mkdtemp(prefix="study_api_")), (study.EXDIR, study.STATE)
    for name in (f"{SLUG}.py", "_lib.py"):
        shutil.copy(study.EXDIR / name, tmp / name)
    study.EXDIR, study.STATE = tmp, tmp / "progress.json"

    async def drive():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=web.app),
                                     base_url="http://127.0.0.1") as api:
            await flow(api, tmp / f"{SLUG}.py")

    try:
        asyncio.run(drive())
    finally:
        study.EXDIR, study.STATE = keep
        shutil.rmtree(tmp)


async def _stub_to_pass(api, path):
    cat = (await api.get("/api/catalogue")).json()
    assert [e["slug"] for e in cat["exercises"]] == [SLUG]
    assert cat["exercises"][0]["status"] == "new" and cat["today"]["new"] == [SLUG]
    assert cat["tags"] == ["core"] and cat["stats"]["total"] == 1

    ex = (await api.post(f"/api/ex/{SLUG}/open")).json()
    assert ex["attempt"]["attempts"] == 0 and ex["status"] == "open"
    assert ex["spec"].startswith("WHY:") and '"""' not in ex["code"]   # the spec is not editable
    assert "raise NotImplementedError" in ex["code"] and "_reference" not in ex["code"]

    run = (await api.post(f"/api/ex/{SLUG}/run",
                          json={"code": ex["code"], "etag": ex["etag"]})).json()
    assert run["passed"] is False and run["attempts"] == 1
    assert any("NotImplementedError" in ln for ln in run["headline"])

    two_space = ex["code"].replace("    raise NotImplementedError", "  return ''")
    put = await api.put(f"/api/ex/{SLUG}", json={"code": two_space, "etag": run["etag"]})
    assert put.status_code == 200
    assert '\n  """WHY' in path.read_text()          # the spec went back, at the learner's indent

    stale = await api.put(f"/api/ex/{SLUG}", json={"code": two_space, "etag": run["etag"]})
    assert stale.status_code == 409                  # that etag is one save out of date
    assert stale.json()["etag"] == put.json()["etag"] and "return ''" in stale.json()["code"]

    solved = ex["code"].replace("raise NotImplementedError", PASSING)
    run = (await api.post(f"/api/ex/{SLUG}/run",
                          json={"code": solved, "etag": put.json()["etag"]})).json()
    assert run["passed"] is True and run["attempts"] == 2
    assert run["grade"] in study.GRADES and run["due_in"] == study.LADDER[run["box"]]
    body = study.cut(path.read_text()).body
    assert study.stub(body) == body                  # passing puts the stub back on disk

    st = study.load()
    assert st["open"] == {} and [e["slug"] for e in st["log"]] == [SLUG]
    assert PASSING in st["archive"][SLUG][0]["code"]

    again = (await api.post(f"/api/ex/{SLUG}/open")).json()
    assert again["attempt"] == {"attempts": 0, "hints": 0, "active": 0,
                                "seed": again["attempt"]["seed"], "solution_shown": False}
    assert "raise NotImplementedError" in again["code"]
    assert "code" not in again["archive"][0]         # a review never sees last time's answer
    assert again["solution"] == {"unlocked": False, "need_attempts": 3, "need_secs": 600}

    hint = await api.post(f"/api/ex/{SLUG}/hint")
    assert hint.status_code == 200 and (hint.json()["level"], hint.json()["total"]) == (1, 3)
    soon = await api.post(f"/api/ex/{SLUG}/hint")
    assert soon.status_code == 423 and 0 < soon.json()["wait_secs"] <= 120

    assert (await api.get("/api/catalogue", headers={"Host": "evil.com"})).status_code == 400


async def _guards(api, path):
    assert (await api.get("/api/catalogue")).status_code == 200
    assert not study.STATE.exists()                  # a GET never writes progress.json

    missing = await api.get("/api/ex/_lib")          # a real file, but not in the catalogue
    assert missing.status_code == 404 and missing.json()["error"] == "no exercise '_lib'"
    assert (await api.get("/api/ex/..%2f..%2fetc%2fpasswd")).status_code == 404
    assert (await api.post("/api/ex/ex_999_nope/open")).status_code == 404

    ex = (await api.get(f"/api/ex/{SLUG}")).json()
    assert ex["attempt"] is None and ex["hints"]["shown"] == []
    nobody = await api.post(f"/api/ex/{SLUG}/run", json={"code": ex["code"], "etag": ex["etag"]})
    assert nobody.status_code == 409                 # no attempt open: nothing to time or count

    huge = await api.put(f"/api/ex/{SLUG}", json={"code": "x" * (web.MAX_BODY + 1), "etag": ""})
    assert huge.status_code == 413

    await api.post(f"/api/ex/{SLUG}/open")
    broken = await api.put(f"/api/ex/{SLUG}", json={"code": "def solve(rows):\n    return 1 1",
                                                   "etag": ex["etag"]})
    assert broken.status_code == 400 and (broken.json()["line"], broken.json()["col"]) == (2, 14)
    assert "raise NotImplementedError" in path.read_text()    # a rejected edit never lands

    cheat = await api.put(f"/api/ex/{SLUG}",
                          json={"code": "def solve(rows):\n    return _reference(rows)",
                                "etag": ex["etag"]})
    assert cheat.status_code == 400 and "_reference" in cheat.json()["error"]

    assert (await api.post(f"/api/ex/{SLUG}/solution")).status_code == 423
    assert (await api.post("/api/focus", json={"tag": "core"})).json() == {"focus": "core"}
    assert (await api.get("/api/catalogue")).json()["focus"] == "core"
    assert (await api.get("/api/progress")).json()["per_tag"] == {"core": {"seen": 0, "total": 1}}

    stub_etag = (await api.get(f"/api/ex/{SLUG}")).json()["etag"]
    gone = await api.post(f"/api/ex/{SLUG}/abandon", json={"etag": stub_etag})
    assert gone.status_code == 200 and gone.json()["attempt"] is None
    assert study.load()["archive"] == {}              # an untouched stub is not worth keeping


def test_the_api_carries_a_drill_from_stub_to_pass():
    _api(_stub_to_pass)


def test_the_api_guards_its_edges():
    _api(_guards)
