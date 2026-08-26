"""Runner: pytest output turned into editor coordinates."""

from drillion import runner

CANNED = """\
=================================== FAILURES ===================================
__________________________________ test_solve __________________________________

    def test_solve():
>       assert solve(list(rows)) == _reference(rows)

tasks/001_fstrings/task.py:24:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

>       raise NotImplementedError
E       NotImplementedError

tasks/001_fstrings/task.py:2: NotImplementedError
=========================== short test summary info ============================
FAILED tasks/001_fstrings/task.py::test_solve - NotImplementedError
"""


def test_summarise_maps_the_region_to_editor_lines():
    out = runner.summarise(CANNED, marker_line=5)
    assert out["headline"] == ["E       NotImplementedError"]
    assert "line 2: NotImplementedError" in out["output"]  # the learner's raise
    assert "tasks/001_fstrings/task.py:24:" in out["output"]  # the test frame stays put


def test_summarise_falls_back_to_the_failed_line_and_caps_the_headline():
    only_failed = "FAILED tasks/001_fstrings/task.py::test_solve - boom\n"
    assert runner.summarise(only_failed, 5)["headline"] == [only_failed.strip()]
    noisy = "\n".join(f"E   line {i}" for i in range(9))
    assert len(runner.summarise(noisy, 5)["headline"]) == 6
