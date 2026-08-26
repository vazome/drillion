"""Where the tasks live and where the server listens — read from the environment.

One dataclass, one module-level instance. Every module asks `settings` for a path
at call time rather than freezing one at import, so a test can point `root` at a
temp copy (and put it back) and Docker can point it at a mounted volume.
"""

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

PKG = Path(__file__).resolve().parent  # .../src/drillion
REPO = PKG.parent.parent  # the checkout, when we are running from one
# The tasks and the built page, baked into the wheel by `force-include`. Neither
# exists in a checkout, where both live at the repo root and are used in place.
TASKS_TEMPLATE = PKG / "_tasks"
WEB_BUILT_IN = PKG / "_web"


def _data_home():
    """Where a program keeps a user's files when it was installed rather than cloned."""
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local"
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share"
    return Path(base) / "drillion"


def _default_root():
    """Whatever holds `tasks/`: DRILLION_ROOT, the working directory, the checkout.

    Failing all three we were installed from a wheel, and the fallback is a writable
    per-user directory that `cli.seed()` fills from `TASKS_TEMPLATE` on the first run.
    It used to be the repo root unconditionally, which under an install points inside
    site-packages — the wrong place to keep months of somebody's progress, and often
    not writable at all.
    """
    if env := os.environ.get("DRILLION_ROOT"):
        return Path(env)
    cwd = Path.cwd()
    if (cwd / "tasks").is_dir():
        return cwd
    return REPO if (REPO / "tasks").is_dir() else _data_home()


@dataclass
class Settings:
    """Content lives under `root`; the app itself ships next to this file."""

    root: Path = field(default_factory=_default_root)
    host: str = field(
        default_factory=lambda: os.environ.get("DRILLION_HOST", "127.0.0.1")
    )
    port: int = field(
        default_factory=lambda: int(os.environ.get("DRILLION_PORT", "8765"))
    )
    open_browser: bool = field(
        default_factory=lambda: os.environ.get("DRILLION_OPEN_BROWSER", "1") != "0"
    )

    @property
    def tasks_dir(self):
        return self.root / "tasks"

    @property
    def state_path(self):
        return self.root / "progress.json"

    @property
    def web_dist(self):
        # The built page ships with the app — never under `root`, which is the learner's
        # content and comes from a mount in a container. In a checkout that is web/dist,
        # which `api.build_web()` still builds when it is stale; installed, it is the copy
        # inside the package. A checkout is the one with a `web/` beside `src/` at all.
        return REPO / "web" / "dist" if (REPO / "web").is_dir() else WEB_BUILT_IN


settings = Settings()
