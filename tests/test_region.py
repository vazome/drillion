"""Region: the marker split, the stub and the write gate.

Plain functions, no fixtures. The expensive ones sweep every drill: splice and
stub must be exactly reversible or a save would corrupt a drill.
"""

import ast
import shutil
import tempfile
from pathlib import Path

import pytest

from drillion import region, state
from drillion.settings import settings

FILES = sorted(settings.exercises_dir.glob("*/drill.py"))
SRC = (settings.exercises_dir / "001_fstrings" / "drill.py").read_text()


def _solved(src=SRC, code="return ''"):
    """`src` with the region's `raise` replaced by real code."""
    return region.splice(src, region.cut(src).body.replace("raise NotImplementedError", code))


# ------------------------------------------------------------ region: all files
def test_the_marker_opens_the_machinery_of_every_drill():
    assert len(FILES) >= 104
    for f in FILES:
        src = f.read_text()
        line = region.bounds(src)
        assert src.split("\n")[line - 1] == region.MARKER, f.parent.name


def test_splice_puts_every_file_back_exactly():
    for f in FILES:
        src = f.read_text()
        assert region.splice(src, region.cut(src).body) == src, f.parent.name


def test_the_region_holds_solve_and_the_tail_holds_the_machinery():
    for f in FILES:
        body, tail = region.cut(f.read_text())
        assert region._solve(ast.parse(body)) is not None, f.parent.name
        assert "def _reference(" in tail and "_reference" not in body, f.parent.name
        assert "from _lib import rng" in tail, f.parent.name


def test_stub_is_identity_on_pristine_files():
    drafts = set(state.load()["open"])           # an open attempt means the file holds live work
    for f in FILES:
        if f.parent.name in drafts:
            continue
        body = region.cut(f.read_text()).body
        assert region.stub(body) == body, f.parent.name


# ------------------------------------------------------------ stub
def test_stub_keeps_given_code_and_decorators():
    for name, needle in (("036_env", "TRUTHY = {"), ("044_customexc", "class ConfigError"),
                         ("098_fixtures", "@pytest.fixture")):
        body = region.cut((settings.exercises_dir / name / "drill.py").read_text()).body
        stubbed = region.stub(body.replace("raise NotImplementedError", "return {}"))
        assert needle in stubbed and "return {}" not in stubbed, name
        assert stubbed.endswith("    raise NotImplementedError"), name


def test_stub_refuses_a_one_line_body():
    with pytest.raises(region.Invalid):
        region.stub("def solve(x): return x")


def test_has_given_spots_code_above_solve():
    assert region.has_given(region.cut(
        (settings.exercises_dir / "036_env" / "drill.py").read_text()).body)
    assert not region.has_given(region.cut(SRC).body)


# ------------------------------------------------------------ the write gate
def test_validate_accepts_a_normal_edit():
    new = region.validate(region.cut(SRC).body.replace("raise NotImplementedError",
                                                       "return ''"), SRC)
    ast.parse(new)
    assert "def _reference(" in new and "return ''" in new
    assert new.split("\n")[region.bounds(new) - 1] == region.MARKER


def test_validate_accepts_a_learner_docstring():
    """The spec lives in README.md now, so a docstring is just code."""
    new = region.validate('def solve(rows):\n    """mine."""\n    return 1', SRC)
    assert '"""mine."""' in new


def test_validate_reports_the_line_of_a_syntax_error():
    with pytest.raises(region.Invalid) as e:
        region.validate("def solve(rows)\n    return ''", SRC)
    assert e.value.line == 1


def test_validate_rejects_bad_regions():
    bad = {
        "empty": "   \n",
        "no solve": "def helper(x):\n    return x",
        "two solves": "def solve(x):\n    return x\n\n\ndef solve(y):\n    return y",
        "machinery": "def _reference(rows):\n    return ''\n\n\ndef solve(rows):\n    return ''",
        "generator": "def _gen(r):\n    return 1\n\n\ndef solve(rows):\n    return ''",
        "test": "def test_x():\n    pass\n\n\ndef solve(rows):\n    return ''",
        "peeking": "def solve(rows):\n    return _reference(rows)",
        "one-liner": "def solve(rows): return ''",
        "the marker itself": f"def solve(rows):\n    return ''\n\n\n{region.MARKER}\nx = 1",
    }
    for why, edited in bad.items():
        try:
            region.validate(edited, SRC)
        except region.Invalid:
            continue
        raise AssertionError(f"validate accepted {why}")


def test_etag_tracks_only_the_learner_region():
    assert len(region.etag(SRC)) == 12
    assert region.etag(SRC) == region.etag(SRC.replace("def _reference", "def _reference  "))
    assert region.etag(SRC) != region.etag(_solved())


def test_write_region_is_atomic():
    tmp = Path(tempfile.mkdtemp())
    try:
        path = tmp / "drill.py"
        path.write_text(SRC)
        region.write_region(path, _solved())
        assert "return ''" in path.read_text()
        assert not list(tmp.glob("*.tmp"))
    finally:
        shutil.rmtree(tmp)
