"""The ways in: serve the tasks in a browser, or check the whole set still works.

    drillion             open the web UI
    drillion selfcheck   solve every task with its own _reference
    drillion doctor      say why a task folder would be skipped
    drillion --version   the installed version, the same one /api/health reports

Every command starts by seeding an empty root from the tasks the wheel carries, so an
install with no checkout anywhere near it still has something to practise.

This is the only module that imports the web layer, and it does so lazily: a
selfcheck must not need a server to run.
"""

import argparse
import logging
import shutil

from . import __version__
from .settings import TASKS_TEMPLATE, settings

log = logging.getLogger(__name__)


def seed():
    """Fill an empty root from the tasks baked into the wheel, once.

    The tasks are not read-only content: `region.write_region()` rewrites task.py on every
    save and `runner.selfcheck()` writes into every task folder, so they cannot be practised
    where pip put them. The wheel carries a pristine template instead and the first run copies
    it somewhere writable — `settings.root`, which installed means a per-user data directory
    and in a container means the mounted volume.

    A root that already has `tasks/` is left completely alone: that is a checkout, or a
    learner's own copy with their code saved inside the task files, and an upgrade that wrote
    over it would eat their work. A checkout has no template at all, so this is a no-op there
    twice over.
    """
    # ponytail: tasks added by a later drillion never reach an already-seeded root.
    # Fill in only the missing folders if that starts to matter.
    if settings.tasks_dir.is_dir() or not TASKS_TEMPLATE.is_dir():
        return
    log.info(
        "first run: seeding %s from the tasks that ship with drillion", settings.root
    )
    shutil.copytree(TASKS_TEMPLATE, settings.tasks_dir)


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="drillion", description="Spaced-repetition Python tasks."
    )
    ap.add_argument("--version", action="version", version=f"drillion {__version__}")
    ap.add_argument(
        "command",
        nargs="?",
        default="serve",
        choices=("serve", "selfcheck", "doctor"),
        help="serve the web UI (default), solve every task with its reference, "
        "or report why a task folder would be skipped",
    )
    args = ap.parse_args(argv)
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    seed()
    if not settings.tasks_dir.is_dir():
        raise SystemExit(
            f"no tasks/ under {settings.root} — run drillion from the repo, "
            f"or point DRILLION_ROOT at the directory that holds it"
        )
    if args.command == "doctor":
        from .doctor import doctor

        raise SystemExit(1 if doctor() else 0)
    if args.command == "selfcheck":
        from .runner import selfcheck

        raise SystemExit(1 if selfcheck() else 0)
    from .api import serve

    serve()
