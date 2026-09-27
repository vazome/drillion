"""The learner's shell: bash on a PTY over a WebSocket, one per task, ended with its socket."""

import asyncio
import json
import os
import re
import shutil
import subprocess
import threading
import time
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from drillion import backup, gitrepo, terminal
from drillion.api import app
from drillion.catalogue import tasks
from drillion.settings import settings
from drillion.state import reading
from tests.fixtures import tasks_root
from tests.fixtures_git import fixture_task

SLUG = "900_git_fixture"
SAME = f"http://127.0.0.1:{settings.port}"
# the TestClient says `testserver` for a relative socket URL, which TrustedHost refuses
WS = f"ws://127.0.0.1:{settings.port}/terminal"
pytestmark = [
    pytest.mark.skipif(
        shutil.which("git") is None or shutil.which("bash") is None,
        reason="needs git and bash",
    ),
    pytest.mark.timeout(60),
]


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", "/dev/null")
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    root, keep = tasks_root(**{SLUG: fixture_task()}), settings.root
    shutil.copy(keep / "tasks" / "_git.py", root / "tasks" / "_git.py")
    settings.root = root
    with TestClient(app, base_url=SAME) as c:
        assert (
            c.post(f"/api/task/{SLUG}/open", headers={"Origin": SAME}).status_code
            == 200
        )
        yield c
    settings.root = keep
    shutil.rmtree(root, ignore_errors=True)


def _until(ws, needle):
    seen = b""
    while needle.encode() not in seen:
        seen += ws.receive_bytes()
    return seen.decode(errors="replace")


def _type(ws, text):
    ws.send_text(json.dumps({"i": text}))


def _pid(ws, line):
    """Type `line`, which echoes `pid=<n>=$((5*5))`, and read <n> back. The needle is
    output only: the echoed command line holds `$((5*5))`, never `=25`."""
    _type(ws, line)
    return int(re.search(r"pid=(\d+)=25", _until(ws, "=25")).group(1))


def _gone(pid):
    for _ in range(50):
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return
        time.sleep(0.1)
    pytest.fail(f"{pid} outlived its terminal")


def _closed_with(ws):
    with pytest.raises(WebSocketDisconnect) as closed:
        while True:
            ws.receive_bytes()
    return closed.value.code


def test_a_command_runs_in_the_sittings_repository(client):
    with client.websocket_connect(f"{WS}/{SLUG}", headers={"Origin": SAME}) as ws:
        _until(ws, "confined by")
        _type(ws, "git log --format=%s; echo done-$((1+1))\r")
        out = _until(ws, "done-2")
    assert "start" in out


def test_a_resize_reaches_the_shell(client):
    with client.websocket_connect(f"{WS}/{SLUG}", headers={"Origin": SAME}) as ws:
        _until(ws, "confined by")
        ws.send_text(json.dumps({"r": [100, 40]}))
        _type(ws, "stty size\r")
        assert "40 100" in _until(ws, "40 100")


def test_every_command_lands_in_history(client):
    with client.websocket_connect(f"{WS}/{SLUG}", headers={"Origin": SAME}) as ws:
        _until(ws, "confined by")
        _type(ws, "git status --short; echo marker-$((3*3))\r")
        _until(ws, "marker-9")
        _type(ws, "echo two-$((1+1))\r")
        _until(ws, "two-2")
    history = (settings.tasks_dir / SLUG / "history.sh").read_text()
    assert "git status --short" in history


def test_a_newer_socket_ends_the_older(client):
    with client.websocket_connect(f"{WS}/{SLUG}", headers={"Origin": SAME}) as old:
        _until(old, "confined by")
        with client.websocket_connect(f"{WS}/{SLUG}", headers={"Origin": SAME}) as new:
            _until(new, "confined by")
            assert _closed_with(old) == 4000


def test_closing_the_socket_ends_the_shell_and_its_jobs(client):
    with client.websocket_connect(f"{WS}/{SLUG}", headers={"Origin": SAME}) as ws:
        _until(ws, "confined by")
        pid = _pid(ws, "sleep 1000 & echo pid=$!=$((5*5))\r")
    _gone(pid)


def test_exit_ends_the_socket_and_the_shells_jobs(client):
    with client.websocket_connect(f"{WS}/{SLUG}", headers={"Origin": SAME}) as ws:
        _until(ws, "confined by")
        pid = _pid(ws, "sleep 1000 & echo pid=$!=$((5*5))\r")
        _type(ws, "exit\r")
        assert _closed_with(ws) == terminal.EXITED
    _gone(pid)


def test_no_attempt_no_terminal(client):
    # accepted, then closed: a close before accept reaches a browser as 1006, not 1008
    with client.websocket_connect(
        f"{WS}/001_guidos_gorgeous_lasagna", headers={"Origin": SAME}
    ) as ws:
        assert _closed_with(ws) == 1008


def test_a_foreign_page_gets_no_terminal(client):
    with (
        pytest.raises(WebSocketDisconnect) as closed,
        client.websocket_connect(
            f"{WS}/{SLUG}", headers={"Origin": "http://evil.example"}
        ) as ws,
    ):
        ws.receive_bytes()
    assert closed.value.code == 1008


def test_reset_repository_ends_the_shell_and_rebuilds(client):
    with client.websocket_connect(f"{WS}/{SLUG}", headers={"Origin": SAME}) as ws:
        _until(ws, "confined by")
        _type(ws, "touch scribble.txt; echo made-$((2+2))\r")
        _until(ws, "made-4")
        r = client.post(f"/api/task/{SLUG}/repo/reset", headers={"Origin": SAME})
        assert r.status_code == 200
        assert _closed_with(ws) == 4001
    assert not gitrepo.home(SLUG).exists()
    assert (
        "# repository reset" in (settings.tasks_dir / SLUG / "history.sh").read_text()
    )


def test_an_erase_ends_every_terminal_and_every_sitting(client):
    with client.websocket_connect(f"{WS}/{SLUG}", headers={"Origin": SAME}) as ws:
        _until(ws, "confined by")
        r = client.post(
            "/api/reset", json={"confirm": backup.PHRASE}, headers={"Origin": SAME}
        )
        assert r.status_code == 200
        assert _closed_with(ws) == 4001
    assert not (settings.root / gitrepo.SITTINGS).exists()


def test_a_restore_ends_every_terminal_and_every_sitting(client):
    data = client.get("/api/backup").content
    with client.websocket_connect(f"{WS}/{SLUG}", headers={"Origin": SAME}) as ws:
        _until(ws, "confined by")
        r = client.post("/api/restore", content=data, headers={"Origin": SAME})
        assert r.status_code == 200
        assert _closed_with(ws) == 4001
    assert not (settings.root / gitrepo.SITTINGS).exists()


def test_a_failed_restore_still_ends_terminals_and_keeps_the_sittings(client):
    with client.websocket_connect(f"{WS}/{SLUG}", headers={"Origin": SAME}) as ws:
        _until(ws, "confined by")
        r = client.post("/api/restore", content=b"not a zip", headers={"Origin": SAME})
        assert r.status_code == 400
        assert _closed_with(ws) == 4001
    assert gitrepo.home(SLUG).exists()


def test_a_socket_opened_during_a_restore_waits_for_a_fresh_sitting(
    client, monkeypatch
):
    data, real = client.get("/api/backup").content, backup.restore
    monkeypatch.setattr(backup, "restore", lambda d: (time.sleep(1), real(d))[1])
    done = []
    post = threading.Thread(
        target=lambda: done.append(
            client.post("/api/restore", content=data, headers={"Origin": SAME})
        )
    )
    with client.websocket_connect(f"{WS}/{SLUG}", headers={"Origin": SAME}) as old:
        _until(old, "confined by")
        before = _pid(old, "touch marker; echo pid=$$=$((5*5))\r")
        post.start()
        assert _closed_with(old) == 4001
    with client.websocket_connect(f"{WS}/{SLUG}", headers={"Origin": SAME}) as late:
        assert not done  # the restore is still running
        _until(late, "confined by")
        _type(late, "ls marker; echo fin-$((6*7))\r")
        assert "No such file" in _until(late, "fin-42")
        post.join()
        assert done[0].status_code == 200
        assert list(terminal._live) == [SLUG]
    _gone(before)


def test_an_abandon_ends_the_terminal(client):
    with client.websocket_connect(f"{WS}/{SLUG}", headers={"Origin": SAME}) as ws:
        _until(ws, "confined by")
        r = client.post(
            f"/api/task/{SLUG}/abandon",
            json={"etag": "history"},
            headers={"Origin": SAME},
        )
        assert r.status_code == 200
        assert _closed_with(ws) == 1000


def test_a_passing_submit_ends_the_terminal(client):
    with reading() as st:
        name = st["open"][SLUG]["brief"]["name"]
    with client.websocket_connect(f"{WS}/{SLUG}", headers={"Origin": SAME}) as ws:
        _until(ws, "confined by")
        _type(ws, f"git add {name}.md; git commit -qm 'add {name}'; echo ok-$((2*4))\r")
        _until(ws, "ok-8")
        r = client.post(
            f"/api/task/{SLUG}/run",
            json={"code": "", "etag": "history", "submit": True},
            headers={"Origin": SAME},
        )
        assert r.status_code == 200 and r.json()["passed"], r.text
        assert _closed_with(ws) == 1000


# ── overlapping connections, driven on `bridge` directly: a TestClient opens one at a time


class _Page:
    """A socket the test holds open until it hangs up."""

    def __init__(self):
        self.code = None
        self.gone = asyncio.Event()

    async def send_bytes(self, _data):
        if self.gone.is_set():
            raise WebSocketDisconnect(self.code)

    async def receive_text(self):
        await self.gone.wait()
        raise WebSocketDisconnect(self.code)

    async def close(self, code=1000):
        self.code = self.code or code
        self.gone.set()


def _sleeper(meta, sitting):
    """A stand-in shell: a process in its own session holding the PTY open."""
    master, slave = os.openpty()
    proc = subprocess.Popen(
        ["sleep", "1000"], stdin=slave, stdout=slave, start_new_session=True
    )
    os.close(slave)
    os.set_blocking(master, False)
    return proc, master


@pytest.fixture
def slow(monkeypatch, tmp_path):
    """`bridge` with a setup slow enough for connections to overlap, and no real shell."""

    def ensure(meta, o):
        time.sleep(0.3)
        return tmp_path, False

    monkeypatch.setattr(gitrepo, "ensure", ensure)
    monkeypatch.setattr(terminal, "_spawn", _sleeper)
    yield
    assert not terminal._live and not terminal._claims and not terminal._locks
    assert not terminal._starting


async def _settle(*pages):
    for page in pages:
        await page.close()


def test_two_sockets_at_once_for_one_task_leave_one_shell(slow):
    async def drive():
        meta = {"dir": Path("/tasks") / SLUG}
        pages = [_Page(), _Page()]
        runs = [
            asyncio.create_task(terminal.bridge(p, SLUG, lambda: (meta, {})))
            for p in pages
        ]
        while not (SLUG in terminal._live and any(p.code for p in pages)):
            await asyncio.sleep(0.05)
        assert [p.code for p in pages].count(4000) == 1
        live = terminal._live[SLUG]
        assert live.ws.code is None and live.proc.poll() is None
        await _settle(*pages)
        await asyncio.gather(*runs)
        assert live.proc.poll() is not None

    asyncio.run(drive())


def test_a_fifth_task_at_once_is_refused(slow):
    async def drive():
        pages = [_Page() for _ in range(5)]
        runs = [
            asyncio.create_task(
                terminal.bridge(
                    p,
                    f"90{n}_git",
                    lambda n=n: ({"dir": Path(f"/tasks/90{n}_git")}, {}),
                )
            )
            for n, p in enumerate(pages)
        ]
        while len(terminal._live) + sum(p.code == 1013 for p in pages) < 5:
            await asyncio.sleep(0.05)
        assert len(terminal._live) == terminal.MAX_SHELLS
        assert [p.code for p in pages].count(1013) == 1
        await _settle(*pages)
        await asyncio.gather(*runs)

    asyncio.run(drive())


def test_a_reset_during_setup_leaves_no_shell_behind(client, monkeypatch):
    real_ensure, real_spawn, spawned = gitrepo.ensure, terminal._spawn, []

    def ensure(meta, o):
        time.sleep(0.3)
        return real_ensure(meta, o)

    def spawn(meta, sitting):
        spawned.append(real_spawn(meta, sitting))
        return spawned[-1]

    monkeypatch.setattr(gitrepo, "ensure", ensure)
    monkeypatch.setattr(terminal, "_spawn", spawn)
    with reading() as st:
        meta, o = tasks()[SLUG], dict(st["open"][SLUG])

    async def drive():
        page = _Page()
        run = asyncio.create_task(terminal.bridge(page, SLUG, lambda: (meta, o)))
        await asyncio.sleep(0.1)  # inside the slow setup
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url=SAME
        ) as api:
            r = await api.post(f"/api/task/{SLUG}/repo/reset")
        assert r.status_code == 200
        await run
        return page.code

    assert asyncio.run(drive()) == 4001
    assert [proc.poll() is not None for proc, _ in spawned] == [True]
    assert not terminal._live
    assert not gitrepo.home(SLUG).exists()
