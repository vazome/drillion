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

from . import __version__, region
from .settings import TASKS_TEMPLATE, settings

log = logging.getLogger(__name__)


SHIPPED = ".shipped"
RETIRED = "_retired"


def _merge(packaged, out):
    """Take the version's machinery, keep whatever the learner has in the region.

    A file whose region no longer fits the new machinery — a signature that moved, a task
    the learner has edited outside the region — is left exactly as it is and named in the
    log, because a broken task is recoverable and overwritten work is not."""
    current = out.read_text(encoding="utf-8")
    try:
        merged = region.validate(
            region.cut(current).body, packaged.read_text(encoding="utf-8")
        )
    except region.Invalid as exc:
        log.warning("kept %s as it is: %s", out, exc)
        return
    if merged != current:
        region.write_region(out, merged)


def _retire(dest, shipped):
    """Take back what drillion used to ship and no longer does, and nothing else.

    `.shipped` is the record of what the last run put here, so a task the learner wrote
    themselves is never in it and is never touched. A task drillion has dropped keeps the
    code written for it: the folder moves under `_retired/`, which the catalogue skips,
    rather than being deleted. A root seeded before this record existed has nothing to
    compare against, so it loses nothing and gets the record for next time."""
    manifest = dest / SHIPPED
    if not manifest.is_file():
        return
    gone = [
        rel
        for rel in manifest.read_text(encoding="utf-8").split()
        if rel not in shipped
    ]
    slugs = {rel.split("/")[0] for rel in shipped}
    for rel in gone:
        folder = rel.split("/")[0]
        if "/" in rel and folder not in slugs:
            _move_aside(dest / folder, dest / RETIRED / folder)
        else:
            (dest / rel).unlink(missing_ok=True)
    for rel in gone:
        parent = (dest / rel).parent
        if parent != dest and parent.is_dir() and not any(parent.iterdir()):
            parent.rmdir()


def _move_aside(folder, out):
    if not folder.is_dir():
        return  # already moved, or never arrived
    if out.exists():
        log.warning(
            "%s is no longer shipped, and %s is taken: left where it is", folder, out
        )
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(folder), str(out))
    log.info(
        "%s is no longer shipped; what you wrote for it is at %s", folder.name, out
    )


def seed():
    """Bring root's tasks/ in line with the tasks baked into the wheel, on every run.

    Everything under tasks/ is drillion's except the learner's region inside each
    `task.py`, so READMEs, `_lib.py` and the test files follow the installed version, a
    task file gets this version's machinery spliced around the code the learner wrote, and
    new tasks arrive on upgrade. A task drillion no longer ships is moved aside rather than
    deleted, and a task the learner added themselves is left alone. A checkout has no
    template and is untouched."""
    if not TASKS_TEMPLATE.is_dir():
        return
    dest = settings.tasks_dir
    if not dest.is_dir():
        log.info("first run: seeding %s from the tasks that ship with drillion", dest)
    dest.mkdir(parents=True, exist_ok=True)
    shipped = []
    for src in sorted(TASKS_TEMPLATE.rglob("*")):
        rel = src.relative_to(TASKS_TEMPLATE)
        out = dest / rel
        if src.is_dir():
            out.mkdir(parents=True, exist_ok=True)
            continue
        shipped.append(rel.as_posix())
        if out.name == "task.py" and out.is_file():
            _merge(src, out)
        else:
            shutil.copy2(src, out)
    _retire(dest, set(shipped))
    (dest / SHIPPED).write_text("\n".join(shipped) + "\n", encoding="utf-8")


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
