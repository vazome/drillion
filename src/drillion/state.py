"""progress.json: every card, every open attempt, every pass you have ever made.

One file under `settings.root`, read and written whole. Writes are atomic, so a
crash mid-save cannot eat months of work.
"""

import json
import os
import threading
from contextlib import contextmanager
from datetime import date

from .settings import settings


def load():
    path = settings.state_path                      # read at call time: tests move the root
    st = json.loads(path.read_text()) if path.exists() else {}
    return {"focus": None, "cards": {}, "open": {}, "log": [], "archive": {}, **st}


def save(st):
    path = settings.state_path
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(st, indent=1))
    os.replace(tmp, path)          # atomic: a crash mid-write can't eat months of progress


def today():
    return date.today().isoformat()


def card(st, slug):
    """Your standing with one task, blanks filled in. `lapses` arrived after people had months
    of progress.json on disk and `load()` only defaults top-level keys, so it is filled in here
    per card: an older file reads back as a card with no lapses, and no migration step exists."""
    c = st["cards"].setdefault(slug, {"box": 0, "due": today(), "seen": 0})
    c.setdefault("lapses", 0)
    return c


# ---------------------------------------------------------------- the transaction
_LOCK = threading.Lock()     # read → validate → write → commit is one transaction


@contextmanager
def writing():
    """A change to progress.json: one lock, one load, one commit on a clean exit.

    Every route that changes anything goes through here, so the file has exactly one
    writer and one write point. An exception inside the block leaves it as it was."""
    with _LOCK:
        st = load()
        yield st
        save(st)


@contextmanager
def reading():
    """A GET: the same lock and load, with no way to commit. `card()` fills blanks in
    the dict it hands out, and under this manager those blanks are always discarded."""
    with _LOCK:
        yield load()
