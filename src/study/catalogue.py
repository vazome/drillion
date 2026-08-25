"""The catalogue: one folder per drill, read from disk and never executed.

`<NNN>_<name>/README.md` is the guidance — YAML frontmatter and GitHub-flavoured
Markdown — and `<NNN>_<name>/drill.py` is the code. A half-written folder is skipped
instead of breaking the menu, and nothing in `exercises/` is ever imported into this
process: the answers stay on disk.
"""

import ast
import re

import yaml

from .region import _solve, bounds, cut
from .settings import settings

REQUIRED = ("title", "minutes", "tags")
HINT = re.compile(r"^### Hint \d+[ \t]*$", re.MULTILINE)


def frontmatter(md):
    """(the YAML header as a dict, the Markdown below it)."""
    if not md.startswith("---\n"):
        raise ValueError("a README needs a YAML frontmatter block")
    head, sep, body = md[4:].partition("\n---\n")
    if not sep:
        raise ValueError("the frontmatter block is not closed")
    return yaml.safe_load(head), body.lstrip("\n")


def guidance(md):
    """(spec Markdown, hints) — the spec is everything above `## Hints`."""
    spec, _, rest = md.partition("\n## Hints\n")
    return spec.strip(), [h.strip() for h in HINT.split(rest)[1:]]


def exercises():
    """{slug: frontmatter + topic, path, dir, spec_md, hints, marker_line}.

    Text only: a half-edited drill is skipped instead of breaking the menu, and
    nothing in exercises/ is ever imported into this process."""
    out = {}
    for folder in sorted(settings.exercises_dir.iterdir()):
        try:
            topic = int(folder.name.split("_")[0])
            src = (folder / "drill.py").read_text()
            marker_line = bounds(src)
            _solve(ast.parse(cut(src).body))
            meta, md = frontmatter((folder / "README.md").read_text())
            spec_md, hints = guidance(md)
            if any(meta.get(k) in (None, "", []) for k in REQUIRED) or len(hints) != 3:
                raise ValueError("a drill needs a title, minutes, tags and 3 hints")
        except Exception:  # noqa: BLE001, S112 — a half-written folder must not break the menu
            continue
        out[folder.name] = {"prereqs": [], "practices": [], **meta, "topic": topic,
                            "path": folder / "drill.py", "dir": folder, "hints": hints,
                            "spec_md": spec_md, "marker_line": marker_line}
    return out
