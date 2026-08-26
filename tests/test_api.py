"""The web API, driven over ASGI against a throwaway copy of one drill folder."""

import asyncio
import shutil
import tempfile
from pathlib import Path

import httpx

from drillion import region, scheduler, state
from drillion.api import MAX_BODY, app
from drillion.settings import settings

SLUG = "001_fstrings"
PASSING = 'return "\\n".join(f"{name:<14}{value:>12,.2f}" for name, value in rows)'


def _api(flow):
    """Run `flow(api, path)` against a throwaway copy of one drill: the API tests
    write real files, and Daniel's exercises/ and progress.json are not for that."""
    tmp, keep = Path(tempfile.mkdtemp(prefix="drillion_api_")), settings.root
    exdir = tmp / "exercises"
    exdir.mkdir()
    shutil.copytree(settings.exercises_dir / SLUG, exdir / SLUG)
    shutil.copy(settings.exercises_dir / "_lib.py", exdir / "_lib.py")
    (exdir / SLUG / "assets").mkdir()
    (exdir / SLUG / "assets" / "shape.svg").write_text("<svg/>")
    settings.root = tmp                              # exercises/ and progress.json move together

    async def drive():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),
                                     base_url="http://127.0.0.1") as client:
            await flow(client, exdir / SLUG / "drill.py")

    try:
        asyncio.run(drive())
    finally:
        settings.root = keep
        shutil.rmtree(tmp)


async def _stub_to_pass(api, path):
    cat = (await api.get("/api/catalogue")).json()
    assert [e["slug"] for e in cat["exercises"]] == [SLUG]
    assert cat["exercises"][0]["status"] == "new" and cat["today"]["new"] == [SLUG]
    assert cat["tags"] == ["core"] and cat["stats"]["total"] == 1

    ex = (await api.post(f"/api/ex/{SLUG}/open")).json()
    assert ex["attempt"]["attempts"] == 0 and ex["status"] == "open"
    assert ex["spec_md"].startswith("# ") and "\n## Why\n" in ex["spec_md"]
    assert "## Hints" not in ex["spec_md"] and "spec" not in ex   # guidance is Markdown now
    assert ex["meta"]["topic"] == 1 and "spec_md" not in ex["meta"]
    assert ex["region_start"] == 1 and ex["marker_line"] > 1
    assert "raise NotImplementedError" in ex["code"] and "_reference" not in ex["code"]

    run = (await api.post(f"/api/ex/{SLUG}/run",
                          json={"code": ex["code"], "etag": ex["etag"]})).json()
    assert run["passed"] is False and run["attempts"] == 1
    assert any("NotImplementedError" in ln for ln in run["headline"])
    assert "line 2: NotImplementedError" in run["output"]   # the learner's raise, editor line

    drafted = ex["code"].replace("    raise NotImplementedError", "  return ''")
    put = await api.put(f"/api/ex/{SLUG}", json={"code": drafted, "etag": run["etag"]})
    assert put.status_code == 200 and "  return ''" in path.read_text()

    stale = await api.put(f"/api/ex/{SLUG}", json={"code": drafted, "etag": run["etag"]})
    assert stale.status_code == 409                  # that etag is one save out of date
    assert stale.json()["etag"] == put.json()["etag"] and "return ''" in stale.json()["code"]

    solved = ex["code"].replace("raise NotImplementedError", PASSING)
    run = (await api.post(f"/api/ex/{SLUG}/run",
                          json={"code": solved, "etag": put.json()["etag"]})).json()
    assert run["passed"] is True and run["attempts"] == 2
    assert run["grade"] in scheduler.GRADES and run["due_in"] == scheduler.LADDER[run["box"]]
    body = region.cut(path.read_text()).body
    assert region.stub(body) == body                  # passing puts the stub back on disk

    st = state.load()
    assert st["open"] == {} and [e["slug"] for e in st["log"]] == [SLUG]
    assert PASSING in st["archive"][SLUG][0]["code"]

    again = (await api.post(f"/api/ex/{SLUG}/open")).json()
    assert again["attempt"] == {"attempts": 0, "hints": 0, "active": 0,
                                "seed": again["attempt"]["seed"], "solution_shown": False}
    assert "raise NotImplementedError" in again["code"]
    assert "code" not in again["archive"][0]         # a review never sees last time's answer
    assert again["solution"] == {"unlocked": False, "need_attempts": 3, "need_secs": 600}

    hint = await api.post(f"/api/ex/{SLUG}/hint")
    assert hint.status_code == 200 and (hint.json()["level"], hint.json()["total"]) == (1, 3)
    assert hint.json()["text"] == (await api.get(f"/api/ex/{SLUG}")).json()["hints"]["shown"][0]
    soon = await api.post(f"/api/ex/{SLUG}/hint")
    assert soon.status_code == 423 and 0 < soon.json()["wait_secs"] <= 120

    assert (await api.get("/api/catalogue", headers={"Host": "evil.com"})).status_code == 400


async def _guards(api, path):
    assert (await api.get("/api/catalogue")).status_code == 200
    assert not settings.state_path.exists()                  # a GET never writes progress.json

    missing = await api.get("/api/ex/_lib")          # a real file, but not in the catalogue
    assert missing.status_code == 404 and missing.json()["error"] == "no exercise '_lib'"
    assert (await api.get("/api/ex/..%2f..%2fetc%2fpasswd")).status_code == 404
    assert (await api.post("/api/ex/999_nope/open")).status_code == 404

    ex = (await api.get(f"/api/ex/{SLUG}")).json()
    assert ex["attempt"] is None and ex["hints"]["shown"] == []
    nobody = await api.post(f"/api/ex/{SLUG}/run", json={"code": ex["code"], "etag": ex["etag"]})
    assert nobody.status_code == 409                 # no attempt open: nothing to time or count
    assert nobody.json()["error"].startswith("no open attempt")
    closed = await api.put(f"/api/ex/{SLUG}", json={"code": ex["code"], "etag": ex["etag"]})
    assert closed.status_code == 409                 # ...and no autosave may un-stub a closed file

    huge = await api.put(f"/api/ex/{SLUG}", json={"code": "x" * (MAX_BODY + 1), "etag": ""})
    assert huge.status_code == 413

    await api.post(f"/api/ex/{SLUG}/open")
    broken = await api.put(f"/api/ex/{SLUG}", json={"code": "def solve(rows):\n    return 1 1",
                                                   "etag": ex["etag"]})
    assert broken.status_code == 400 and (broken.json()["line"], broken.json()["col"]) == (2, 14)
    assert "raise NotImplementedError" in path.read_text()    # a rejected edit never lands

    cheat = await api.put(f"/api/ex/{SLUG}",
                          json={"code": "def solve(rows):\n    return _reference(rows)",
                                "etag": ex["etag"]})
    assert cheat.status_code == 400 and "_reference" in cheat.json()["error"]

    pasted = await api.put(f"/api/ex/{SLUG}",
                           json={"code": f"def solve(rows):\n    return ''\n{region.MARKER}\n",
                                 "etag": ex["etag"]})
    assert pasted.status_code == 400                 # the marker is the grader's, not the editor's

    locked = await api.post(f"/api/ex/{SLUG}/solution")
    assert locked.status_code == 423                 # the refusal repeats the payload's own numbers
    assert {"unlocked": False, **{k: locked.json()[k]
                                  for k in ("need_attempts", "need_secs")}} == ex["solution"]
    assert (await api.post("/api/focus", json={"tag": "core"})).json() == {"focus": "core"}
    assert (await api.get("/api/catalogue")).json()["focus"] == "core"
    assert (await api.get("/api/progress")).json()["per_tag"] == {"core": {"seen": 0, "total": 1}}

    stub_etag = (await api.get(f"/api/ex/{SLUG}")).json()["etag"]
    gone = await api.post(f"/api/ex/{SLUG}/abandon", json={"etag": stub_etag})
    assert gone.status_code == 200 and gone.json()["attempt"] is None
    assert state.load()["archive"] == {}              # an untouched stub is not worth keeping


async def _assets(api, _path):
    """Images and clips a README points at — a filename, never a path."""
    ok = await api.get(f"/api/ex/{SLUG}/assets/shape.svg")
    assert ok.status_code == 200 and ok.text == "<svg/>"
    for name in ("..%2Fdrill.py", "nope.png", "..%2F..%2F_lib.py", "sub%2Fx.png"):
        assert (await api.get(f"/api/ex/{SLUG}/assets/{name}")).status_code == 404, name
    assert (await api.get("/api/ex/999_nope/assets/shape.svg")).status_code == 404


async def _health(api, _path):
    """The container health check: up, pointed at the drills, and cheap."""
    health = (await api.get("/api/health")).json()
    assert health == {"status": "ok", "exercises": 1, "root": str(settings.root)}


def test_the_api_carries_a_drill_from_stub_to_pass():
    _api(_stub_to_pass)


def test_the_api_guards_its_edges():
    _api(_guards)


def test_the_api_serves_a_drills_assets():
    _api(_assets)


def test_the_api_reports_its_health():
    _api(_health)
