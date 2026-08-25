"""Region: cut, splice, spec and the write gate.

Plain functions, no fixtures. The expensive ones sweep every exercise file:
splice/stub/spec must be exactly reversible or a save would corrupt a drill.
"""

import ast
import inspect
import shutil
import tempfile
from pathlib import Path

import pytest

from study import region, state
from study.settings import settings

FILES = sorted(settings.exercises_dir.glob("ex_*.py"))
SRC = (settings.exercises_dir / "ex_001_fstrings.py").read_text()

SPEC = '    """WHY: the spec the editor never shows.\n\n    YOU RETURN: x.\n    """'


def _parts(src=SRC):
    """(region body, editor text, spec source) of a pristine file."""
    body = region.cut(src).body
    spec = region.strip_spec(body)
    return body, spec.editor, spec.spec_src


def _solved(src=SRC, code="return ''"):
    """`src` with the region's `raise` replaced by real code."""
    return region.splice(src, region.cut(src).body.replace("raise NotImplementedError", code))


# ------------------------------------------------------------ region: all files
def test_splice_puts_every_file_back_exactly():
    assert len(FILES) >= 79
    for f in FILES:
        src = f.read_text()
        assert region.splice(src, region.cut(src).body) == src, f.name


def test_stub_is_identity_on_pristine_files():
    drafts = set(state.load()["open"])           # an open attempt means the file holds live work
    for f in FILES:
        if f.stem in drafts:
            continue
        body = region.cut(f.read_text()).body
        assert region.stub(body) == body, f.name


def test_spec_survives_the_round_trip_on_every_file():
    for f in FILES:
        body, editor, spec_src = _parts(f.read_text())
        assert ast.get_docstring(region._solve(ast.parse(editor))) is None, f.name
        assert region.merge_spec(editor, spec_src) == body, f.name


def test_strip_spec_reports_the_docstring_it_removed():
    body, editor, spec_src = _parts()
    spec = region.strip_spec(body)
    assert spec.doc_offset == len(spec_src.split("\n"))
    assert len(editor.split("\n")) + spec.doc_offset == len(body.split("\n"))
    assert spec.spec_text == inspect.cleandoc(ast.literal_eval(spec_src.strip()))


def test_strip_spec_survives_a_solve_without_a_docstring():
    spec = region.strip_spec("def solve(x):\n    return x")
    assert spec.editor == "def solve(x):\n    return x"
    assert spec.spec_src is None and spec.doc_offset == 0
    assert region.merge_spec(spec.editor, spec.spec_src) == spec.editor


# ------------------------------------------------------------ merge edge cases
def test_merge_rejects_a_one_line_def():
    with pytest.raises(region.Invalid):
        region.merge_spec("def solve(x): return x", SPEC)


def test_merge_rejects_a_body_hiding_on_the_signature_line():
    with pytest.raises(region.Invalid):
        region.merge_spec("def solve(\n    x,\n): return x", SPEC)


def test_merge_accepts_a_two_space_body():
    out = region.merge_spec("def solve(x):\n  return x", SPEC)
    assert '\n  """WHY' in out and "\n  YOU RETURN" in out
    assert ast.get_docstring(region._solve(ast.parse(out))).startswith("WHY:")


def test_a_two_space_save_survives_a_second_save():
    """The spec goes back at the learner's own indentation, so the next save must
    not assume the pristine four spaces."""
    body, editor, spec_src = _parts()
    once = region.merge_spec(editor.replace("    raise NotImplementedError", "  return ''"), spec_src)
    again = region.strip_spec(once)
    assert again.spec_text == region.strip_spec(body).spec_text     # the spec text is unchanged
    assert region.merge_spec(again.editor, again.spec_src) == once  # and stable from here on


def test_merge_accepts_a_tab_body():
    out = region.merge_spec("def solve(x):\n\treturn x", SPEC)
    assert '\n\t"""WHY' in out
    assert ast.get_docstring(region._solve(ast.parse(out))).startswith("WHY:")


def test_merge_drops_a_pasted_docstring():
    out = region.merge_spec('def solve(x):\n    """stale copy."""\n    return x * 2', SPEC)
    assert "stale copy" not in out and out.count('"""') == 2
    assert out.endswith("    return x * 2")


def test_merge_rejects_a_body_that_is_only_a_pasted_docstring():
    with pytest.raises(region.Invalid):
        region.merge_spec('def solve(x):\n    """stale copy."""', SPEC)


def test_merge_accepts_a_comment_first_body():
    out = region.merge_spec("def solve(x):\n    # plan: double it\n    return x * 2", SPEC)
    assert "# plan: double it" in out
    assert ast.get_docstring(region._solve(ast.parse(out))).startswith("WHY:")


def test_merge_keeps_a_decorator_and_the_code_above_solve():
    out = region.merge_spec("import functools\n\n\n@functools.cache\ndef solve(x):\n    return x", SPEC)
    assert "@functools.cache" in out and out.startswith("import functools")
    assert ast.get_docstring(region._solve(ast.parse(out))).startswith("WHY:")


# ------------------------------------------------------------ the write gate
def test_validate_accepts_a_normal_edit():
    _, editor, spec_src = _parts()
    new = region.validate(editor.replace("raise NotImplementedError", "return ''"), spec_src, SRC)
    ast.parse(new)
    assert '"""WHY' in new and "def _reference(" in new and "return ''" in new
    assert new.split("\n")[:6] == SRC.split("\n")[:6]


def test_validate_reports_the_line_of_a_syntax_error():
    _, _, spec_src = _parts()
    with pytest.raises(region.Invalid) as e:
        region.validate("def solve(rows)\n    return ''", spec_src, SRC)
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
            region.validate(edited, spec_src, SRC)
        except region.Invalid:
            continue
        raise AssertionError(f"validate accepted {why}")


def test_validate_refuses_to_drop_the_docstring():
    with pytest.raises(region.Invalid):
        region.validate("def solve(rows):\n    return ''", None, SRC)


def test_stub_keeps_given_code():
    for name, needle in (("ex_036_env.py", "TRUTHY = {"), ("ex_044_customexc.py", "class ConfigError")):
        body = region.cut((settings.exercises_dir / name).read_text()).body
        stubbed = region.stub(body.replace("raise NotImplementedError", "return {}"))
        assert needle in stubbed and "return {}" not in stubbed
        assert stubbed.endswith("    raise NotImplementedError")
        assert ast.get_docstring(region._solve(ast.parse(stubbed))).startswith("WHY:")


def test_etag_tracks_only_the_learner_region():
    assert len(region.etag(SRC)) == 12
    assert region.etag(SRC) == region.etag(SRC.replace('"""f-string', '"""FSTRING'))
    assert region.etag(SRC) != region.etag(_solved())


def test_write_region_is_atomic_and_keeps_the_docstring():
    tmp = Path(tempfile.mkdtemp())
    try:
        path = tmp / "ex_001_fstrings.py"
        path.write_text(SRC)
        region.write_region(path, _solved())
        assert "return ''" in path.read_text() and '"""WHY' in path.read_text()
        assert not list(tmp.glob("*.tmp"))
        with pytest.raises(region.Invalid):
            region.write_region(path, region.splice(SRC, _parts()[1]))
        assert '"""WHY' in path.read_text()
    finally:
        shutil.rmtree(tmp)
