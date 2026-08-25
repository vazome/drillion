"""JSON API over the drill core, and the built page that drives it.

Every route is a plain `def`. They all touch the disk under one lock, and an
`async def` blocking on a `threading.Lock` would freeze the whole server while
a 60 s pytest run held it; FastAPI runs sync handlers in a threadpool, where
blocking is what threads are for.

Nothing here re-implements a rule: `region` owns validation and the splice,
`scheduler` and `attempts` own grading, and the exercise files are read as text
and run as a subprocess — the server never imports them. The browser only ever
sees the editor half of the region, so `_reference`, `_gen` and the tests cannot
leak into it.
"""

import logging
import subprocess
import threading
import webbrowser
from datetime import date
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .attempts import (
    HINT_GAP,
    SOLUTION_GATE,
    Gated,
    _solution,
    abandon,
    next_hint,
    open_attempt,
    record_pass,
    touch,
    unlock_solution,
)
from .catalogue import exercises, has_given
from .region import (
    Invalid,
    bounds,
    cut,
    etag,
    splice,
    strip_spec,
    stub,
    validate,
    write_region,
)
from .runner import run_tests, summarise
from .scheduler import INTERVIEW, LADDER, due_today, queue
from .settings import settings
from .state import card, load, save, today

log = logging.getLogger(__name__)
MAX_BODY = 256 * 1024
LOCK = threading.Lock()      # read → validate → write → save() is one transaction
CATALOGUE_ONLY = ("path", "hints", "read_first", "hints_line", "region_start")  # never shipped

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
        return JSONResponse({"error": "that is more code than any drill needs"}, 413)
    return await call_next(request)


# a container is reached through a published localhost port; Starlette ignores it
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"])


# ---------------------------------------------------------------- helpers
def _exercise(slug):
    """The catalogue entry for `slug` — a slug never becomes a path any other way."""
    exs = exercises()
    if slug not in exs:
        raise HTTPException(404, f"no exercise {slug!r}")
    return exs[slug]


def _attempt(st, slug):
    """The open attempt, its timer wound on. The core would raise KeyError."""
    if slug not in st["open"]:
        raise HTTPException(409, "no open attempt — open the exercise first")
    o = st["open"][slug]
    touch(o)
    return o


def _check_etag(src, sent):
    """Optimistic lock: the editor may only write what it last read."""
    if sent != etag(src):
        raise HTTPException(409, {"error": "the file changed on disk",
                                  "etag": etag(src),
                                  "code": strip_spec(cut(src).body).editor})


def _coords(src):
    """(region_start, doc_offset, hints_line) of the file as it is *now* — pytest
    reports line numbers in the file it just ran, not the one we first parsed."""
    meta_end, hints_line = bounds(src)
    region = cut(src)
    return (meta_end + 1 + region.lead.count("\n"),
            strip_spec(region.body).doc_offset, hints_line)


def _gate(o):
    """(unlocked, attempts still owed, active seconds still owed) — pure, unlike
    `unlock_solution`, which marks the attempt as peeked."""
    attempts, secs = SOLUTION_GATE
    if o is None:
        return False, attempts, secs
    return (o["solution_shown"] or (o["attempts"] >= attempts and o["active"] >= secs),
            max(0, attempts - o["attempts"]), max(0, secs - o["active"]))


def _next_hint_in(o, total):
    """Seconds until the next hint; 0 if it is ready, None if there is none."""
    if o is None or o["hints"] >= total:
        return None
    return max(0, HINT_GAP * (o["hints"] + 1) - o["active"]) if o["hints"] else 0


def _status(st, slug):
    c = card(st, slug)
    if slug in st["open"]:
        return "open"
    if not c["seen"]:
        return "new"
    return "due" if c["due"] <= today() else "done"


def _payload(st, slug, meta, src):
    """Everything the exercise page needs, and nothing the answer lives in."""
    region = cut(src)
    spec = strip_spec(region.body)
    o = st["open"].get(slug)
    c = card(st, slug)
    region_start, _, hints_line = _coords(src)
    unlocked, need_attempts, need_secs = _gate(o)
    # a due review must not be handed last time's answer; a locked attempt neither
    show_code = c["seen"] > 0 and (unlocked if o else c["due"] > today())
    return {"slug": slug,
            "meta": {k: v for k, v in meta.items() if k not in CATALOGUE_ONLY},
            "spec": spec.spec_text,
            "read_first": meta["read_first"],
            "code": spec.editor,
            "etag": etag(src),
            "has_given": has_given(region.body),
            "doc_offset": spec.doc_offset,
            "region_start": region_start,
            "hints_line": hints_line,
            "status": _status(st, slug),
            "attempt": {k: o[k] for k in ("attempts", "hints", "active", "seed",
                                          "solution_shown")} if o else None,
            "hints": {"total": len(meta["hints"]),
                      "shown": meta["hints"][:o["hints"]] if o else [],
                      "next_in": _next_hint_in(o, len(meta["hints"]))},
            "solution": {"unlocked": unlocked, "need_attempts": need_attempts,
                         "need_secs": need_secs},
            "archive": [{"date": a["date"], "grade": a["grade"],
                         **({"code": a["code"]} if show_code else {})}
                        for a in st["archive"].get(slug, [])]}


def _boxes(st, exs):
    boxes = [0] * len(LADDER)
    for slug in exs:
        c = card(st, slug)
        if c["seen"]:
            boxes[c["box"]] += 1
    return boxes


# ---------------------------------------------------------------- read-only routes
@app.get("/api/health")
def health():
    """Is the app up and pointed at the drills? No lock, no state, no writes —
    a container health check must never queue behind a 60 s pytest run."""
    return {"status": "ok", "exercises": len(exercises()), "root": str(settings.root)}


@app.get("/api/catalogue")
def catalogue():
    with LOCK:                                   # GETs never save(): card() only fills blanks
        st, exs = load(), exercises()
        q = queue(st, exs)
        rows = [{"slug": slug, "topic": m["topic"], "title": m["title"],
                 "minutes": m["minutes"], "tags": m["tags"], "prereqs": m.get("prereqs", []),
                 "practices": m.get("practices", []), "status": _status(st, slug),
                 **{k: card(st, slug)[k] for k in ("box", "due", "seen")}}
                for slug, m in exs.items()]
        boxes = _boxes(st, exs)
        left = (INTERVIEW - date.fromisoformat(today())).days
        return {"focus": st["focus"],
                "tags": sorted({t for m in exs.values() for t in m["tags"]}),
                "today": q,
                "stats": {"boxes": boxes, "due": len(q["review"]), "seen": sum(boxes),
                          "total": len(exs), "days_left": left},
                "exercises": rows}


@app.get("/api/progress")
def progress():
    with LOCK:
        st, exs = load(), exercises()
        per_tag = {}
        for slug, meta in exs.items():
            seen = card(st, slug)["seen"] > 0
            for tag in meta["tags"]:
                t = per_tag.setdefault(tag, {"seen": 0, "total": 0})
                t["total"], t["seen"] = t["total"] + 1, t["seen"] + seen
        boxes = _boxes(st, exs)
        return {"boxes": boxes, "due": len(due_today(st, exs)), "seen": sum(boxes),
                "total": len(exs), "log": st["log"][-30:], "per_tag": per_tag}


@app.get("/api/ex/{slug}")
def get_exercise(slug: str):
    with LOCK:
        meta = _exercise(slug)
        return _payload(load(), slug, meta, meta["path"].read_text())


# ---------------------------------------------------------------- the attempt
@app.post("/api/ex/{slug}/open")
def open_exercise(slug: str):
    with LOCK:
        meta = _exercise(slug)
        st = load()
        open_attempt(st, slug)                   # the file is already a stub: nothing is written
        save(st)
        return _payload(st, slug, meta, meta["path"].read_text())


@app.put("/api/ex/{slug}")
def save_exercise(slug: str, edit: Edit):
    with LOCK:                                   # autosave: the file only, no timer, no save()
        meta = _exercise(slug)
        if slug not in load()["open"]:           # a closed exercise is a stub; keep it one
            raise HTTPException(409, "no open attempt — open the exercise first")
        src = meta["path"].read_text()
        _check_etag(src, edit.etag)
        new_src = validate(edit.code, strip_spec(cut(src).body).spec_src, src)
        write_region(meta["path"], new_src)
        return {"etag": etag(new_src)}


@app.post("/api/ex/{slug}/run")
def run_exercise(slug: str, edit: Edit):
    """Save, then run. A rejected save is a 400 and costs no attempt."""
    with LOCK:
        meta = _exercise(slug)
        st = load()
        o = _attempt(st, slug)
        src = meta["path"].read_text()
        _check_etag(src, edit.etag)
        new_src = validate(edit.code, strip_spec(cut(src).body).spec_src, src)
        write_region(meta["path"], new_src)
        passed, out = run_tests(meta["path"], o["seed"])
        o["attempts"] += 1                       # pytest ran; that is what an attempt is
        body = cut(new_src).body
        code = strip_spec(body).editor
        resp = {"passed": passed, "attempts": o["attempts"],
                **summarise(out, *_coords(new_src))}
        log.info("%s passed=%s attempts=%s", slug, passed, o["attempts"])
        if passed:
            grade, gap, box = record_pass(st, slug, meta, code)     # drops the attempt
            log.info("%s %s box=%s due in %sd", slug, grade, box, gap)
            new_src = splice(new_src, stub(body))
            write_region(meta["path"], new_src)                     # back to the stub
            resp |= {"grade": grade, "box": box, "due_in": gap, "code": code}
        save(st)
        return resp | {"etag": etag(new_src)}


@app.post("/api/ex/{slug}/touch")
def touch_exercise(slug: str):
    with LOCK:                                   # no catalogue lookup: this runs every 60 s and
        st = load()                              # only an opened — known — slug can be in `open`
        active = _attempt(st, slug)["active"]
        save(st)
        return {"active": active}


@app.post("/api/ex/{slug}/hint")
def hint_exercise(slug: str):
    with LOCK:
        meta = _exercise(slug)
        st = load()
        _attempt(st, slug)
        try:
            level, text = next_hint(st, slug, meta["hints"])
        except Gated as gate:
            raise HTTPException(423, {
                "error": "not yet — sit with it a little longer" if gate.wait_secs
                         else "no hints left — the solution is the next step",
                "wait_secs": gate.wait_secs, "exhausted": not gate.wait_secs}) from None
        save(st)
        return {"level": level, "total": len(meta["hints"]), "text": text}


@app.post("/api/ex/{slug}/solution")
def solution_exercise(slug: str):
    with LOCK:
        meta = _exercise(slug)
        st = load()
        o = _attempt(st, slug)
        if not unlock_solution(st, slug):
            _, need_attempts, need_secs = _gate(o)
            raise HTTPException(423, {"error": "the answer opens after real effort",
                                      "need_attempts": need_attempts, "need_secs": need_secs})
        save(st)
        return {"code": _solution(meta["path"])}       # the gate is right above


@app.post("/api/ex/{slug}/abandon")
def abandon_exercise(slug: str, sent: Etag):
    """Give up: keep the work in the archive, put the stub back, drop the timer."""
    with LOCK:
        meta = _exercise(slug)
        st = load()
        src = meta["path"].read_text()
        _check_etag(src, sent.etag)
        new_src = abandon(st, slug, src)
        log.info("%s abandoned", slug)
        write_region(meta["path"], new_src)
        save(st)
        return _payload(st, slug, meta, new_src)


@app.post("/api/focus")
def set_focus(focus: Focus):
    with LOCK:
        st = load()
        st["focus"] = focus.tag
        save(st)
        return {"focus": st["focus"]}


# The page itself, last: an unmatched /api/... must 404 as JSON, not as a missing file.
if settings.web_dist.is_dir():                # built by the frontend build; the API runs without it
    app.mount("/", StaticFiles(directory=settings.web_dist, html=True), name="web")


def _open_browser(url):
    version = Path("/proc/version")
    if version.exists() and "microsoft" in version.read_text().lower():
        subprocess.Popen(["explorer.exe", url])   # WSL: exit code 1 even when it worked
    else:
        webbrowser.open(url)


def serve():
    url = f"http://{settings.host}:{settings.port}/"
    print(f"study → {url}   (ctrl-c to stop)", flush=True)   # piped output too
    if settings.open_browser and settings.host == "127.0.0.1":   # not from a container
        threading.Timer(0.7, _open_browser, [url]).start()
    uvicorn.run(app, host=settings.host, port=settings.port, log_level="info")
