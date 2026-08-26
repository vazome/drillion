"""Runner: pytest output turned into editor coordinates, and the selfcheck splice."""

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


def test_a_reference_call_rebuilds_every_kind_of_parameter():
    """`drillion selfcheck` is the gate that keeps 171 authored tasks honest, and this hand-built
    call is the whole of it: it reads solve()'s own signature and wires it to `_reference`. Get one
    parameter kind wrong and selfcheck reports *every* task as failing — at which point someone
    goes and "fixes" the tasks. Positional-only, varargs, keyword-only and **kwargs each need a
    different spelling at the call site, and only keyword-only ones are passed by name."""
    every_kind = "def solve(a, /, b, *rest, c, **kw):\n    raise NotImplementedError\n"
    assert runner._reference_call(every_kind) == (
        "def solve(a, /, b, *rest, c, **kw):\n    return _reference(a, b, *rest, c=c, **kw)"
    )


def test_a_reference_call_replaces_a_written_body_not_just_the_raise():
    """The splice cuts at the *last* `raise NotImplementedError`, so a task whose stub does
    setup work above it keeps none of that — the reference answer is the whole implementation."""
    with_setup = "def solve(rows):\n    total = 0\n    raise NotImplementedError\n"
    assert runner._reference_call(with_setup) == (
        "def solve(rows):\n    return _reference(rows)"
    )


def test_the_output_panel_never_shows_terminal_escapes(tmp_path, monkeypatch):
    """pytest does not decide colour by asking whether it is a tty — `FORCE_COLOR` or
    `PY_COLORS` in the environment turns it on regardless, and a pnpm script sets `FORCE_COLOR`
    for everything it spawns. The escapes then reach the page as literal `[31mF[0m` all through
    the failure output, which is the one place a learner actually has to read."""
    monkeypatch.setenv("FORCE_COLOR", "1")
    task = tmp_path / "task.py"
    task.write_text("def test_solve():\n    assert 1 == 2\n")
    passed, out = runner.run_tests(task, seed=1)
    assert passed is False
    assert "\x1b[" not in out, "terminal escapes reached the output panel"
