"""progress.json: every card, every open attempt, every pass you have ever made.

One file under `settings.root`, read and written whole. Writes are atomic, so a
crash mid-save cannot eat months of work.
"""

import json
import os
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
    return st["cards"].setdefault(slug, {"box": 0, "due": today(), "seen": 0})
