"""The catalogue: one folder per task, read from disk and never executed.

`<NNN>_<name>/README.md` is the guidance — YAML frontmatter and GitHub-flavoured
Markdown — and `<NNN>_<name>/task.py` is the code. A half-written folder is skipped
instead of breaking the menu, and nothing in `tasks/` is ever imported into this
process: the answers stay on disk.
"""

import ast
import re

import yaml

from .region import _solve, bounds, cut
from .settings import settings

REQUIRED = ("title", "difficulty", "tier", "minutes", "tags")
BROWSER = ("topic", "title", "difficulty", "tier", "track", "tags", "prereqs", "source")
# `minutes` is deliberately absent: par time is grade_of()'s input, not the learner's to see.
HINT = re.compile(r"^### Hint \d+[ \t]*$", re.MULTILINE)
# The four sections every one of the 171 tasks authors, and the only ones `search_text`
# keeps. `## Read first` is links, and `## Introduction` / `## Instructions` are the
# imported Exercism prose — together they triple the text for words already said above.
SEARCHED = ("why", "you get", "you return", "rules")
SECTION = re.compile(r"^## +(.+)$", re.MULTILINE)
FENCE = re.compile(r"^```.*?^```", re.DOTALL | re.MULTILINE)
_cache = (
    None,
    None,
)  # (key, records) — rebinding a global is atomic, so a race just re-scans


def public(meta):
    """The fields the browser may see. An allowlist, so a field added to the record
    is private until someone puts it here — paths, hints and the spec never are."""
    return {k: meta[k] for k in BROWSER if k in meta}


def search_text(spec_md):
    """What a task is about, flattened into one line the catalogue can substring-match.

    The catalogue's search box only ever saw titles, so a learner had to already know a
    task's name to find it. This ships the prose with the row instead: the four authored
    sections, minus fenced code, whitespace squeezed out and lowercased, so the client
    filter is `row.text.includes(needle)` with no per-keystroke work. ~2 KB a task."""
    parts = SECTION.split(spec_md)  # [before, head, body, head, body, ...]
    kept = [
        body
        for head, body in zip(parts[1::2], parts[2::2])
        if head.strip().lower() in SEARCHED
    ]
    return " ".join(FENCE.sub(" ", " ".join(kept)).split()).lower()


def _stamp(folder):
    """Cheap identity for a task folder: its name and both files' mtimes. Two stats
    beat re-reading and re-parsing the whole set on every request."""
    out = [folder.name]
    for name in ("README.md", "task.py"):
        try:
            out.append((folder / name).stat().st_mtime_ns)
        except OSError:
            out.append(0)
    return tuple(out)


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


def tasks():
    """{slug: frontmatter + topic, path, dir, spec_md, hints}.

    Text only: a half-edited task is skipped instead of breaking the menu, and
    nothing in tasks/ is ever imported into this process. The scan is cached
    against the folders' mtimes, so an edited task still re-reads on the next call."""
    global _cache
    folders = sorted(settings.tasks_dir.iterdir())
    key = (settings.tasks_dir, tuple(_stamp(f) for f in folders))
    if _cache[0] == key:
        return _cache[1]
    out = {}
    for folder in folders:
        try:
            topic = int(folder.name.split("_")[0])
            src = (folder / "task.py").read_text()
            bounds(src)  # no marker line, no task
            _solve(ast.parse(cut(src).body))
            meta, md = frontmatter((folder / "README.md").read_text())
            spec_md, hints = guidance(md)
            if any(meta.get(k) in (None, "", []) for k in REQUIRED) or len(hints) != 3:
                raise ValueError(
                    "a task needs a title, difficulty, tier, minutes, tags and 3 hints"
                )
        except Exception:  # noqa: BLE001, S112 — a half-written folder must not break the menu
            continue
        out[folder.name] = {
            "prereqs": [],
            **meta,
            "topic": topic,
            "path": folder / "task.py",
            "dir": folder,
            "hints": hints,
            "spec_md": spec_md,
            "search_text": search_text(spec_md),
        }
    _cache = (key, out)
    return out
