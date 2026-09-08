"""Transactional local progress. Import legacy JSON once, without changing its bytes.

The domain still uses dictionaries; SQLite stores each card, attempt, note and history
entry separately. Only changed rows are written, including on timer heartbeats.
"""

import json
import logging
import sqlite3
import threading
from contextlib import closing, contextmanager
from datetime import date, datetime
from pathlib import PureWindowsPath

from . import region
from .settings import settings

SCHEMA = 1  # legacy JSON/domain shape
DB_SCHEMA = 1  # SQLite layout, independent of the imported JSON version
_LOCK = threading.Lock()
_MAPS = ("cards", "open", "notes")
log = logging.getLogger(__name__)


class TooNew(Exception):
    """Refuse a newer format before changing any progress."""


class Unreadable(Exception):
    """Progress could not be opened safely; never substitute an empty state."""


class _State(dict):
    """A request's working copy, with task resets committed alongside its archive."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resets = {}


def _defaults():
    return _State(
        version=SCHEMA, focus=None, cards={}, open={}, log=[], archive={}, notes={}
    )


def _checked(st):
    """Validate imported containers and record types without discarding unknown fields."""
    if not isinstance(st, dict):
        raise Unreadable("Progress must be an object. Restore a known-good backup.")
    version = st.get("version", SCHEMA)
    if isinstance(version, (int, float)) and version > SCHEMA:
        raise TooNew(f"Progress uses schema v{version}; upgrade drillion to open it.")
    result = _defaults()
    result.update(st)
    result["version"] = SCHEMA
    if result["focus"] is not None and not isinstance(result["focus"], str):
        raise Unreadable("Progress focus must be text or null.")
    for key in (*_MAPS, "archive"):
        if not isinstance(result[key], dict):
            raise Unreadable(f"Progress {key} must be an object.")
    for key in ("cards", "open"):
        if any(not isinstance(value, dict) for value in result[key].values()):
            raise Unreadable(f"Progress {key} must contain objects.")
        for value in result[key].values():
            _fields(value)
    if any(not isinstance(value, str) for value in result["notes"].values()):
        raise Unreadable("Progress notes must contain text.")
    for entries in (result["log"], *result["archive"].values()):
        if not isinstance(entries, list) or any(
            not isinstance(e, dict) for e in entries
        ):
            raise Unreadable("Progress log and archive must contain lists of objects.")
        for entry in entries:
            _fields(entry)
    return result


def _fields(record):
    """Reject malformed known values; historical records may omit newer fields."""
    for key in (
        "box",
        "seen",
        "lapses",
        "attempts",
        "runs",
        "hints",
        "active",
        "seed",
        "secs",
    ):
        if key in record and (type(record[key]) is not int or record[key] < 0):
            raise Unreadable(f"Progress {key} must be a nonnegative integer.")
    for key in ("new", "solution_shown"):
        if key in record and type(record[key]) is not bool:
            raise Unreadable(f"Progress {key} must be a boolean.")
    for key in ("date", "due", "buried", "last", "started", "grade", "slug", "code"):
        if key not in record:
            continue
        value = record[key]
        if not isinstance(value, str):
            raise Unreadable(f"Progress {key} must be text.")
        try:
            if key in ("date", "due") or (key == "buried" and value):
                date.fromisoformat(value)
            elif key in ("last", "started"):
                datetime.fromisoformat(value)
        except ValueError as exc:
            raise Unreadable(f"Progress {key} is not a valid ISO date/time.") from exc


def _legacy():
    path = settings.root / "progress.json"
    if not path.exists():
        return _defaults()
    try:
        return _checked(json.loads(path.read_text(encoding="utf-8")))
    except (ValueError, UnicodeError) as exc:
        raise Unreadable(
            f"Cannot read {path}. Its bytes are untouched; restore a backup."
        ) from exc


def _records(st):
    """Address records by section, task/key and sequence position; -1 marks a scalar."""
    # ponytail: full-state scans fit one learner; use targeted reads if history gets large.
    rows = {}
    for key, value in st.items():
        if key in _MAPS:
            rows.update(
                {(key, slug, -1): json.dumps(item) for slug, item in value.items()}
            )
        elif key == "archive":
            for slug, entries in value.items():
                rows[(key, slug, -1)] = "null"  # preserve even an empty archive group
                rows.update(
                    {(key, slug, i): json.dumps(e) for i, e in enumerate(entries)}
                )
        elif key == "log":
            rows.update({(key, "", i): json.dumps(e) for i, e in enumerate(value)})
        else:
            rows[("meta", key, -1)] = json.dumps(value)
    return rows


def _read(db):
    st = _defaults()
    rows = {}
    for section, key, position, data in db.execute(
        "SELECT section, key, position, data FROM progress ORDER BY section, key, position"
    ):
        rows[(section, key, position)] = data
        value = json.loads(data)
        if section == "meta":
            st[key] = value
        elif section == "archive":
            entries = st["archive"].setdefault(key, [])
            if position >= 0:
                entries.append(value)
        elif section == "log":
            st["log"].append(value)
        else:
            st[section][key] = value
    return _checked(st), rows


def _store(db, st, before):
    after = _records(_checked(st))
    db.executemany(
        "DELETE FROM progress WHERE section = ? AND key = ? AND position = ?",
        before.keys() - after.keys(),
    )
    db.executemany(
        "INSERT INTO progress VALUES (?, ?, ?, ?) "
        "ON CONFLICT(section, key, position) DO UPDATE SET data = excluded.data",
        ((*key, value) for key, value in after.items() if before.get(key) != value),
    )
    db.executemany(
        "INSERT INTO pending_resets VALUES (?, ?, ?)",
        ((slug, *reset) for slug, reset in st.resets.items()),
    )


def _initialise(db):
    version = db.execute("PRAGMA user_version").fetchone()[0]
    if version > DB_SCHEMA:
        raise TooNew(
            f"Progress database uses schema v{version}; upgrade drillion to open it."
        )
    if version == 0:
        # DDL, import and version stamp are one transaction. A failed import is retryable.
        st = _legacy()
        db.execute("""CREATE TABLE progress (
            section TEXT NOT NULL CHECK (section IN ('meta', 'cards', 'open', 'notes', 'log', 'archive')),
            key TEXT NOT NULL, position INTEGER NOT NULL CHECK (position >= -1),
            data TEXT NOT NULL CHECK (json_valid(data)),
            PRIMARY KEY (section, key, position))""")
        db.execute("""CREATE TABLE pending_resets (
            slug TEXT PRIMARY KEY, original TEXT NOT NULL, replacement TEXT NOT NULL)""")
        _store(db, st, {})
        db.execute(f"PRAGMA user_version = {DB_SCHEMA}")


def _task_path(slug):
    if (
        not slug
        or slug in (".", "..")
        or "/" in slug
        or "\\" in slug
        or PureWindowsPath(slug).drive
    ):
        raise Unreadable("Invalid task slug in a pending reset.")
    path = settings.tasks_dir / slug / "task.py"
    if not path.resolve().is_relative_to(settings.tasks_dir.resolve()):
        raise Unreadable("Pending task reset points outside the tasks directory.")
    return path


def reset_after_commit(st, path, original, replacement):
    """Schedule a region reset only after the accompanying archive is durable."""
    slug = path.parent.name
    if path.resolve() != _task_path(slug).resolve():
        raise Unreadable("Pending reset is not a task file.")
    st.resets[slug] = (region.cut(original).body, region.cut(replacement).body)


def _recover(db):
    """Finish committed resets under the database lock, preserving later external edits."""
    for slug, original, replacement in db.execute(
        "SELECT * FROM pending_resets"
    ).fetchall():
        path = _task_path(slug)
        try:
            source = path.read_text(encoding="utf-8")
            body = region.cut(source).body
            if body in (original, replacement):
                # Repeat even an already-applied reset: sync it before deleting the intent.
                region.write_region(path, region.splice(source, replacement))
            else:
                log.warning(
                    "Preserving externally edited %s after a committed reset", path
                )
        except FileNotFoundError:
            # No file to reset and the progress it belonged to is already committed, so
            # keeping the intent would only fail every later access. Repairable errors
            # below still raise, because those can be retried.
            log.warning(
                "Dropping a committed reset for %s: the task file is gone", path
            )
        except (OSError, UnicodeError, region.Invalid) as exc:
            raise Unreadable(
                f"Progress is saved, but {path} could not be reset. "
                "Restore access or repair the task file, then retry."
            ) from exc
        db.execute("DELETE FROM pending_resets WHERE slug = ?", (slug,))


@contextmanager
def _transaction():
    try:
        with closing(
            sqlite3.connect(settings.state_path, timeout=90, isolation_level=None)
        ) as db:
            # Rollback journal + EXTRA also sync the directory on journal removal.
            db.execute("PRAGMA synchronous = EXTRA")
            db.execute("BEGIN IMMEDIATE")
            try:
                _initialise(db)
                _recover(db)
                yield db
                db.commit()
                if db.execute("SELECT 1 FROM pending_resets LIMIT 1").fetchone():
                    db.execute("BEGIN IMMEDIATE")
                    _recover(db)
                    db.commit()
            except BaseException:
                db.rollback()
                raise
    except sqlite3.Error as exc:
        raise Unreadable(
            f"Cannot access {settings.state_path}: {exc}. Progress was not reset. "
            "If the database is damaged, restore a known-good backup."
        ) from exc


@contextmanager
def writing():
    """One process-safe read/modify/commit, followed by recoverable task resets."""
    with _LOCK, _transaction() as db:
        st, before = _read(db)
        yield st
        _store(db, st, before)


@contextmanager
def reading():
    """A consistent copy; shared locking also protects autosaves to task files."""
    with _LOCK:
        if (
            not settings.state_path.exists()
            and not (settings.root / "progress.json").exists()
        ):
            yield _defaults()
            return
        with _transaction() as db:
            st, _ = _read(db)
            yield st


def load():
    with reading() as st:
        return st


def save(st):
    """Replace a snapshot (fixtures/imports). Use writing() for read/modify/write."""
    with writing() as stored:
        stored.clear()
        stored.update(_checked(st))


def today():
    return date.today().isoformat()


def card(st, slug):
    """A copy with defaults: reading a task never creates a stored card."""
    return {
        "box": 0,
        "due": today(),
        "seen": 0,
        "lapses": 0,
        "buried": "",
        **st["cards"].get(slug, {}),
    }


def own(st, slug):
    """The stored card, created and back-filled on the spot: the write path."""
    st["cards"][slug] = card(st, slug)
    return st["cards"][slug]
