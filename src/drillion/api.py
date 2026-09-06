"""JSON API over the task core, and the built page that drives it.

Every route is a plain `def` that touches progress.json inside a `state.writing()` or
`state.reading()` block: an `async def` blocking on that lock would freeze the whole
server, while FastAPI runs sync handlers in a threadpool."""

import logging
from collections import Counter
from datetime import date, timedelta

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.responses import FileResponse, JSONResponse
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
from .lsp import bridge
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
    WINDOW,
    blocked,
    buried,
    by_tag,
    forecast,
    pick,
    queue,
    stats,
    stuck,
)
from .settings import settings
from .state import TooNew, card, own, reading, today, writing

log = logging.getLogger(__name__)
MAX_BODY = 256 * 1024

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


class Edit(BaseModel):
    code: str
    etag: str
    # a plain Run executes the tests and grades nothing; only a Submit costs an attempt
    submit: bool = True


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
    """A refused edit is the learner's problem, not a crash: 400 with the line."""
    return JSONResponse({"error": exc.msg, "line": exc.line}, 400)


@app.exception_handler(TooNew)
async def _too_new(_request, exc):
    """A progress file from a newer drillion: say so on the page, do not 500 the log."""
    return JSONResponse({"error": str(exc)}, 409)


@app.exception_handler(NoAttempt)
async def _no_attempt(_request, _exc):
    """Acting on a task nobody opened: the learner's problem, not a crash."""
    return JSONResponse({"error": "no open attempt — open the task first"}, 409)


@app.exception_handler(StarletteHTTPException)
async def _error(_request, exc):
    """One error shape for the page: {"error": ...} plus whatever the case adds."""
    body = exc.detail if isinstance(exc.detail, dict) else {"error": exc.detail}
    return JSONResponse(body, exc.status_code, headers=exc.headers)


def _allowed_origins():
    """The page this server itself serves, on the two hosts TrustedHostMiddleware admits.

    Read per request rather than frozen at import: the port is configurable, and an origin
    carries it."""
    return {f"http://{host}:{settings.port}" for host in ("127.0.0.1", "localhost")}


@app.middleware("http")
async def _same_origin(request, call_next):
    """Refuse the write a foreign page provoked: a browser attaches `Origin` to a cross-site
    request, and curl and the container healthcheck attach none, so absent stays allowed.
    `"null"` is what a sandboxed iframe sends — a string, not absent, and never trusted."""
    origin = request.headers.get("origin")
    if origin is not None and origin not in _allowed_origins():
        return JSONResponse({"error": "cross-origin request refused"}, 403)
    return await call_next(request)


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


def _deps(st, all_tasks, meta):
    """Prereq edges resolved against the ladder: what this task requires, and the one hop
    it unlocks.

    `passed` is box 1 — the same bar `blocked()` uses, and not the same thing as a `done`
    status once a card has lapsed back down."""
    by_topic = {m["topic"]: (s, m) for s, m in all_tasks.items()}

    def ref(slug, m, **extra):
        # `tags` so a node can say which corner of Python it is, the way a catalogue row does
        return {
            "slug": slug,
            "topic": m["topic"],
            "title": m["title"],
            "tags": m.get("tags", []),
            **extra,
        }

    requires = []
    for topic in meta.get("prereqs", ()):
        if topic in by_topic:
            slug, m = by_topic[topic]
            box = card(st, slug)["box"]
            state = "passed" if box >= 1 else "blocked"
            requires.append(ref(slug, m, state=state, box=box))
    # `also` is what else still gates that task: passing this one is not always enough,
    # and a node that says so is the difference between a graph and a decoration
    unlocks = []
    for slug, m in all_tasks.items():
        prereqs = m.get("prereqs", ())
        if meta["topic"] in prereqs:
            also = [p for p in prereqs if p != meta["topic"] and p in by_topic]
            unlocks.append(ref(slug, m, also=also))
    return {"requires": requires, "unlocks": unlocks}


def _payload(st, slug, meta, src):
    """Everything the task page needs, and nothing the answer lives in."""
    body = cut(src).body
    o = st["open"].get(slug)
    c = card(st, slug)
    att = attempt_view(o, meta["hints"])
    status = _status(st, slug)
    # one rule, both answers: passing opens them, and while an attempt is open only the
    # deliberate peek does
    reveal = o["solution_shown"] if o else status == "done"
    return {
        "slug": slug,
        "meta": public(meta),
        "spec_md": meta["spec_md"],
        "code": body,
        "etag": etag(src),
        "has_given": has_given(body),
        "status": status,
        # not a fifth `status`: a buried card is still exactly `due`, just not offered today
        "buried": buried(st, slug),
        "seen": c["seen"],
        "box": c["box"],
        "lapses": c["lapses"],
        "lapse_limit": LAPSE_LIMIT,
        **_deps(st, tasks(), meta),
        "ladder": LADDER,
        "note": st["notes"].get(slug, ""),
        "reference": solution_text(meta["path"]) if reveal else None,
        **att,
        "archive": [
            {
                "date": a["date"],
                "grade": a["grade"],
                "code": a["code"] if reveal else None,
            }
            for a in st["archive"].get(slug, [])
        ],
    }


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


@app.get("/api/health")
def health():
    """Is the app up and pointed at the tasks? No lock, no state, no writes —
    a container health check must never queue behind a 60 s pytest run."""
    return {"version": __version__, "tasks": len(tasks())}


@app.get("/api/catalogue")
def catalogue():
    with reading() as st:
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
        return {
            "focus": st["focus"],
            "tags": sorted({t for m in all_tasks.values() for t in m.get("tags", ())}),
            "tiers": ["core", "advanced", "packages"],  # fixed order: easiest first
            "tracks": sorted({t for m in all_tasks.values() if (t := m.get("track"))}),
            "today": q,
            "stats": {
                **stats(st, all_tasks, q["due_total"]),
                "lapse_limit": LAPSE_LIMIT,
                "stuck": stuck(st, all_tasks),
            },
            "tasks": rows,
        }


@app.get("/api/progress")
def progress():
    with reading() as st:
        all_tasks = tasks()
        return {
            **stats(st, all_tasks),
            "today": today(),
            "forecast": forecast(st, all_tasks),
            "cap": REVIEWS_PER_DAY,
            "days": dict(Counter(e["date"] for e in st["log"])),
            "log": st["log"][-30:],
            "per_tag": by_tag(st, all_tasks),
        }


@app.get("/api/task/{slug}")
def get_task(slug: str):
    with reading() as st:
        meta = _task(slug)
        return _payload(st, slug, meta, meta["path"].read_text(encoding="utf-8"))


@app.post("/api/task/{slug}/open")
def open_task(slug: str):
    with writing() as st:
        meta = _task(slug)
        open_attempt(st, slug)
        return _payload(st, slug, meta, meta["path"].read_text(encoding="utf-8"))


@app.put("/api/task/{slug}")
def save_task(slug: str, edit: Edit):
    with reading() as st:  # autosave: the file only, no timer, no commit
        meta = _task(slug)
        if slug not in st["open"]:  # a closed task is a stub; keep it one
            raise NoAttempt(slug)
        src = meta["path"].read_text(encoding="utf-8")
        _check_etag(src, edit.etag)
        new_src = validate(edit.code, src)
        write_region(meta["path"], new_src)
        return {"etag": etag(new_src)}


@app.post("/api/task/{slug}/run")
def run_task(slug: str, edit: Edit):
    """Save, then run. A rejected save is a 400 and costs no attempt.

    `submit` is the learner saying they are done: only then does the run cost an attempt
    and, on green, grade the pass. A plain Run is free and repeatable — it reports the same
    pytest output and moves nothing."""
    with writing() as st:
        meta = _task(slug)
        o = current(st, slug)
        src = meta["path"].read_text(encoding="utf-8")
        _check_etag(src, edit.etag)
        new_src = validate(edit.code, src)
        write_region(meta["path"], new_src)
        passed, out = run_tests(meta["path"], o["seed"])
        if edit.submit:
            o["attempts"] += 1
        else:
            o["runs"] = o.get("runs", 0) + 1  # not graded, but it answers the nudge
        body = cut(new_src).body
        resp = {
            "passed": passed,
            "graded": edit.submit,
            "attempts": o["attempts"],
            **summarise(out, bounds(new_src)),
        }
        log.info(
            "%s passed=%s graded=%s attempts=%s",
            slug,
            passed,
            edit.submit,
            o["attempts"],
        )
        if passed and edit.submit:
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
                "next": pick(st, tasks())[0],
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
                },
            ) from None
        return _payload(st, slug, meta, meta["path"].read_text(encoding="utf-8"))


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
        return _payload(st, slug, meta, meta["path"].read_text(encoding="utf-8"))


@app.post("/api/task/{slug}/abandon")
def abandon_task(slug: str, sent: Etag):
    """Give up: keep the work in the archive, put the stub back, drop the timer.

    `current()` first, like every other acting route: `abandon()` stubs the source whether
    or not an attempt was open."""
    with writing() as st:
        meta = _task(slug)
        current(st, slug)
        src = meta["path"].read_text(encoding="utf-8")
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
        own(st, slug)["buried"] = today() if want.buried else ""
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
    """An image, diagram or clip the README points at. A name, never a path.

    The guard is containment of the resolved path, not a list of forbidden characters: a
    list has to know every escape, and it missed both a symlink out of `assets/` and a
    Windows drive-relative name like `C:progress.json`, which carries none of them and
    still throws the left side of the join away. `is_file()` runs first so a name that
    cannot be resolved at all — an embedded null — is a 404 rather than a 500."""
    assets = _task(slug)["dir"] / "assets"
    path = assets / name
    if not path.is_file() or not path.resolve().is_relative_to(assets.resolve()):
        raise HTTPException(404, f"no asset {name!r}")
    return FileResponse(path)


@app.post("/api/focus")
def set_focus(focus: Focus):
    with writing() as st:
        st["focus"] = focus.tag
        return {"focus": st["focus"]}


@app.websocket("/lsp")
async def lsp(ws: WebSocket):
    """The editor's language server, one per open socket. See `lsp.bridge`.

    The origin check is here and not in middleware, which never runs for a websocket — and a
    websocket is exempt from the same-origin policy, so any page could otherwise open one."""
    if ws.headers.get("origin") not in _allowed_origins():
        await ws.close(code=1008)
        return
    await ws.accept()
    await bridge(ws)
