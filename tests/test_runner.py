"""Runner: pytest output turned into editor coordinates."""

from study import runner

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
    out = runner.summarise(CANNED, region_start=9, doc_offset=28, hints_line=41)
    assert out["headline"] == ["E       NotImplementedError"]
    assert "line 2: NotImplementedError" in out["output"]          # the learner's raise
    assert "exercises/ex_001_fstrings.py:78:" in out["output"]     # the test frame stays put


def test_summarise_falls_back_to_the_failed_line_and_caps_the_headline():
    only_failed = "FAILED exercises/ex_001_fstrings.py::test_solve - boom\n"
    assert runner.summarise(only_failed, 9, 28, 41)["headline"] == [only_failed.strip()]
    noisy = "\n".join(f"E   line {i}" for i in range(9))
    assert len(runner.summarise(noisy, 9, 28, 41)["headline"]) == 6
