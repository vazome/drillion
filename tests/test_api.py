"""The web API, driven over ASGI against a throwaway copy of one task folder."""

import asyncio
import shutil
import tempfile
from datetime import date, timedelta
from pathlib import Path

import httpx

from drillion import region, scheduler, state
from drillion.api import MAX_BODY, WINDOW, _practised, _recent, app
from drillion.settings import settings

SLUG = "001_fstrings"
PASSING = 'return "\\n".join(f"{name:<14}{value:>12,.2f}" for name, value in rows)'


def _api(flow):
    """Run `flow(api, path)` against a throwaway copy of one task: the API tests
    write real files, and Daniel's tasks/ and progress.json are not for that."""
    tmp, keep = Path(tempfile.mkdtemp(prefix="drillion_api_")), settings.root
    taskdir = tmp / "tasks"
    taskdir.mkdir()
    shutil.copytree(settings.tasks_dir / SLUG, taskdir / SLUG)
    shutil.copy(settings.tasks_dir / "_lib.py", taskdir / "_lib.py")
    (taskdir / SLUG / "assets").mkdir()
    (taskdir / SLUG / "assets" / "shape.svg").write_text("<svg/>")
    settings.root = tmp  # tasks/ and progress.json move together

    async def drive():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://127.0.0.1"
        ) as client:
            await flow(client, taskdir / SLUG / "task.py")

    try:
        asyncio.run(drive())
    finally:
        settings.root = keep
        shutil.rmtree(tmp)


async def _stub_to_pass(api, path):
    cat = (await api.get("/api/catalogue")).json()
    assert [e["slug"] for e in cat["tasks"]] == [SLUG]
    assert cat["tasks"][0]["status"] == "new" and cat["today"]["new"] == [SLUG]
    assert cat["tags"] == ["f-strings"] and cat["stats"]["total"] == 1
    assert cat["today"]["due_total"] == 0 and cat["today"]["behind"] is False
    assert cat["tasks"][0]["lapses"] == 0  # a card nobody has fought yet
    assert cat["stats"]["lapse_limit"] == scheduler.LAPSE_LIMIT
    assert cat["stats"]["due"] == 0  # the real backlog, not the capped list's length
    assert cat["tiers"] == ["core", "advanced", "packages"] and cat["tracks"] == []
    assert cat["tasks"][0]["tier"] == "core" and cat["tasks"][0]["difficulty"] == "easy"
    assert "minutes" not in cat["tasks"][0]  # par time is never the learner's
    # the spec, flattened, so the search box can match what a task is about (#14)
    assert "finance" in cat["tasks"][0]["text"]  # a word in the Why, not in the title
    assert "## why" not in cat["tasks"][0]["text"]

    task = (await api.post(f"/api/task/{SLUG}/open")).json()
    assert task["attempt"]["attempts"] == 0 and task["status"] == "open"
    assert task["spec_md"].startswith("# ") and "\n## Why\n" in task["spec_md"]
    assert (
        "## Hints" not in task["spec_md"] and "spec" not in task
    )  # guidance is Markdown now
    assert task["meta"]["topic"] == 1 and "spec_md" not in task["meta"]
    assert task["region_start"] == 1 and task["marker_line"] > 1
    assert (
        "raise NotImplementedError" in task["code"] and "_reference" not in task["code"]
    )

    run = (
        await api.post(
            f"/api/task/{SLUG}/run", json={"code": task["code"], "etag": task["etag"]}
        )
    ).json()
    assert run["passed"] is False and run["attempts"] == 1
    assert any("NotImplementedError" in ln for ln in run["headline"])
    assert (
        "line 2: NotImplementedError" in run["output"]
    )  # the learner's raise, editor line

    drafted = task["code"].replace("    raise NotImplementedError", "  return ''")
    put = await api.put(
        f"/api/task/{SLUG}", json={"code": drafted, "etag": run["etag"]}
    )
    assert put.status_code == 200 and "  return ''" in path.read_text()

    stale = await api.put(
        f"/api/task/{SLUG}", json={"code": drafted, "etag": run["etag"]}
    )
    assert stale.status_code == 409  # that etag is one save out of date
    assert (
        stale.json()["etag"] == put.json()["etag"]
        and "return ''" in stale.json()["code"]
    )

    solved = task["code"].replace("raise NotImplementedError", PASSING)
    run = (
        await api.post(
            f"/api/task/{SLUG}/run", json={"code": solved, "etag": put.json()["etag"]}
        )
    ).json()
    assert run["passed"] is True and run["attempts"] == 2
    assert (
        run["grade"] in scheduler.GRADES
        and run["due_in"] == scheduler.LADDER[run["box"]]
    )
    assert run["box"] == 1 and run["stepped"] is True  # box 0 -> 1: a real promotion
    assert run["from_box"] == 0  # ...and it is a climb, not a fall
    assert run["reason"] == "the runs it took"  # the cause, never par's number
    assert run["reference"].startswith("def _reference(")  # passing is what opens it
    body = region.cut(path.read_text()).body
    assert region.stub(body) == body  # passing puts the stub back on disk

    st = state.load()
    assert st["open"] == {} and [e["slug"] for e in st["log"]] == [SLUG]
    assert PASSING in st["archive"][SLUG][0]["code"]

    done = (await api.get(f"/api/task/{SLUG}")).json()
    assert done["reference"].startswith(
        "def _reference("
    )  # a passed card may re-read it
    assert done["nudge"] is False and done["lapses"] == 0

    again = (await api.post(f"/api/task/{SLUG}/open")).json()
    assert again["reference"] is None  # ...and a new sitting starts clean
    assert again["attempt"] == {
        "attempts": 0,
        "hints": 0,
        "active": 0,
        "seed": again["attempt"]["seed"],
        "solution_shown": False,
    }
    assert "raise NotImplementedError" in again["code"]
    assert "code" not in again["archive"][0]  # a review never sees last time's answer
    assert again["solution"] == {
        "unlocked": False,
        "need_attempts": 3,
        "need_secs": 600,
    }

    hint = await api.post(f"/api/task/{SLUG}/hint")
    assert hint.status_code == 200 and (hint.json()["level"], hint.json()["total"]) == (
        1,
        3,
    )
    assert (
        hint.json()["text"]
        == (await api.get(f"/api/task/{SLUG}")).json()["hints"]["shown"][0]
    )
    soon = await api.post(f"/api/task/{SLUG}/hint")
    assert soon.status_code == 423 and 0 < soon.json()["wait_secs"] <= 120

    assert (
        await api.get("/api/catalogue", headers={"Host": "evil.com"})
    ).status_code == 400


async def _guards(api, path):
    assert (await api.get("/api/catalogue")).status_code == 200
    assert not settings.state_path.exists()  # a GET never writes progress.json

    missing = await api.get("/api/task/_lib")  # a real file, but not in the catalogue
    assert missing.status_code == 404 and missing.json()["error"] == "no task '_lib'"
    assert (await api.get("/api/task/..%2f..%2fetc%2fpasswd")).status_code == 404
    assert (await api.post("/api/task/999_nope/open")).status_code == 404

    task = (await api.get(f"/api/task/{SLUG}")).json()
    assert task["attempt"] is None and task["hints"]["shown"] == []
    assert (
        task["reference"] is None
    )  # nobody has passed it: the answer is not in the payload
    assert "_reference" not in str(task)  # ...and it is nowhere else in it either
    nobody = await api.post(
        f"/api/task/{SLUG}/run", json={"code": task["code"], "etag": task["etag"]}
    )
    assert nobody.status_code == 409  # no attempt open: nothing to time or count
    assert nobody.json()["error"].startswith("no open attempt")
    closed = await api.put(
        f"/api/task/{SLUG}", json={"code": task["code"], "etag": task["etag"]}
    )
    assert closed.status_code == 409  # ...and no autosave may un-stub a closed file

    huge = await api.put(
        f"/api/task/{SLUG}", json={"code": "x" * (MAX_BODY + 1), "etag": ""}
    )
    assert huge.status_code == 413

    await api.post(f"/api/task/{SLUG}/open")
    broken = await api.put(
        f"/api/task/{SLUG}",
        json={"code": "def solve(rows):\n    return 1 1", "etag": task["etag"]},
    )
    assert broken.status_code == 400 and (
        broken.json()["line"],
        broken.json()["col"],
    ) == (2, 14)
    assert (
        "raise NotImplementedError" in path.read_text()
    )  # a rejected edit never lands

    cheat = await api.put(
        f"/api/task/{SLUG}",
        json={
            "code": "def solve(rows):\n    return _reference(rows)",
            "etag": task["etag"],
        },
    )
    assert cheat.status_code == 400 and "_reference" in cheat.json()["error"]

    pasted = await api.put(
        f"/api/task/{SLUG}",
        json={
            "code": f"def solve(rows):\n    return ''\n{region.MARKER}\n",
            "etag": task["etag"],
        },
    )
    assert pasted.status_code == 400  # the marker is the grader's, not the editor's

    locked = await api.post(f"/api/task/{SLUG}/solution")
    assert locked.status_code == 423  # the refusal repeats the payload's own numbers
    assert {
        "unlocked": False,
        **{k: locked.json()[k] for k in ("need_attempts", "need_secs")},
    } == task["solution"]
    assert (await api.post("/api/focus", json={"tag": "core"})).json() == {
        "focus": "core"
    }
    assert (await api.get("/api/catalogue")).json()[
        "focus"
    ] == "core"  # a tier, not a tag
    assert (await api.get("/api/progress")).json()["per_tag"] == {
        "f-strings": {"seen": 0, "total": 1}
    }

    stub_etag = (await api.get(f"/api/task/{SLUG}")).json()["etag"]
    gone = await api.post(f"/api/task/{SLUG}/abandon", json={"etag": stub_etag})
    assert gone.status_code == 200 and gone.json()["attempt"] is None
    assert state.load()["archive"] == {}  # an untouched stub is not worth keeping


async def _struggled_first_sighting(api, _path):
    """The card the page kept claiming had stepped up.

    Three attempts is `struggled`, a struggle now costs a box, and a never-seen card is
    already in box 0 — the floor, so this pass moves nothing. The server says so; the page
    only renders it.
    """
    task = (await api.post(f"/api/task/{SLUG}/open")).json()
    assert state.card(state.load(), SLUG) == {
        "box": 0,
        "due": state.today(),
        "seen": 0,
        "lapses": 0,
        "buried": "",
    }

    etag = task["etag"]
    for _ in range(2):  # two failures put the pass out of `pass` range
        run = (
            await api.post(
                f"/api/task/{SLUG}/run", json={"code": task["code"], "etag": etag}
            )
        ).json()
        assert run["passed"] is False
        etag = run["etag"]

    solved = task["code"].replace("raise NotImplementedError", PASSING)
    run = (
        await api.post(f"/api/task/{SLUG}/run", json={"code": solved, "etag": etag})
    ).json()
    assert run["passed"] is True and run["attempts"] == 3
    assert run["grade"] == "struggled" and run["box"] == 0
    assert run["stepped"] is False  # box 0 -> box 0: it did not step anywhere
    assert run["from_box"] == 0  # ...and there was no box below to fall to
    assert run["reason"] == "the runs it took"  # three runs, not the clock
    assert run["lapses"] == 1  # ...but the struggle itself is counted and said
    task = (await api.get(f"/api/task/{SLUG}")).json()
    assert task["lapses"] == 1 and task["lapse_limit"] == scheduler.LAPSE_LIMIT


async def _a_slow_pass_falls_a_box(api, _path):
    """The other half of the same fix: a card that is *up* the ladder steps back down.

    The page animated a climb and said "the card stepped up" for every move there was, so a
    demotion read as a promotion. `from_box` is the direction, `stepped` is still the fact of
    the move, and the reason says which of the grade's causes landed it — here the clock, on
    a single run. Also the moment the lapse count reaches the limit, which the page flags.
    """
    task = (await api.post(f"/api/task/{SLUG}/open")).json()
    st = state.load()  # a card three boxes up, one lapse short of the flag
    st["cards"][SLUG] = {
        "box": 3,
        "due": state.today(),
        "seen": 4,
        "lapses": scheduler.LAPSE_LIMIT - 1,
    }
    st["open"][SLUG]["active"] = 9000  # an afternoon on it: over par whatever par is
    state.save(st)

    solved = task["code"].replace("raise NotImplementedError", PASSING)
    run = (
        await api.post(
            f"/api/task/{SLUG}/run", json={"code": solved, "etag": task["etag"]}
        )
    ).json()
    assert run["passed"] is True and run["grade"] == "struggled"
    assert (run["from_box"], run["box"], run["stepped"]) == (
        3,
        2,
        True,
    )  # a fall, not a climb
    assert run["reason"] == "the time it took"  # one run: the clock, not the runs
    assert run["lapses"] == scheduler.LAPSE_LIMIT  # the count the page says out loud

    task = (await api.get(f"/api/task/{SLUG}")).json()
    assert task["lapses"] == task["lapse_limit"] == scheduler.LAPSE_LIMIT


async def _the_reference_needs_the_peek_not_just_its_price(api, _path):
    """Passing a task opens the reference. Affording it must not.

    `solution.unlocked` goes true the moment three runs and ten minutes have been spent —
    but taking the answer is what sets `solution_shown`, and that is what costs the
    promotion. Shipping the reference in the payload one moment earlier would hand it over
    for free, with the page left to decide whether to look. The server owns the gate.
    """
    await api.post(f"/api/task/{SLUG}/open")
    st = state.load()
    st["cards"][SLUG] = {"box": 2, "due": state.today(), "seen": 2, "lapses": 0}
    st["open"][SLUG].update(attempts=3, active=600)  # the whole price, unspent
    state.save(st)

    task = (await api.get(f"/api/task/{SLUG}")).json()
    assert task["solution"]["unlocked"] is True and task["reference"] is None
    assert "_reference" not in str(task)

    took = (await api.post(f"/api/task/{SLUG}/solution")).json()
    assert took["code"].startswith("def _reference(")
    assert state.load()["open"][SLUG]["solution_shown"] is True  # ...and it is marked
    reread = (await api.get(f"/api/task/{SLUG}")).json()
    assert reread["reference"] == took["code"]  # a reload does not un-take it


async def _assets(api, _path):
    """Images and clips a README points at — a filename, never a path."""
    ok = await api.get(f"/api/task/{SLUG}/assets/shape.svg")
    assert ok.status_code == 200 and ok.text == "<svg/>"
    for name in ("..%2Ftask.py", "nope.png", "..%2F..%2F_lib.py", "sub%2Fx.png"):
        assert (await api.get(f"/api/task/{SLUG}/assets/{name}")).status_code == 404, (
            name
        )
    assert (await api.get("/api/task/999_nope/assets/shape.svg")).status_code == 404


async def _health(api, _path):
    """The container health check: up, pointed at the tasks, and cheap."""
    health = (await api.get("/api/health")).json()
    assert health == {"status": "ok", "tasks": 1, "root": str(settings.root)}


async def _bury(api, _path):
    """Bury from the API's side: out of today, back by itself, and reversible before then.

    The card is the point. Everything the ladder owns — box, due date, seen count, lapses —
    has to read back byte-identical afterwards, because that is the entire argument for
    shipping bury without suspend: a bury you forget about costs one day of not being asked.
    """
    st = state.load()
    st["cards"][SLUG] = {"box": 2, "due": "2020-01-01", "seen": 4, "lapses": 1}
    state.save(st)
    was = dict(st["cards"][SLUG])

    cat = (await api.get("/api/catalogue")).json()
    assert cat["today"]["review"] == [SLUG] and cat["tasks"][0]["buried"] is False

    assert (await api.post(f"/api/task/{SLUG}/bury", json={})).json() == {
        "buried": True
    }
    cat = (await api.get("/api/catalogue")).json()
    assert cat["today"]["review"] == [] and cat["today"]["due_total"] == 0
    # the way to see it: still `due`, never a fifth status, and the row says it is buried
    assert cat["tasks"][0]["status"] == "due" and cat["tasks"][0]["buried"] is True
    assert (await api.get(f"/api/task/{SLUG}")).json()["buried"] is True
    assert {k: state.card(state.load(), SLUG)[k] for k in was} == was  # nothing moved

    # the way out, taken early — the other way out is tomorrow arriving
    resp = await api.post(f"/api/task/{SLUG}/bury", json={"buried": False})
    assert resp.json() == {"buried": False}
    cat = (await api.get("/api/catalogue")).json()
    assert cat["today"]["review"] == [SLUG] and cat["tasks"][0]["buried"] is False
    assert {k: state.card(state.load(), SLUG)[k] for k in was} == was

    assert (await api.post("/api/task/nope_9999/bury", json={})).status_code == 404


def test_the_api_carries_a_task_from_stub_to_pass():
    _api(_stub_to_pass)


def test_the_api_guards_its_edges():
    _api(_guards)


def test_a_struggled_first_sighting_does_not_step_up():
    _api(_struggled_first_sighting)


def test_a_slow_pass_steps_the_card_back_down():
    _api(_a_slow_pass_falls_a_box)


def test_the_reference_opens_on_the_peek_not_on_the_price():
    _api(_the_reference_needs_the_peek_not_just_its_price)


def test_the_api_serves_a_tasks_assets():
    _api(_assets)


def test_the_api_reports_its_health():
    _api(_health)


def test_burying_takes_a_card_out_of_today_and_leaves_its_schedule_alone():
    _api(_bury)


def test_the_practice_count_is_a_rolling_window_not_a_streak():
    """A day counts if anything was archived on it — a pass, or an attempt given up on.
    Missing one costs exactly one point: there is no run to break and none to protect."""

    def day(n):
        return (date.today() - timedelta(days=n)).isoformat()  # noqa: DTZ011

    st = {
        "archive": {
            "a": [{"date": day(0)}, {"date": day(0)}],  # twice in a day is one day
            "b": [{"date": day(2)}, {"date": day(WINDOW - 1)}],
        }
    }
    assert _practised(st) == 3
    st["archive"]["c"] = [{"date": day(WINDOW)}]  # one day past the edge
    assert _practised(st) == 3
    assert _practised({"archive": {}}) == 0


def test_recent_activity_is_the_week_most_recent_first():
    """The way back into work already started: distinct slugs, newest first, capped by the
    window rather than by a count — and never filtered against today's queue, which once left
    the whole section empty for a learner whose only recent work was also their only reviews."""

    def day(n):
        return (date.today() - timedelta(days=n)).isoformat()  # noqa: DTZ011

    st = {
        "open": {},
        "archive": {
            "001_a": [{"date": day(3)}, {"date": day(1), "grade": "pass"}],
            "002_b": [{"date": day(2)}],
            "003_c": [{"date": day(WINDOW)}],  # a day past the window
            "004_d": [{"date": day(0)}],
            "009_gone": [{"date": day(0)}],
        },
    }  # renamed away: no row for it
    tasks = {"001_a": {}, "002_b": {}, "003_c": {}, "004_d": {}, "005_e": {}}
    assert _recent(st, tasks) == ["004_d", "001_a", "002_b"]

    # an open attempt is work in progress: it reaches no archive, and it still leads the list
    st["open"] = {
        "005_e": {"last": f"{day(0)}T09:30:00"},
        "002_b": {"last": f"{day(0)}T09:31:00"},
    }
    assert _recent(st, tasks) == ["002_b", "005_e", "004_d", "001_a"]
    assert _recent({"open": {}, "archive": {}}, tasks) == []

    # abandoning is the way out: it stops leading you back, until you open or pass it again
    st["open"] = {}
    st["archive"]["001_a"].append({"date": day(0), "grade": "abandoned"})
    assert _recent(st, tasks) == ["004_d", "002_b"]
    st["open"] = {"001_a": {"last": f"{day(0)}T09:30:00"}}
    assert _recent(st, tasks)[0] == "001_a"
    st["open"] = {}
    st["archive"]["001_a"].append({"date": day(0), "grade": "pass"})
    assert _recent(st, tasks)[0] == "001_a"
