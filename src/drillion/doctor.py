"""Why a task folder was skipped: the rules `catalogue.tasks()` enforces, said out loud.

`tasks()` drops a folder it cannot read and says nothing, which is right for the menu
mid-session and a dead end for whoever is writing the task. `doctor` walks the same
folders, collects **every** reason each one is wrong — never stopping at the first — and
adds the value rules the catalogue never had to check: how `difficulty` and `tier` are
spelled, that `minutes` is a real par time, that tags are kebab-case, and that no
reference names a task that is not there. The reason string is the whole point.
"""

import ast
import graphlib
import re

import yaml

from .catalogue import REQUIRED, frontmatter, guidance, tasks
from .region import Invalid, _solve, bounds, cut
from .settings import settings

SLUG = re.compile(r"^(\d{3})_[a-z0-9_]+$")
TAG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DIFFICULTIES = ("easy", "medium", "hard")
TIERS = ("core", "advanced", "packages")
REFERENCES = ("prereqs", "practices")   # optional frontmatter lists of task numbers


def _folder_problems(folder):
    """(reasons, frontmatter) for one task folder — every rule it breaks, in reading
    order. The frontmatter comes back so the cross-set pass need not parse it twice;
    it is `{}` when the README could not be read at all."""
    out = []
    if not SLUG.match(folder.name):
        out.append("folder name is not <NNN>_<name>: three digits, then a lowercase name")
    src = folder / "task.py"
    if not src.is_file():
        out.append("task.py: missing")
    else:
        try:
            text = src.read_text()
            bounds(text)                            # no marker line, no task
            _solve(ast.parse(cut(text).body))
        except Invalid as err:
            out.append(f"task.py: {err}")
        except SyntaxError as err:
            out.append(f"task.py: the region above the marker is not valid Python — {err.msg}")
        except OSError as err:
            out.append(f"task.py: cannot be read — {err.strerror}")

    readme = folder / "README.md"
    if not readme.is_file():
        return [*out, "README.md: missing"], {}
    try:
        meta, md = frontmatter(readme.read_text())
    except ValueError as err:
        return [*out, f"README.md: {err}"], {}
    except yaml.YAMLError as err:
        return [*out, f"README.md: the frontmatter is not valid YAML — {err}"], {}
    if not isinstance(meta, dict):
        return [*out, "README.md: the frontmatter is not a block of key: value lines"], {}

    out += [f"README.md: frontmatter is missing `{k}`"
            for k in REQUIRED if meta.get(k) in (None, "", [])]
    if (difficulty := meta.get("difficulty")) is not None and difficulty not in DIFFICULTIES:
        out.append(f"README.md: difficulty {difficulty!r} is not one of "
                   f"{' / '.join(DIFFICULTIES)}")
    if (tier := meta.get("tier")) is not None and tier not in TIERS:
        out.append(f"README.md: tier {tier!r} is not one of {' / '.join(TIERS)}")
    minutes = meta.get("minutes")
    if minutes is not None and (isinstance(minutes, bool) or not isinstance(minutes, int)
                                or minutes <= 0):
        out.append(f"README.md: minutes {minutes!r} is not a positive whole number")
    tags = meta.get("tags")
    if tags is not None and not isinstance(tags, list):
        out.append("README.md: tags must be a list")
    elif tags:
        out += [f"README.md: tag {t!r} is not lowercase kebab-case"
                for t in tags if not isinstance(t, str) or not TAG.match(t)]
    for key in REFERENCES:
        value = meta.get(key)
        if value is not None and (not isinstance(value, list)
                                  or not all(isinstance(n, int) for n in value)):
            out.append(f"README.md: {key} must be a list of task numbers")
    hints = guidance(md)[1]
    if len(hints) != 3:
        out.append(f"README.md: found {len(hints)} hints, need exactly 3")
    return out, meta


def _set_problems(metas):
    """The rules no folder can check alone: task numbers are unique, every reference
    names a real task, nothing gates itself, and no chain of prereqs closes into a loop.

    The loop check is also the reachability check the issue asks for — a task whose
    prereqs all exist and never cycle can always be reached by working through them."""
    out, topics = [], {}
    for name in metas:
        if m := SLUG.match(name):
            topic = int(m.group(1))
            if topic in topics:
                out.append((name, f"task number {m.group(1)} is already used by {topics[topic]}"))
            else:
                topics[topic] = name
    for name, meta in metas.items():
        mine = SLUG.match(name)
        for key in REFERENCES:
            refs = meta.get(key)
            for n in refs if isinstance(refs, list) else []:
                if not isinstance(n, int):
                    continue                             # already reported as a bad list
                if mine and n == int(mine.group(1)):
                    out.append((name, f"{key} lists the task itself"))
                elif n not in topics:
                    out.append((name, f"{key} names task {n}, which does not exist"))
    graph = {t: [n for n in metas[name].get("prereqs") or [] if n in topics]
             for t, name in topics.items()}
    try:
        # ponytail: reports the first cycle only; the next run finds the next one.
        graphlib.TopologicalSorter(graph).prepare()
    except graphlib.CycleError as err:
        loop = err.args[1]
        out.append((topics[loop[0]], "prereqs form a cycle: "
                                     + " → ".join(f"{n:03d}" for n in loop)))
    return out


def problems():
    """[(folder name, reason)] for everything wrong under tasks/, folder by folder.

    Nothing here stops at the first failure: a contributor should learn all of it in one
    run. The last pass is the honesty check — a folder the catalogue drops for a reason
    none of the rules above names would be exactly the silence `doctor` exists to end."""
    folders = [f for f in sorted(settings.tasks_dir.iterdir()) if f.is_dir()]
    out, metas = [], {}
    for folder in folders:
        reasons, metas[folder.name] = _folder_problems(folder)
        out += [(folder.name, r) for r in reasons]
    out += _set_problems(metas)
    named, loaded = {name for name, _ in out}, tasks()
    out += [(f.name, "the catalogue skips this folder and doctor cannot say why")
            for f in folders if f.name not in loaded and f.name not in named]
    out.sort(key=lambda pair: pair[0])          # stable: reasons keep their reading order
    return out


def doctor():
    """Print every problem under tasks/, one line each, and return how many there were.
    Non-zero from the CLI on any, so CI can gate a contribution on it."""
    found = problems()
    if found:
        width = max(len(name) for name, _ in found) + 8
        for name, reason in found:
            print(f"tasks/{name}/".ljust(width), reason)
    total = sum(1 for f in settings.tasks_dir.iterdir() if f.is_dir())
    bad = {name for name, _ in found}
    if not found:
        print(f"{total} tasks, no problems")
    else:
        skipped = len(bad - set(tasks()))
        print(f"{len(found)} problems in {len(bad)} of {total} tasks; "
              f"{skipped} would be skipped by the catalogue")
    return len(found)
