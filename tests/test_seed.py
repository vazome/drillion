"""Seeding: a wheel arrives with the tasks, and the code the learner wrote survives it."""

import os
import shutil
import tempfile
from pathlib import Path

from drillion import cli, region
from drillion.settings import PKG, _data_home, _default_root, settings

REPO = Path(__file__).resolve().parent.parent


def _task(body, machinery="def _reference(xs):\n    return xs\n"):
    """A task file in the shape seeding cares about: a region, the marker, machinery."""
    return f"{body}\n\n\n{region.MARKER}\n\n{machinery}"


def _seeding(fn):
    """Run `fn(root, template)` with a two-task template standing in for the wheel's."""
    tmp, keep = Path(tempfile.mkdtemp(prefix="drillion_seed_")), settings.root
    packaged = cli.TASKS_TEMPLATE
    template, root = tmp / "template", tmp / "root"
    (template / "009_fstrings").mkdir(parents=True)
    (template / "009_fstrings" / "task.py").write_text("packaged\n", encoding="utf-8")
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
        assert (root / "tasks" / "009_fstrings" / "task.py").read_text(
            encoding="utf-8"
        ) == "packaged\n"
        assert (root / "tasks" / "_lib.py").is_file()

    _seeding(check)


def test_seeding_never_overwrites_saved_code():
    """The upgrade case: a task file under root holds whatever the learner last saved."""

    def check(root, _template):
        (root / "tasks" / "009_fstrings").mkdir(parents=True)
        (root / "tasks" / "009_fstrings" / "task.py").write_text(
            "mine\n", encoding="utf-8"
        )
        cli.seed()
        assert (root / "tasks" / "009_fstrings" / "task.py").read_text(
            encoding="utf-8"
        ) == "mine\n"

    _seeding(check)


def test_an_upgrade_reaches_a_root_that_was_already_seeded():
    """The reason this runs every time: a root seeded by an older drillion still gets the
    files that version never shipped."""

    def check(root, _template):
        (root / "tasks" / "009_fstrings").mkdir(parents=True)
        cli.seed()
        assert (root / "tasks" / "_lib.py").is_file()
        assert (root / "tasks" / "009_fstrings" / "task.py").is_file()

    _seeding(check)


def test_drillions_own_files_follow_the_installed_version():
    """Everything that is not task.py — READMEs, tests, `_lib.py` — is overwritten, so a
    rewritten prompt reaches a learner who is already using the task."""

    def check(root, template):
        (root / "tasks" / "009_fstrings").mkdir(parents=True)
        (root / "tasks" / "009_fstrings" / "README.md").write_text(
            "stale\n", encoding="utf-8"
        )
        (template / "009_fstrings" / "README.md").write_text(
            "current\n", encoding="utf-8"
        )
        cli.seed()
        assert (root / "tasks" / "009_fstrings" / "README.md").read_text(
            encoding="utf-8"
        ) == "current\n"

    _seeding(check)


def test_a_task_this_version_no_longer_ships_is_moved_aside_with_its_code():
    """Renumbering a task renames its folder. The old slug must leave the catalogue, but
    what the learner wrote for it is theirs and goes to `_retired/`."""

    def check(root, _template):
        cli.seed()  # the record of what this version ships
        gone = root / "tasks" / "001_fstrings"
        gone.mkdir(parents=True)
        (gone / "task.py").write_text("mine\n", encoding="utf-8")
        (root / "tasks" / cli.SHIPPED).write_text(
            "001_fstrings/task.py\n_lib.py\n", encoding="utf-8"
        )

        cli.seed()

        assert not gone.exists()
        assert (root / "tasks" / cli.RETIRED / "001_fstrings" / "task.py").read_text(
            encoding="utf-8"
        ) == "mine\n"
        assert (root / "tasks" / "009_fstrings").is_dir()

    _seeding(check)


def test_a_task_the_learner_added_is_left_alone():
    """Nothing drillion ever shipped is nothing drillion may take away."""

    def check(root, _template):
        cli.seed()
        mine = root / "tasks" / "500_mine"
        mine.mkdir(parents=True)
        (mine / "task.py").write_text("mine\n", encoding="utf-8")

        cli.seed()
        cli.seed()  # and still there on the run after that

        assert (mine / "task.py").read_text(encoding="utf-8") == "mine\n"
        assert not (root / "tasks" / cli.RETIRED).exists()

    _seeding(check)


def test_a_root_with_no_record_of_what_was_shipped_loses_nothing():
    """The first run after this record existed: there is nothing to compare against, so an
    upgrade prunes nothing and writes the record for next time."""

    def check(root, _template):
        older = root / "tasks" / "001_fstrings"
        older.mkdir(parents=True)
        (older / "task.py").write_text("mine\n", encoding="utf-8")

        cli.seed()

        assert (older / "task.py").is_file()
        assert (root / "tasks" / cli.SHIPPED).is_file()

    _seeding(check)


def test_a_file_this_version_dropped_from_a_task_it_still_ships_goes():
    def check(root, template):
        (template / "009_fstrings" / "README.md").write_text(
            "current\n", encoding="utf-8"
        )
        cli.seed()
        stale = root / "tasks" / "009_fstrings" / "test_extra.py"
        stale.write_text("old\n", encoding="utf-8")
        (root / "tasks" / cli.SHIPPED).write_text(
            "009_fstrings/task.py\n009_fstrings/test_extra.py\n", encoding="utf-8"
        )

        cli.seed()

        assert not stale.exists()
        assert (root / "tasks" / "009_fstrings" / "task.py").is_file()

    _seeding(check)


def test_an_upgrade_replaces_the_machinery_and_keeps_the_region():
    """The defect this exists to prevent: a task the learner has opened kept its old grader
    for good, so a fix to the machinery never reached anyone already practising it."""

    def check(root, template):
        (template / "009_fstrings" / "task.py").write_text(
            _task(
                "def solve(xs):\n    raise NotImplementedError",
                "def _reference(xs):\n    return 2\n",
            ),
            encoding="utf-8",
        )
        cli.seed()
        mine = root / "tasks" / "009_fstrings" / "task.py"
        mine.write_text(
            _task(
                "def solve(xs):\n    return 'mine'",
                "def _reference(xs):\n    return 1\n",
            ),
            encoding="utf-8",
        )

        cli.seed()

        text = mine.read_text(encoding="utf-8")
        assert "return 'mine'" in region.cut(text).body
        assert "return 2" in region.cut(text).tail

    _seeding(check)


def test_a_task_file_whose_region_no_longer_fits_is_kept_as_it_is():
    """Better a task that needs a hand than work overwritten by an upgrade."""

    def check(root, _template):
        cli.seed()
        mine = root / "tasks" / "009_fstrings" / "task.py"
        mine.write_text("whatever I did to this file\n", encoding="utf-8")

        cli.seed()

        assert mine.read_text(encoding="utf-8") == "whatever I did to this file\n"

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
