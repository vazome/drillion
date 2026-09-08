"""Backup and restore run against throwaway roots, never anyone's practice history."""

import asyncio
import io
import shutil
import tempfile
import zipfile
from pathlib import Path

import httpx
import pytest

from drillion import backup, region, state
from drillion.api import app
from drillion.settings import settings

SLUG = "009_fstrings"
SOURCE = settings.tasks_dir


def _root(extra=()):
    """A throwaway root holding one task, plus any `extra` slugs a test needs."""
    tmp = Path(tempfile.mkdtemp(prefix="drillion_backup_"))
    (tmp / "tasks").mkdir()
    for slug in (SLUG, *extra):
        shutil.copytree(SOURCE / slug, tmp / "tasks" / slug)
    shutil.copy(SOURCE / "_lib.py", tmp / "tasks" / "_lib.py")
    return tmp


@pytest.fixture
def root(monkeypatch):
    tmp = _root()
    monkeypatch.setattr(settings, "root", tmp)
    yield tmp
    shutil.rmtree(tmp, ignore_errors=True)


def _write(slug, body):
    path = settings.tasks_dir / slug / "task.py"
    src = path.read_text(encoding="utf-8")
    region.write_region(path, region.validate(body, src))


def _body(slug):
    path = settings.tasks_dir / slug / "task.py"
    return region.cut(path.read_text(encoding="utf-8")).body


def test_a_bundle_round_trips_progress_and_saved_code(root):
    with state.writing() as st:
        st["notes"][SLUG] = "my note"
        st["cards"][SLUG] = {"box": 3, "due": "2030-01-01", "seen": 2, "lapses": 1}
    mine = "def solve(rows):\n    return 'mine'\n"
    _write(SLUG, mine)
    data = backup.bundle()

    with state.writing() as st:
        st["notes"].clear()
        st["cards"].clear()
    _write(SLUG, "def solve(rows):\n    return 'clobbered'\n")

    summary = backup.restore(data)
    assert summary["brings"]["tasks"] == 1
    assert summary["unknown"] == [] and summary["failed"] == []
    assert state.load()["notes"][SLUG] == "my note"
    assert state.load()["cards"][SLUG]["box"] == 3
    assert _body(SLUG) == mine.strip("\n")


def test_restoring_keeps_the_data_it_replaces(root):
    with state.writing() as st:
        st["notes"][SLUG] = "before"
    data = backup.bundle()
    with state.writing() as st:
        st["notes"][SLUG] = "after"
    kept = Path(backup.restore(data)["kept"])
    assert kept.is_file()
    with zipfile.ZipFile(kept) as zf:
        assert backup.MANIFEST in zf.namelist()


def test_a_task_this_version_does_not_ship_is_reported_not_dropped(root):
    data = backup.bundle()
    buf = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(data)) as old, zipfile.ZipFile(buf, "w") as new:
        for item in old.infolist():
            new.writestr(item, old.read(item.filename))
        new.writestr(f"{backup.REGIONS}999_retired.py", "def solve():\n    return 1\n")
    assert backup.inspect(buf.getvalue())["unknown"] == ["999_retired"]
    assert backup.restore(buf.getvalue())["unknown"] == ["999_retired"]


@pytest.mark.parametrize(
    "make",
    [
        lambda: b"not a zip at all",
        lambda: _zip({"manifest.json": '{"format": 99}'}),
        lambda: _zip({"manifest.json": '{"format": 1}'}),  # no progress
        lambda: _zip({"manifest.json": '{"format": 1}', "progress.json": "["}),
        lambda: _zip(
            {"manifest.json": '{"format": 1}', "progress.json": '{"version": 99}'}
        ),
    ],
)
def test_a_bundle_we_cannot_read_changes_nothing(root, make):
    with state.writing() as st:
        st["notes"][SLUG] = "untouched"
    before = settings.state_path.read_bytes()
    with pytest.raises(backup.Rejected):
        backup.restore(make())
    assert settings.state_path.read_bytes() == before
    assert state.load()["notes"][SLUG] == "untouched"


def _zip(files):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, text in files.items():
            zf.writestr(name, text)
    return buf.getvalue()


def test_the_routes_download_preview_and_restore(root):
    async def drive():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://127.0.0.1"
        ) as api:
            paths = (await api.get("/api/settings")).json()
            assert paths["root"] == str(root)

            with state.writing() as st:
                st["notes"][SLUG] = "kept"
            got = await api.get("/api/backup")
            assert got.headers["content-type"] == "application/zip"
            assert "drillion-backup-" in got.headers["content-disposition"]
            data = got.content

            with state.writing() as st:
                st["notes"][SLUG] = "gone"
            preview = (await api.post("/api/restore/preview", content=data)).json()
            assert preview["brings"]["tasks"] == 1 and preview["brings"]["notes"] == 1
            assert preview["replaces"]["notes"] == 1
            assert state.load()["notes"][SLUG] == "gone"  # a preview changes nothing

            done = (await api.post("/api/restore", content=data)).json()
            assert done["brings"]["tasks"] == 1
            assert state.load()["notes"][SLUG] == "kept"

            bad = await api.post("/api/restore", content=b"not a zip")
            assert bad.status_code == 400 and "error" in bad.json()

    asyncio.run(drive())
