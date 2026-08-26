"""JSON API over the task core, and the built page that drives it.

Every route is a plain `def`. Each one that touches progress.json opens a
`state.writing()` (or `state.reading()`) block, which holds the lock and is the
only place the file is committed; an `async def` blocking on that lock would
freeze the whole server while a 60 s pytest run held it, and FastAPI runs sync
handlers in a threadpool, where blocking is what threads are for.

Nothing here re-implements a rule: `region` owns validation and the splice,
`scheduler` and `attempts` own grading, and the task files are read as text
and run as a subprocess — the server never imports them. The browser only ever
sees the region above the marker, so `_reference`, `_gen` and the tests cannot
leak into it, and the guidance it renders comes from the task's README.md.
"""

import logging
import shutil
import subprocess
import threading
import webbrowser
from datetime import date, timedelta
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .attempts import (
    Gated,
    NoAttempt,
    abandon,
    attempt_view,
    current,
    next_hint,
    open_attempt,
    record_pass,
    solution_text,
    unlock_solution,
)
from .catalogue import public, tasks
from .region import (
    Invalid,
    bounds,
    cut,
    etag,
    has_given,
    splice,
    stub,
    validate,
    write_region,
)
from .runner import run_tests, summarise
from .scheduler import LADDER, LAPSE_LIMIT, due_today, queue
from .settings import settings
from .state import card, reading, today, writing

log = logging.getLogger(__name__)
MAX_BODY = 256 * 1024
WINDOW = 7  # days in the consistency window; the page reads it off the payload

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


class Edit(BaseModel):
    code: str
    etag: str


class Etag(BaseModel):
    etag: str


class Focus(BaseModel):
    tag: str | None = None


# ---------------------------------------------------------------- errors
@app.exception_handler(Invalid)
async def _rejected(_request, exc):
    """A refused edit is the learner's problem, not a crash: 400 with coordinates."""
    return JSONResponse({"error": exc.msg, "line": exc.line, "col": exc.col}, 400)


@app.exception_handler(NoAttempt)
async def _no_attempt(_request, _exc):
    """Acting on a task nobody opened: the learner's problem, not a crash."""
    return JSONResponse({"error": "no open attempt — open the task first"}, 409)


@app.exception_handler(StarletteHTTPException)
async def _error(_request, exc):
    """One error shape for the page: {"error": ...} plus whatever the case adds."""
    body = exc.detail if isinstance(exc.detail, dict) else {"error": exc.detail}
    return JSONResponse(body, exc.status_code, headers=exc.headers)


# ---------------------------------------------------------------- middleware
@app.middleware("http")
async def _limit_body(request, call_next):
    # ponytail: a chunked body carries no length and slips past; the only client
    # is our own page, and uvicorn already caps headers.
    length = request.headers.get("content-length", "")
    if length.isdigit() and int(length) > MAX_BODY:
        return JSONResponse({"error": "that is more code than any task needs"}, 413)
    return await call_next(request)


# a container is reached through a published localhost port; Starlette ignores it
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"])


# ---------------------------------------------------------------- helpers
def _task(slug):
    """The catalogue entry for `slug` — a slug never becomes a path any other way."""
    all_tasks = tasks()
    if slug not in all_tasks:
        raise HTTPException(404, f"no task {slug!r}")
    return all_tasks[slug]


def _check_etag(src, sent):
    """Optimistic lock: the editor may only write what it last read."""
    if sent != etag(src):
        raise HTTPException(
            409,
            {
                "error": "the file changed on disk",
                "etag": etag(src),
                "code": cut(src).body,
            },
        )


def _status(st, slug):
    c = card(st, slug)
    if slug in st["open"]:
        return "open"
    if not c["seen"]:
        return "new"
    return "due" if c["due"] <= today() else "done"


def _payload(st, slug, meta, src):
    """Everything the task page needs, and nothing the answer lives in."""
    body = cut(src).body
    o = st["open"].get(slug)
    c = card(st, slug)
    att = attempt_view(o, meta["hints"])
    # a due review must not be handed last time's answer; a locked attempt neither
    show_code = c["seen"] > 0 and (
        att["solution"]["unlocked"] if o else c["due"] > today()
    )
    return {
        "slug": slug,
        "meta": public(meta),
        "spec_md": meta["spec_md"],
        "code": body,
        "etag": etag(src),
        "has_given": has_given(body),
        "region_start": 1,
        "marker_line": bounds(src),
        "status": _status(st, slug),
        "lapses": c["lapses"],
        "lapse_limit": LAPSE_LIMIT,
        **att,
        "archive": [
            {
                "date": a["date"],
                "grade": a["grade"],
                **({"code": a["code"]} if show_code else {}),
            }
            for a in st["archive"].get(slug, [])
        ],
    }


def _practised(st):
    """Days worked in the last WINDOW, counted from the archive — which holds a row
    for every pass and every abandoned attempt that got anywhere, so a hard day you
    gave up on still counts. A rolling window, never a streak: one missed day costs one point and
    repairs itself, and nothing here rewards filling all seven (Lally 2010: a single
    missed occasion does not derail a forming habit)."""
    cut = (date.fromisoformat(today()) - timedelta(days=WINDOW - 1)).isoformat()
    return len(
        {r["date"] for runs in st["archive"].values() for r in runs if r["date"] >= cut}
    )


def _recent(st, all_tasks):
    """Tasks worked in the last WINDOW days, most recent first — the way back into whatever
    you were just doing. Distinct slugs and no cap: what makes it recent is the window, not a
    count. Read from the archive for the same reason `_practised` is: it holds the days you
    gave up on as well as the days you passed.

    An attempt still open counts, and counts first: nothing reaches the archive until a pass or
    an abandon, so a task you are in the middle of right now is exactly the work this list exists
    to lead you back to. Its `last` touch is a full timestamp, so today's work orders within the
    day; an archived run only knows its date, and sorts as the start of that day.

    Giving up is the way out. A slug whose latest run is `abandoned` drops off — abandoning is
    the explicit "put this back", and a list that keeps offering it has no exit. Opening it again
    brings it back, and so does a later pass. (`_practised` still counts the day: you showed up.)

    Nothing is held back for being in today's queue. A card worked on Friday and due again
    today is both things at once, and the queue is not the authority on what you were doing."""
    cut = (date.fromisoformat(today()) - timedelta(days=WINDOW - 1)).isoformat()
    last = {
        slug: runs[-1]["date"]
        for slug, runs in st["archive"].items()
        if runs[-1].get("grade") != "abandoned"
    }
    for slug, o in st["open"].items():
        last[slug] = max(last.get(slug, ""), o["last"])
    return sorted(
        (
            s for s, d in last.items() if s in all_tasks and d >= cut
        ),  # a rename leaves a dead key
        key=lambda s: last[s],
        reverse=True,
    )


def _boxes(st, all_tasks):
    boxes = [0] * len(LADDER)
    for slug in all_tasks:
        c = card(st, slug)
        if c["seen"]:
            boxes[c["box"]] += 1
    return boxes


# ---------------------------------------------------------------- read-only routes
@app.get("/api/health")
def health():
    """Is the app up and pointed at the tasks? No lock, no state, no writes —
    a container health check must never queue behind a 60 s pytest run."""
    return {"status": "ok", "tasks": len(tasks()), "root": str(settings.root)}


@app.get("/api/catalogue")
def catalogue():
    with reading() as st:  # card() only fills blanks; nothing commits
        all_tasks = tasks()
        q = queue(st, all_tasks)
        q["recent"] = _recent(st, all_tasks)
        # `text` is the spec flattened for the search box (#14) — the same prose the
        # task page already shows, so nothing leaks. Deliberately outside `public()`'s
        # allowlist, because GET /api/task ships the real spec_md instead.
        rows = [
            {
                "slug": slug,
                **public(m),
                "text": m["search_text"],
                "status": _status(st, slug),
                **{k: card(st, slug)[k] for k in ("box", "due", "seen", "lapses")},
            }
            for slug, m in all_tasks.items()
        ]
        boxes = _boxes(st, all_tasks)
        return {
            "focus": st["focus"],
            "tags": sorted({t for m in all_tasks.values() for t in m["tags"]}),
            "tiers": ["core", "advanced", "packages"],  # fixed order: easiest first
            "tracks": sorted(
                {m["track"] for m in all_tasks.values() if m.get("track")}
            ),
            "today": q,
            "stats": {
                "boxes": boxes,
                "due": q["due_total"],
                "seen": sum(boxes),
                "total": len(all_tasks),
                "practised": _practised(st),
                "window": WINDOW,
                "lapse_limit": LAPSE_LIMIT,
            },
            "tasks": rows,
        }


@app.get("/api/progress")
def progress():
    with reading() as st:
        all_tasks = tasks()
        per_tag = {}
        for slug, meta in all_tasks.items():
            seen = card(st, slug)["seen"] > 0
            for tag in meta["tags"]:
                t = per_tag.setdefault(tag, {"seen": 0, "total": 0})
                t["total"], t["seen"] = t["total"] + 1, t["seen"] + seen
        boxes = _boxes(st, all_tasks)
        return {
            "boxes": boxes,
            "due": len(due_today(st, all_tasks)),
            "seen": sum(boxes),
            "total": len(all_tasks),
            "practised": _practised(st),
            "window": WINDOW,
            "log": st["log"][-30:],
            "per_tag": per_tag,
        }


@app.get("/api/task/{slug}")
def get_task(slug: str):
    with reading() as st:
        meta = _task(slug)
        return _payload(st, slug, meta, meta["path"].read_text())


# ---------------------------------------------------------------- the attempt
@app.post("/api/task/{slug}/open")
def open_task(slug: str):
    with writing() as st:
        meta = _task(slug)
        open_attempt(st, slug)  # the file is already a stub: nothing is written
        return _payload(st, slug, meta, meta["path"].read_text())


@app.put("/api/task/{slug}")
def save_task(slug: str, edit: Edit):
    with reading() as st:  # autosave: the file only, no timer, no commit
        meta = _task(slug)
        if slug not in st["open"]:  # a closed task is a stub; keep it one
            raise NoAttempt(slug)
        src = meta["path"].read_text()
        _check_etag(src, edit.etag)
        new_src = validate(edit.code, src)
        write_region(meta["path"], new_src)
        return {"etag": etag(new_src)}


@app.post("/api/task/{slug}/run")
def run_task(slug: str, edit: Edit):
    """Save, then run. A rejected save is a 400 and costs no attempt."""
    with writing() as st:
        meta = _task(slug)
        o = current(st, slug)
        src = meta["path"].read_text()
        _check_etag(src, edit.etag)
        new_src = validate(edit.code, src)
        write_region(meta["path"], new_src)
        passed, out = run_tests(meta["path"], o["seed"])
        o["attempts"] += 1  # pytest ran; that is what an attempt is
        code = body = cut(new_src).body
        resp = {
            "passed": passed,
            "attempts": o["attempts"],
            **summarise(out, bounds(new_src)),
        }
        log.info("%s passed=%s attempts=%s", slug, passed, o["attempts"])
        if passed:
            # Whether the card actually moved is the scheduler's fact, not the page's to
            # infer: `struggled` and a `quick` at the top box both clamp, and an unseen
            # card already sits in box 0. The page renders this; it does not recompute it.
            was = card(st, slug)["box"]
            grade, gap, box = record_pass(st, slug, meta, code)  # drops the attempt
            log.info("%s %s box=%s due in %sd", slug, grade, box, gap)
            new_src = splice(new_src, stub(body))
            write_region(meta["path"], new_src)  # back to the stub
            resp |= {
                "grade": grade,
                "box": box,
                "stepped": box != was,
                "due_in": gap,
                "code": code,
                "lapses": card(st, slug)["lapses"],
            }  # the page reads lapse_limit off /task
        return resp | {"etag": etag(new_src)}


@app.post("/api/task/{slug}/touch")
def touch_task(slug: str):
    with writing() as st:  # no catalogue lookup: this runs every 60 s and
        return {
            "active": current(st, slug)["active"]
        }  # only an opened — known — slug is open


@app.post("/api/task/{slug}/hint")
def hint_task(slug: str):
    with writing() as st:
        meta = _task(slug)
        current(st, slug)
        try:
            level, text = next_hint(st, slug, meta["hints"])
        except Gated as gate:
            raise HTTPException(
                423,
                {
                    "error": "not yet — sit with it a little longer"
                    if gate.wait_secs
                    else "no hints left — the solution is the next step",
                    "wait_secs": gate.wait_secs,
                    "exhausted": not gate.wait_secs,
                },
            ) from None
        return {"level": level, "total": len(meta["hints"]), "text": text}


@app.post("/api/task/{slug}/solution")
def solution_task(slug: str):
    with writing() as st:
        meta = _task(slug)
        current(st, slug)
        try:
            unlock_solution(st, slug)
        except Gated as gate:
            raise HTTPException(
                423, {"error": "the answer opens after real effort", **gate.owed}
            ) from None
        return {"code": solution_text(meta["path"])}  # the gate is right above


@app.post("/api/task/{slug}/abandon")
def abandon_task(slug: str, sent: Etag):
    """Give up: keep the work in the archive, put the stub back, drop the timer."""
    with writing() as st:
        meta = _task(slug)
        src = meta["path"].read_text()
        _check_etag(src, sent.etag)
        new_src = abandon(st, slug, src)
        log.info("%s abandoned", slug)
        write_region(meta["path"], new_src)
        return _payload(st, slug, meta, new_src)


@app.get("/api/task/{slug}/assets/{name}")
def asset(slug: str, name: str):
    """An image, diagram or clip the README points at. A name, never a path."""
    folder = _task(slug)["dir"]
    path = folder / "assets" / name
    if "/" in name or "\\" in name or ".." in name or not path.is_file():
        raise HTTPException(404, f"no asset {name!r}")
    return FileResponse(path)


@app.post("/api/focus")
def set_focus(focus: Focus):
    with writing() as st:
        st["focus"] = focus.tag
        return {"focus": st["focus"]}


class _Web(StaticFiles):
    """web/dist, resolved per request and optional.

    `check_dir=False` only skips the constructor's check: Starlette still stats the directory
    on the first request and raises `RuntimeError` if it is missing. A clone that has not run
    `pnpm build` yet — CI between `pytest` and the web job, or a machine without pnpm — must
    get a 404 on `/`, not a 500 on every unmatched route. CI runs pytest before the web build,
    so it is the standing guard against this coming back."""

    async def check_config(self):
        return


# The page itself, last: an unmatched /api/... must 404 as JSON, not as a missing file.
# Mounted rather than resolved at import, so `serve()` may build web/dist after this module loads.
app.mount(
    "/", _Web(directory=settings.web_dist, html=True, check_dir=False), name="web"
)


def _open_browser(url):
    version = Path("/proc/version")
    if version.exists() and "microsoft" in version.read_text().lower():
        subprocess.Popen(["explorer.exe", url])  # WSL: exit code 1 even when it worked
    else:
        webbrowser.open(url)


def build_web():
    """Build web/dist when it is missing or older than its sources.

    web/dist is generated, so it is git-ignored: a fresh clone has none, and `drillion`
    is supposed to just work. Without pnpm the API still serves; only `/` is missing.
    """
    web = settings.web_dist.parent
    if not (web / "package.json").is_file():
        return
    watched = [
        web / "package.json",
        web / "index.html",
        web / "vite.config.ts",
        *(web / "src").rglob("*"),
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
    build_web()
    url = f"http://{settings.host}:{settings.port}/"
    print(f"drillion → {url}   (ctrl-c to stop)", flush=True)  # piped output too
    if settings.open_browser and settings.host == "127.0.0.1":  # not from a container
        threading.Timer(0.7, _open_browser, [url]).start()
    uvicorn.run(app, host=settings.host, port=settings.port, log_level="info")
