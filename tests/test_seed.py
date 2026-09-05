"""Seeding: a wheel arrives with the tasks, and a root that has them is never written over."""

import os
import shutil
import tempfile
from pathlib import Path

from drillion import cli
from drillion.settings import PKG, _data_home, _default_root, settings

REPO = Path(__file__).resolve().parent.parent


def _seeding(fn):
    """Run `fn(root, template)` with a two-task template standing in for the wheel's."""
    tmp, keep = Path(tempfile.mkdtemp(prefix="drillion_seed_")), settings.root
    packaged = cli.TASKS_TEMPLATE
    template, root = tmp / "template", tmp / "root"
    (template / "017_fstrings").mkdir(parents=True)
    (template / "017_fstrings" / "task.py").write_text("packaged\n", encoding="utf-8")
    (template / "_lib.py").write_text("packaged lib\n", encoding="utf-8")
    try:
        settings.root = root
        cli.TASKS_TEMPLATE = template
        fn(root, template)
    finally:
        settings.root = keep
        cli.TASKS_TEMPLATE = packaged
        shutil.rmtree(tmp)


def test_an_empty_root_is_seeded_from_the_package():
    """`uvx drillion` where there is no tasks/: the packaged copy lands somewhere writable."""

    def check(root, _template):
        cli.seed()
        assert (root / "tasks" / "017_fstrings" / "task.py").read_text(
            encoding="utf-8"
        ) == "packaged\n"
        assert (root / "tasks" / "_lib.py").is_file()

    _seeding(check)


def test_seeding_never_overwrites_saved_code():
    """The upgrade case: a task file under root holds whatever the learner last saved."""

    def check(root, _template):
        (root / "tasks" / "017_fstrings").mkdir(parents=True)
        (root / "tasks" / "017_fstrings" / "task.py").write_text(
            "mine\n", encoding="utf-8"
        )
        cli.seed()
        assert (root / "tasks" / "017_fstrings" / "task.py").read_text(
            encoding="utf-8"
        ) == "mine\n"

    _seeding(check)


def test_a_root_that_has_tasks_is_left_alone():
    """Nothing is added either — not `_lib.py`, not a folder only the package has."""

    def check(root, _template):
        (root / "tasks" / "017_fstrings").mkdir(parents=True)
        before = sorted(p.relative_to(root) for p in root.rglob("*"))
        cli.seed()
        assert sorted(p.relative_to(root) for p in root.rglob("*")) == before

    _seeding(check)


def test_a_checkout_seeds_nothing():
    """A checkout has no template — it exists only inside a built wheel — so seed() returns
    before it looks at tasks/ at all."""
    assert not (REPO / "src" / "drillion" / "_tasks").exists()
    if os.environ.get("DRILLION_ROOT"):
        return  # somebody pointed the root elsewhere: nothing to say about the checkout
    assert Path(_default_root()).resolve() == REPO


def test_an_install_keeps_progress_out_of_site_packages():
    """With no checkout and no tasks/ in sight, the fallback root is a writable per-user
    directory, never one under the package."""
    home = _data_home()
    assert home.name == "drillion" and home.is_absolute()
    assert not home.is_relative_to(PKG)
