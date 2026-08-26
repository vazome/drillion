"""Where the tasks live and where the server listens — read from the environment.

One dataclass, one module-level instance. Every module asks `settings` for a path
at call time rather than freezing one at import, so a test can point `root` at a
temp copy (and put it back) and Docker can point it at a mounted volume.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path

PKG = Path(__file__).resolve().parent           # .../src/drillion


def _default_root():
    """Whatever holds `tasks/`: the working directory, else the repo itself."""
    if env := os.environ.get("DRILLION_ROOT"):
        return Path(env)
    cwd = Path.cwd()
    return cwd if (cwd / "tasks").is_dir() else PKG.parent.parent


@dataclass
class Settings:
    """Content lives under `root`; the app itself ships next to this file."""

    root: Path = field(default_factory=_default_root)
    host: str = field(default_factory=lambda: os.environ.get("DRILLION_HOST", "127.0.0.1"))
    port: int = field(default_factory=lambda: int(os.environ.get("DRILLION_PORT", "8765")))
    open_browser: bool = field(
        default_factory=lambda: os.environ.get("DRILLION_OPEN_BROWSER", "1") != "0")

    @property
    def tasks_dir(self):
        return self.root / "tasks"

    @property
    def state_path(self):
        return self.root / "progress.json"

    @property
    def web_dist(self):
        # The built page ships with the app, next to `src/` — never under `root`,
        # which is the learner's content and comes from a mount in a container.
        return PKG.parent.parent / "web" / "dist"


settings = Settings()
