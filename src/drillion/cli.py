"""The ways in: serve the tasks in a browser, or check the whole set still works."""

import argparse
import io
import logging
import shutil
import subprocess
import sys
import threading
import webbrowser
from pathlib import Path

from . import __version__
from .settings import TASKS_TEMPLATE, settings

log = logging.getLogger(__name__)


def seed():
    """Bring root's tasks/ in line with the tasks baked into the wheel, on every run.

    `task.py` is the learner's — it is never written over. Everything else under tasks/ is
    drillion's, so READMEs, `_lib.py` and the test files follow the installed version, new
    tasks arrive on upgrade, and a task this version no longer ships is removed rather than
    left as a slug nothing links to. A checkout has no template and is untouched."""
    if not TASKS_TEMPLATE.is_dir():
        return
    dest = settings.tasks_dir
    if not dest.is_dir():
        log.info("first run: seeding %s from the tasks that ship with drillion", dest)
    dest.mkdir(parents=True, exist_ok=True)
    for src in TASKS_TEMPLATE.rglob("*"):
        out = dest / src.relative_to(TASKS_TEMPLATE)
        if src.is_dir():
            out.mkdir(parents=True, exist_ok=True)
        elif not (out.name == "task.py" and out.is_file()):
            shutil.copy2(src, out)
    # deepest first, so a directory is empty by the time its own turn comes
    for out in sorted(dest.rglob("*"), reverse=True):
        if (TASKS_TEMPLATE / out.relative_to(dest)).exists():
            continue
        if out.is_dir():
            shutil.rmtree(out, ignore_errors=True)
        else:
            out.unlink(missing_ok=True)


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

    class Revalidated(StaticFiles):
        """The built page, always revalidated. The bundler reuses one filename for the
        entry chunk however much its contents changed, so a browser that has ever loaded
        drillion holds `assets/index-<name>.js` under whatever freshness it invented for a
        response that carried no `cache-control` — and serves yesterday's app after an
        upgrade. `no-cache` is revalidate-before-use, not don't-store: the ETag already
        here answers 304 in a few bytes."""

        def file_response(self, *args, **kwargs):
            resp = super().file_response(*args, **kwargs)
            resp.headers["cache-control"] = "no-cache"
            return resp

    build_web()
    # mounted after every /api route, so an unmatched /api/... 404s as JSON
    if settings.web_dist.is_dir():
        app.mount("/", Revalidated(directory=settings.web_dist, html=True), name="web")
    url = f"http://{settings.host}:{settings.port}/"
    print(f"drillion → {url}   (ctrl-c to stop)", flush=True)  # piped output too
    if settings.open_browser and settings.host == "127.0.0.1":  # not from a container
        threading.Timer(0.7, _open_browser, [url]).start()
    uvicorn.run(app, host=settings.host, port=settings.port, log_level="info")


def main(argv=None):
    # everything we print is UTF-8; a redirected stdout is locale-encoded on Windows
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            stream.reconfigure(encoding="utf-8")
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
