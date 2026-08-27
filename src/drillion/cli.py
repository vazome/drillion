"""The ways in: serve the tasks in a browser, or check the whole set still works."""

import argparse
import logging
import shutil
import subprocess
import threading
import webbrowser
from pathlib import Path

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


def _open_browser(url):
    version = Path("/proc/version")
    if version.exists() and "microsoft" in version.read_text().lower():
        subprocess.Popen(["explorer.exe", url])  # WSL: exit code 1 even when it worked
    else:
        webbrowser.open(url)


def build_web():
    """Build web/dist when it is missing or older than its sources. Without pnpm the API
    still serves; only `/` is missing."""
    web = settings.web_dist.parent
    if not (web / "package.json").is_file():
        return
    watched = [
        web / "package.json",
        web / "index.html",
        web / "vite.config.ts",
        *(web / "src").rglob("*"),
        *(web / "public").rglob("*"),
    ]
    newest = max((p.stat().st_mtime for p in watched if p.is_file()), default=0)
    built = settings.web_dist / "index.html"
    if built.is_file() and built.stat().st_mtime >= newest:
        return
    if shutil.which("pnpm") is None:
        log.warning(
            "web/dist is stale and pnpm is not installed — the API runs, / will 404"
        )
        return
    log.info("building web/dist (first run, or the frontend changed)")
    for cmd in (["pnpm", "install", "--frozen-lockfile"], ["pnpm", "build"]):
        if subprocess.run(cmd, cwd=web, check=False).returncode:
            log.warning("`%s` failed — the API runs, / will 404", " ".join(cmd))
            return


def serve():
    import uvicorn
    from fastapi.staticfiles import StaticFiles

    from .api import app

    build_web()
    # mounted after every /api route, so an unmatched /api/... 404s as JSON
    if settings.web_dist.is_dir():
        app.mount("/", StaticFiles(directory=settings.web_dist, html=True), name="web")
    url = f"http://{settings.host}:{settings.port}/"
    print(f"drillion → {url}   (ctrl-c to stop)", flush=True)  # piped output too
    if settings.open_browser and settings.host == "127.0.0.1":  # not from a container
        threading.Timer(0.7, _open_browser, [url]).start()
    uvicorn.run(app, host=settings.host, port=settings.port, log_level="info")


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
    serve()
