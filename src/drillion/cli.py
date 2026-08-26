"""The ways in: serve the tasks in a browser, or check the whole set still works."""

import argparse
import logging
import shutil

from . import __version__
from .settings import TASKS_TEMPLATE, settings

log = logging.getLogger(__name__)


def seed():
    """Fill an empty root from the tasks baked into the wheel, once.

    A root that already has `tasks/` is left alone: it is a checkout, or a learner's own
    copy with their code saved inside the task files. Tasks added by a later drillion never
    reach a root that was already seeded."""
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
