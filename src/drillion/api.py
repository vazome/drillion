"""JSON API over the task core, and the built page that drives it.

Every route is a plain `def` that touches progress.json inside a `state.writing()` or
`state.reading()` block: an `async def` blocking on that lock would freeze the whole
server, while FastAPI runs sync handlers in a threadpool."""

import logging
import shutil
import subprocess
import threading
import webbrowser
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.trustedhost import TrustedHostMiddleware

from . import __version__
from .attempts import (
    Gated,
    NoAttempt,
    abandon,
    attempt_view,
    current,
    next_hint,
    nudge_due,
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
from .scheduler import (
    LADDER,
    LAPSE_LIMIT,
    REVIEWS_PER_DAY,
    blocked,
    buried,
    due_today,
    pick,
    queue,
)
from .settings import settings
from .state import card, reading, today, writing

log = logging.getLogger(__name__)
MAX_BODY = 256 * 1024
WINDOW = 7  # days in the consistency window; the page reads it off the payload
FORECAST_DAYS = 14  # how far ahead the progress page looks

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


class Edit(BaseModel):
    code: str
    etag: str


class Etag(BaseModel):
    etag: str


class Focus(BaseModel):
    tag: str | None = None


class Bury(BaseModel):
    buried: bool = True


class Note(BaseModel):
    text: str


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


@app.middleware("http")
async def _limit_body(request, call_next):
    """Refuse an oversized body by its declared length; a chunked body is not measured here."""
    length = request.headers.get("content-length", "")
    if length.isdigit() and int(length) > MAX_BODY:
        return JSONResponse({"error": "that is more code than any task needs"}, 413)
    return await call_next(request)


# a container is reached through a published localhost port; Starlette ignores it
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"])


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
    # one rule, both answers: passing opens them, and while an attempt is open only the
    # deliberate peek does
    reveal = o["solution_shown"] if o else c["seen"] > 0 and c["due"] > today()
    return {
        "slug": slug,
        "meta": public(meta),
        "spec_md": meta["spec_md"],
        "code": body,
        "etag": etag(src),
        "has_given": has_given(body),
        "marker_line": bounds(src),
        "status": _status(st, slug),
        # not a fifth `status`: a buried card is still exactly `due`, just not offered today
        "buried": buried(st, slug),
        "lapses": c["lapses"],
        "lapse_limit": LAPSE_LIMIT,
        "ladder": LADDER,
        "note": st["notes"].get(slug, ""),
        "reference": solution_text(meta["path"]) if reveal else None,
        **att,
        "archive": [
            {
                "date": a["date"],
                "grade": a["grade"],
                **({"code": a["code"]} if reveal else {}),
            }
            for a in st["archive"].get(slug, [])
        ],
    }


def _practised(st):
    """Days worked in the last WINDOW, counted from the archive, so a day you gave up on
    still counts. A rolling window, never a streak."""
    cut = (date.fromisoformat(today()) - timedelta(days=WINDOW - 1)).isoformat()
    return len(
        {r["date"] for runs in st["archive"].values() for r in runs if r["date"] >= cut}
    )


def _recent(st, all_tasks):
    """Tasks worked in the last WINDOW days, most recent first — distinct slugs, no cap.

    An open attempt counts and sorts first; a slug whose latest run is `abandoned` drops off
    until it is opened or passed again."""
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


@app.get("/api/health")
def health():
    """Is the app up and pointed at the tasks? No lock, no state, no writes —
    a container health check must never queue behind a 60 s pytest run."""
    return {
        "status": "ok",
        "version": __version__,
        "tasks": len(tasks()),
        "root": str(settings.root),
    }


@app.get("/api/catalogue")
def catalogue():
    with reading() as st:  # card() only fills blanks; nothing commits
        all_tasks = tasks()
        q = queue(st, all_tasks)
        q["recent"] = _recent(st, all_tasks)
        held = blocked(st, all_tasks)
        # `text` is the spec flattened for the search box, deliberately outside
        # `public()`'s allowlist
        rows = [
            {
                "slug": slug,
                **public(m),
                "text": m["search_text"],
                "status": _status(st, slug),
                "buried": buried(st, slug),
                "blocked": held.get(slug, []),
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
                "ladder": LADDER,
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
        start = date.fromisoformat(today())
        week = (start + timedelta(days=6)).isoformat()
        forecast = [0] * FORECAST_DAYS
        per_tag = {}
        for slug, meta in all_tasks.items():
            c = card(st, slug)
            seen = c["seen"] > 0
            if seen:
                # today carries everything overdue, except what is buried: that is tomorrow's
                ahead = (date.fromisoformat(c["due"]) - start).days
                if ahead < FORECAST_DAYS:
                    forecast[max(ahead, 1 if buried(st, slug) else 0)] += 1
            for tag in meta["tags"]:
                t = per_tag.setdefault(
                    tag,
                    {
                        "seen": 0,
                        "total": 0,
                        "boxes": [0] * len(LADDER),
                        "lapses": 0,
                        "due7": 0,
                    },
                )
                t["total"] += 1
                if seen:
                    t["seen"] += 1
                    t["boxes"][c["box"]] += 1
                    t["lapses"] += c["lapses"]
                    t["due7"] += c["due"] <= week
        boxes = _boxes(st, all_tasks)
        return {
            "boxes": boxes,
            "ladder": LADDER,
            "due": len(due_today(st, all_tasks)),
            "seen": sum(boxes),
            "total": len(all_tasks),
            "practised": _practised(st),
            "window": WINDOW,
            "today": today(),
            "forecast": forecast,
            "cap": REVIEWS_PER_DAY,
            "days": dict(Counter(e["date"] for e in st["log"])),
            "log": st["log"][-30:],
            "per_tag": per_tag,
        }


@app.get("/api/task/{slug}")
def get_task(slug: str):
    with reading() as st:
        meta = _task(slug)
        return _payload(st, slug, meta, meta["path"].read_text())


@app.post("/api/task/{slug}/open")
def open_task(slug: str):
    with writing() as st:
        meta = _task(slug)
        open_attempt(st, slug)
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
        body = cut(new_src).body
        resp = {
            "passed": passed,
            "attempts": o["attempts"],
            **summarise(out, bounds(new_src)),
        }
        log.info("%s passed=%s attempts=%s", slug, passed, o["attempts"])
        if passed:
            was = card(st, slug)["box"]
            grade, gap, box, reason = record_pass(
                st, slug, meta, body
            )  # drops the attempt
            log.info("%s %s box=%s due in %sd (%s)", slug, grade, box, gap, reason)
            new_src = splice(new_src, stub(body))
            write_region(meta["path"], new_src)
            # `from_box` is the direction: `struggled` steps a card *down*
            resp |= {
                "grade": grade,
                "box": box,
                "stepped": box != was,
                "from_box": was,
                "reason": reason,
                "due_in": gap,
                "code": body,
                "reference": solution_text(meta["path"]),  # passing is what opens it
                "lapses": card(st, slug)["lapses"],
                # over a copy: `pick` reads every card, and `card()` fills blanks in place
                "next": pick({**st, "cards": dict(st["cards"])}, tasks())[0],
            }
        return resp | {"etag": etag(new_src)}


@app.post("/api/task/{slug}/touch")
def touch_task(slug: str):
    with writing() as st:  # no catalogue lookup: only a known slug can be open
        o = current(st, slug)
        return {"active": o["active"], "nudge": nudge_due(o)}


@app.post("/api/task/{slug}/hint")
def hint_task(slug: str):
    with writing() as st:
        meta = _task(slug)
        current(st, slug)
        try:
            next_hint(st, slug, meta["hints"])
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
        return _payload(st, slug, meta, meta["path"].read_text())


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
        # after `unlock_solution`, so `solution_shown` is set and the payload carries the answer
        return _payload(st, slug, meta, meta["path"].read_text())


@app.post("/api/task/{slug}/abandon")
def abandon_task(slug: str, sent: Etag):
    """Give up: keep the work in the archive, put the stub back, drop the timer.

    `current()` first, like every other acting route: `abandon()` stubs the source whether
    or not an attempt was open."""
    with writing() as st:
        meta = _task(slug)
        current(st, slug)
        src = meta["path"].read_text()
        _check_etag(src, sent.etag)
        new_src = abandon(st, slug, src)
        log.info("%s abandoned", slug)
        write_region(meta["path"], new_src)
        return _payload(st, slug, meta, new_src)


@app.post("/api/task/{slug}/bury")
def bury_task(slug: str, want: Bury):
    """Not today: the card keeps its box, its due date, its seen count and its lapses.
    Tomorrow un-buries it, and `{"buried": false}` is the same door, taken early."""
    with writing() as st:
        _task(slug)  # a slug that is not a task is a 404, not a card in progress.json
        card(st, slug)["buried"] = today() if want.buried else ""
        log.info("%s %s", slug, "buried" if want.buried else "unburied")
        return {"buried": buried(st, slug)}


@app.put("/api/task/{slug}/note")
def note_task(slug: str, note: Note):
    """What you want to remember about this task, in your words: one note, edited in place.

    It belongs to the task and not to the attempt, and needs no open attempt. Emptying the
    box is how you delete it."""
    with writing() as st:
        _task(slug)  # a slug that is not a task is a 404, not a key in progress.json
        text = note.text.strip()
        if text:
            st["notes"][slug] = text
        else:
            st["notes"].pop(slug, None)
        return {"note": text}


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
    # mounted after every /api route, so an unmatched /api/... 404s as JSON
    if settings.web_dist.is_dir():
        app.mount("/", StaticFiles(directory=settings.web_dist, html=True), name="web")
    url = f"http://{settings.host}:{settings.port}/"
    print(f"drillion → {url}   (ctrl-c to stop)", flush=True)  # piped output too
    if settings.open_browser and settings.host == "127.0.0.1":  # not from a container
        threading.Timer(0.7, _open_browser, [url]).start()
    uvicorn.run(app, host=settings.host, port=settings.port, log_level="info")
