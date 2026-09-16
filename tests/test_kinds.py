"""The learner-artifact boundary: what a kind says about the learner's own text."""

from pathlib import Path

from drillion import kinds, region
from tests.fixtures import TASK

META = {"kind": "python", "dir": None}


def test_python_body_is_the_region_above_the_marker():
    k = kinds.of(META)
    assert k.name == "python" and k.filename == "task.py" and k.language == "python"
    assert k.body(TASK) == region.cut(TASK).body
    assert "_reference" not in k.body(TASK)


def test_python_compose_round_trips():
    k = kinds.of(META)
    assert k.compose(TASK, k.body(TASK)) == TASK


def test_python_empty_is_the_stub_not_an_empty_file():
    k = kinds.of(META)
    emptied = k.empty(TASK.replace("raise NotImplementedError", "return x"))
    assert "raise NotImplementedError" in emptied
    assert region.MARKER in emptied


def test_python_etag_ignores_the_machinery():
    k = kinds.of(META)
    moved = TASK.replace("return x", "return x  # changed")
    assert k.etag(TASK) != k.etag(moved.replace("def solve(x)", "def solve(y)"))
    assert k.etag(TASK) == region.etag(TASK)


def test_python_path_joins_the_task_dir_with_its_filename():
    meta = {"kind": "python", "dir": Path("/tasks/001_add")}
    assert kinds.of(meta).path(meta) == Path("/tasks/001_add/task.py")


def test_an_unknown_kind_raises_rather_than_guessing():
    try:
        kinds.of({"kind": "terraform"})
    except KeyError:
        return
    raise AssertionError("an unknown kind must not silently fall back to python")
