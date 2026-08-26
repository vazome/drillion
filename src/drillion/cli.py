"""The ways in: serve the tasks in a browser, or check the whole set still works.

    drillion             open the web UI
    drillion selfcheck   solve every task with its own _reference
    drillion doctor      say why a task folder would be skipped

This is the only module that imports the web layer, and it does so lazily: a
selfcheck must not need a server to run.
"""

import argparse
import logging

from .settings import settings


def main(argv=None):
    ap = argparse.ArgumentParser(prog="drillion", description="Spaced-repetition Python tasks.")
    ap.add_argument("command", nargs="?", default="serve",
                    choices=("serve", "selfcheck", "doctor"),
                    help="serve the web UI (default), solve every task with its reference, "
                         "or report why a task folder would be skipped")
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    if not settings.tasks_dir.is_dir():
        raise SystemExit(f"no tasks/ under {settings.root} — run drillion from the repo, "
                         f"or point DRILLION_ROOT at the directory that holds it")
    if args.command == "doctor":
        from .doctor import doctor
        raise SystemExit(1 if doctor() else 0)
    if args.command == "selfcheck":
        from .runner import selfcheck
        raise SystemExit(1 if selfcheck() else 0)
    from .api import serve
    serve()
