"""progress.json: every card, every open attempt, every pass you have ever made.

One file under `settings.root`, read and written whole."""

import json
import os
import threading
from contextlib import contextmanager
from datetime import date

from .settings import settings


def load():
    path = settings.state_path  # read at call time: tests move the root
    st = json.loads(path.read_text()) if path.exists() else {}
    return {
        "focus": None,
        "cards": {},
        "open": {},
        "log": [],
        "archive": {},
        "notes": {},
        **st,
    }


def save(st):
    path = settings.state_path
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(st, indent=1))
    os.replace(tmp, path)  # atomic: a crash mid-write can't eat months of progress


def today():
    return date.today().isoformat()


def card(st, slug):
    """Your standing with one task, blanks filled in — `load()` only defaults top-level keys."""
    c = st["cards"].setdefault(slug, {"box": 0, "due": today(), "seen": 0})
    c.setdefault("lapses", 0)
    c.setdefault("buried", "")
    return c


_LOCK = threading.Lock()


@contextmanager
def writing():
    """A change to progress.json: one lock, one load, one commit on a clean exit."""
    with _LOCK:
        st = load()
        yield st
        save(st)


@contextmanager
def reading():
    """A GET: the same lock and load, with no way to commit."""
    with _LOCK:
        yield load()
