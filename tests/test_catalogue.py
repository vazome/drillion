"""Catalogue: the ast read of exercises/, READ FIRST blocks and given code."""

from study import catalogue, region
from study.settings import settings

FILES = sorted(settings.exercises_dir.glob("ex_*.py"))
SRC = (settings.exercises_dir / "ex_001_fstrings.py").read_text()


def test_exercises_reads_every_file_by_ast():
    exs = catalogue.exercises()
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
    assert catalogue.read_first(file.format("# READ FIRST:\n#   https://x\n#   https://y")) == [
        "READ FIRST:", "  https://x", "  https://y"]
    assert catalogue.read_first(file.format("# just a note")) == []     # only the READ FIRST block
    assert catalogue.read_first(file.format("import os")) == []
    assert catalogue.read_first(file.format(                                   # exercism attribution
        "# SOURCE: exercism/python practice/leap (MIT, adapted)\n# READ FIRST:\n#   https://x")) == [
        "READ FIRST:", "  https://x"]


def test_has_given_spots_code_above_solve():
    assert catalogue.has_given(region.cut((settings.exercises_dir / "ex_036_env.py").read_text()).body)
    assert not catalogue.has_given(region.cut(SRC).body)
