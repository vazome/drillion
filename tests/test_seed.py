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
    (template / "001_fstrings").mkdir(parents=True)
    (template / "001_fstrings" / "task.py").write_text("packaged\n")
    (template / "_lib.py").write_text("packaged lib\n")
    try:
        settings.root = root
        cli.TASKS_TEMPLATE = template
        fn(root, template)
    finally:
        settings.root = keep
        cli.TASKS_TEMPLATE = packaged
        shutil.rmtree(tmp)


def test_an_empty_root_is_seeded_from_the_package():
    """`uvx drillion` in a directory with no tasks/: the catalogue is empty until this
    puts the packaged copy somewhere the learner can write to."""

    def check(root, _template):
        cli.seed()
        assert (root / "tasks" / "001_fstrings" / "task.py").read_text() == "packaged\n"
        assert (root / "tasks" / "_lib.py").is_file()

    _seeding(check)


def test_seeding_never_overwrites_saved_code():
    """The upgrade case, and the one that could destroy real work: a task file already
    under root holds whatever the learner last saved into it."""

    def check(root, _template):
        (root / "tasks" / "001_fstrings").mkdir(parents=True)
        (root / "tasks" / "001_fstrings" / "task.py").write_text("mine\n")
        cli.seed()
        assert (root / "tasks" / "001_fstrings" / "task.py").read_text() == "mine\n"

    _seeding(check)


def test_a_root_that_has_tasks_is_left_alone():
    """Nothing is added either — not `_lib.py`, not a folder only the package has.
    A root with tasks/ is a checkout or somebody's own copy, and seeding stays out."""

    def check(root, _template):
        (root / "tasks" / "001_fstrings").mkdir(parents=True)
        before = sorted(p.relative_to(root) for p in root.rglob("*"))
        cli.seed()
        assert sorted(p.relative_to(root) for p in root.rglob("*")) == before

    _seeding(check)


def test_a_checkout_seeds_nothing():
    """Running from the repo must be byte-for-byte what it always was. There is no
    template in a checkout — it exists only inside a built wheel — so seed() returns
    before it can look at tasks/ at all."""
    assert not (REPO / "src" / "drillion" / "_tasks").exists()
    if os.environ.get("DRILLION_ROOT"):
        return  # somebody pointed the root elsewhere: nothing to say about the checkout
    assert Path(_default_root()).resolve() == REPO


def test_an_install_keeps_progress_out_of_site_packages():
    """With no checkout and no tasks/ in sight, the fallback root is a per-user directory
    the learner can write to — never under the package, which is where the old fallback
    pointed and where months of progress.json must never end up."""
    home = _data_home()
    assert home.name == "drillion" and home.is_absolute()
    assert not home.is_relative_to(PKG)
