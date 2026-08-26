"""The catalogue: one folder per task, read from disk and never executed.

`<NNN>_<name>/README.md` is the guidance — YAML frontmatter and GitHub-flavoured
Markdown — and `<NNN>_<name>/task.py` is the code. A half-written folder is skipped
instead of breaking the menu, and nothing in `tasks/` is ever imported into this
process: the answers stay on disk.
"""

import ast
import re

import yaml

from .region import Invalid, _solve, bounds, cut
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
SLUG = re.compile(r"^(\d{3})_[a-z0-9_]+$")
_cache = (
    None,
    None,
    None,
)  # (key, scan, tasks) — rebinding a global is atomic, so a race just re-scans


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


def _read(folder):
    """(record | None, [reason]) for one folder: every rule a task must pass to reach the
    menu, and the record when it passes them all. The record comes back whenever the
    frontmatter parsed, so a caller can still read the values of a folder that is wrong."""
    out = []
    if not (slug := SLUG.match(folder.name)):
        out.append(
            "folder name is not <NNN>_<name>: three digits, then a lowercase name"
        )
    src = folder / "task.py"
    if not src.is_file():
        out.append("task.py: missing")
    else:
        try:
            text = src.read_text()
            bounds(text)  # no marker line, no task
            _solve(ast.parse(cut(text).body))
        except Invalid as err:
            out.append(f"task.py: {err}")
        except SyntaxError as err:
            out.append(
                f"task.py: the region above the marker is not valid Python — {err.msg}"
            )
        except UnicodeDecodeError:
            out.append("task.py: is not valid UTF-8")
        except OSError as err:
            out.append(f"task.py: cannot be read — {err.strerror}")

    readme = folder / "README.md"
    if not readme.is_file():
        return None, [*out, "README.md: missing"]
    try:
        meta, md = frontmatter(readme.read_text())
    except UnicodeDecodeError:
        return None, [*out, "README.md: is not valid UTF-8"]
    except ValueError as err:
        return None, [*out, f"README.md: {err}"]
    except yaml.YAMLError as err:
        return None, [*out, f"README.md: the frontmatter is not valid YAML — {err}"]
    except OSError as err:
        return None, [*out, f"README.md: cannot be read — {err.strerror}"]
    if not isinstance(meta, dict):
        return None, [
            *out,
            "README.md: the frontmatter is not a block of key: value lines",
        ]
    out += [
        f"README.md: frontmatter is missing `{k}`"
        for k in REQUIRED
        if meta.get(k) in (None, "", [])
    ]
    spec_md, hints = guidance(md)
    if len(hints) != 3:
        out.append(f"README.md: found {len(hints)} hints, need exactly 3")
    return {
        "prereqs": [],
        **meta,
        "topic": int(slug.group(1)) if slug else None,
        "path": src,
        "dir": folder,
        "hints": hints,
        "spec_md": spec_md,
        "search_text": search_text(spec_md),
    }, out


def _scanned():
    """(the scan, the tasks it yielded), read once per state of tasks/ and cached against
    the folders' mtimes, so an edited task still re-reads on the next call."""
    global _cache
    folders = [
        f
        for f in sorted(settings.tasks_dir.iterdir())
        if f.is_dir() and not f.name.startswith((".", "_"))
    ]
    key = (settings.tasks_dir, tuple(_stamp(f) for f in folders))
    if _cache[0] != key:
        found = [(f.name, *_read(f)) for f in folders]
        _cache = (key, found, {n: r for n, r, why in found if not why})
    return _cache[1], _cache[2]


def scan():
    """[(folder name, record | None, [reason])] — the one place a task is parsed.

    Every folder a contributor authored, in name order, with every rule it breaks. A name
    starting with `.` or `_` is tooling, not an attempt at a task."""
    return _scanned()[0]


def tasks():
    """{slug: frontmatter + topic, path, dir, spec_md, hints} for the folders that pass.

    Text only: a half-edited task is skipped instead of breaking the menu, and nothing in
    tasks/ is ever imported into this process."""
    return _scanned()[1]
