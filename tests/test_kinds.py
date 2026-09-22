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


def test_path_is_the_catalogues():
    meta = {"kind": "python", "path": Path("/tasks/001_add/task.py")}
    assert kinds.of(meta).path(meta) == meta["path"]


def test_an_unknown_kind_raises_rather_than_guessing():
    try:
        kinds.of({"kind": "terraform"})
    except KeyError:
        return
    raise AssertionError("an unknown kind must not silently fall back to python")


MANIFEST_META = {"kind": "manifest", "dir": None}
DEPLOY = "apiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: checkout\n"


def test_manifest_body_is_the_whole_file():
    k = kinds.of(MANIFEST_META)
    assert k.name == "manifest" and k.filename == "task.yaml" and k.language == "yaml"
    assert k.body(DEPLOY) == DEPLOY
    assert k.compose(DEPLOY, "other: 1\n") == "other: 1\n"


def test_manifest_empty_is_an_empty_file():
    assert kinds.of(MANIFEST_META).empty(DEPLOY) == ""


def test_manifest_etag_covers_every_byte():
    k = kinds.of(MANIFEST_META)
    assert k.etag(DEPLOY) != k.etag(DEPLOY + "\n")


def test_manifest_validate_accepts_a_draft_and_rejects_broken_yaml():
    k = kinds.of(MANIFEST_META)
    assert k.validate(DEPLOY, "") == DEPLOY
    assert (
        k.validate("", "") == ""
    )  # an unfinished draft saves; grading rejects it later
    try:
        k.validate("a:\n  - b\n c: broken\n", "")
    except kinds.Invalid as err:
        assert err.line
        return
    raise AssertionError("broken YAML must be rejected on save")
