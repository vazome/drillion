"""Runner: pytest output turned into editor coordinates, and the selfcheck splice."""

import shutil

import pytest

from drillion import runner
from drillion.settings import settings

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
    """Positional-only, varargs, keyword-only and **kwargs each need a different spelling
    at the call site, and only keyword-only ones are passed by name."""
    every_kind = "def solve(a, /, b, *rest, c, **kw):\n    raise NotImplementedError\n"
    assert runner._reference_call(every_kind) == (
        "def solve(a, /, b, *rest, c, **kw):\n    return _reference(a, b, *rest, c=c, **kw)"
    )


def test_a_reference_call_replaces_a_written_body_not_just_the_raise():
    """The splice cuts at the *last* `raise NotImplementedError`, so setup work above it goes
    too — the reference answer is the whole implementation."""
    with_setup = "def solve(rows):\n    total = 0\n    raise NotImplementedError\n"
    assert runner._reference_call(with_setup) == (
        "def solve(rows):\n    return _reference(rows)"
    )


def test_the_output_panel_never_shows_terminal_escapes(tmp_path, monkeypatch):
    """`FORCE_COLOR` or `PY_COLORS` in the environment turns pytest's colour on whatever the
    tty is, and the escapes then reach the page as literal `[31mF[0m`."""
    monkeypatch.setenv("FORCE_COLOR", "1")
    task = tmp_path / "task.py"
    task.write_text("def test_solve():\n    assert 1 == 2\n", encoding="utf-8")
    passed, out = runner.run_tests(task, seed=1)
    assert passed is False
    assert "\x1b[" not in out, "terminal escapes reached the output panel"


def test_the_learners_code_cannot_litter_the_data_root(tmp_path, monkeypatch):
    """pytest runs in a scratch directory, so a stray `open(\"out.txt\", \"w\")` lands somewhere
    nobody minds losing rather than next to `progress.json`."""
    monkeypatch.setattr(settings, "root", tmp_path)
    task = tmp_path / "task.py"
    task.write_text(
        "from pathlib import Path\n"
        "def test_solve():\n"
        "    (Path.cwd() / 'litter.txt').write_text('x')\n",
        encoding="utf-8",
    )
    passed, out = runner.run_tests(task, seed=1)
    assert passed, out  # the write itself succeeded
    assert not list(tmp_path.rglob("litter.txt"))


def test_a_warning_in_the_learners_code_is_not_a_failure(tmp_path, monkeypatch):
    """drillion's own pyproject turns warnings into errors, and in a checkout pytest walks
    up from the task and adopts it. The grader pins an empty config so a learner is graded
    on their assertion, never on a `DeprecationWarning` from the library they were told to
    use."""
    monkeypatch.setattr(settings, "root", tmp_path)
    (tmp_path / "pyproject.toml").write_text(
        "[tool.pytest.ini_options]\nfilterwarnings = ['error']\n"
    )
    task = tmp_path / "task.py"
    task.write_text(
        "import warnings\n"
        "def test_solve():\n"
        "    warnings.warn('old api', DeprecationWarning)\n"
        "    assert True\n"
    )
    passed, out = runner.run_tests(task, seed=1)
    assert passed, out


def test_a_failure_names_the_task_the_short_way(tmp_path, monkeypatch):
    """The scratch cwd sits inside the data root, so pytest reports the task relative to it
    and the output panel never shows a host path."""
    monkeypatch.setattr(settings, "root", tmp_path)
    task = tmp_path / "tasks" / "001_fstrings" / "task.py"
    task.parent.mkdir(parents=True)
    task.write_text("def test_solve():\n    assert 1 == 2\n", encoding="utf-8")
    _, out = runner.run_tests(task, seed=1)
    text = runner.summarise(out, marker_line=1)["output"]
    assert "../tasks/001_fstrings/task.py" in text
    assert "task.py" not in text.replace("../tasks/001_fstrings/task.py", ""), text


def test_selfcheck_solves_each_task_with_its_own_reference(
    tmp_path, monkeypatch, capsys
):
    """A scratch root of two real tasks, not all 171: each is spliced to call `_reference`,
    every splice is cleaned up, and a task that fails comes back named."""
    source = settings.tasks_dir
    monkeypatch.setattr(settings, "root", tmp_path)
    (tmp_path / "tasks").mkdir()
    shutil.copy(source / "_lib.py", tmp_path / "tasks" / "_lib.py")
    for slug in ("001_fstrings", "002_slicing"):
        shutil.copytree(source / slug, tmp_path / "tasks" / slug)

    assert runner.selfcheck() == 0
    assert "2/2 ok" in capsys.readouterr().out
    assert not list(tmp_path.rglob("_selfcheck.py"))

    task = tmp_path / "tasks" / "001_fstrings" / "task.py"
    task.write_text(
        task.read_text(encoding="utf-8") + "\n\ndef test_broken():\n    assert False\n",
        encoding="utf-8",
    )
    assert runner.selfcheck() == 1
    assert "FAILED 001_fstrings" in capsys.readouterr().out


WINDOWS_OUT = (
    "..\\tasks\\001_fstrings\\task.py:9: AssertionError\n"
    "=========================== short test summary info ===========================\n"
    "FAILED ..\\tasks\\001_fstrings\\task.py::test_solve - assert 1 == 2\n"
)


def test_a_windows_path_reaches_the_panel_the_same_way_a_posix_one_does():
    """pytest prints the platform separator; the panel speaks `/` on every platform."""
    text = runner.summarise(WINDOWS_OUT, marker_line=1)["output"]
    assert "../tasks/001_fstrings/task.py:9" in text
    assert "\\" not in text


def test_a_learners_own_backslashes_survive_the_panel():
    """The panel carries the learner's failed assertion, escapes and all."""
    out = "E   AssertionError: assert 'a\\nb' == re.compile(r'\\d+')\n"
    assert runner.summarise(out, marker_line=1)["output"] == out


@pytest.mark.parametrize("sep", ["/", "\\"])
def test_a_failed_line_names_the_task_folder_and_nothing_else(sep):
    """The slug, not the `FAILED ` in front of it and not the path around it."""
    line = f"FAILED ..{sep}tasks{sep}001_fstrings{sep}_selfcheck.py::test_solve - boom"
    collected = f"ERROR ..{sep}tasks{sep}002_slicing{sep}_selfcheck.py"
    noise = "FAILED some/other/thing.py::test_x - not ours"
    assert runner._failed_slugs(f"{line}\n{collected}\n{noise}\n") == [
        "001_fstrings",
        "002_slicing",
    ]
