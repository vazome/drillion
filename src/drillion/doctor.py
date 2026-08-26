"""Why a task folder was skipped, said out loud.

`catalogue.tasks()` drops a folder it cannot read and says nothing, which is right for the
menu mid-session and a dead end for whoever is writing the task. `catalogue.scan()` carries
every reason it dropped one; `doctor` prints them all — never stopping at the first — and
adds the rules the catalogue never had to check: how `difficulty` and `tier` are spelled,
that `minutes` is a real par time, that tags are kebab-case, and that no reference names a
task that is not there. The reason string is the whole point.
"""

import graphlib
import re

from .catalogue import SLUG, scan

TAG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DIFFICULTIES = ("easy", "medium", "hard")
TIERS = ("core", "advanced", "packages")
REFERENCES = ("prereqs",)  # optional frontmatter lists of task numbers


def _value_rules(meta):
    """The rules the catalogue never had to check: what a filled-in field actually says.
    A task with `difficulty: simple` loads fine and then sorts, filters and grades wrong."""
    out = []
    if (
        difficulty := meta.get("difficulty")
    ) is not None and difficulty not in DIFFICULTIES:
        out.append(
            f"README.md: difficulty {difficulty!r} is not one of "
            f"{' / '.join(DIFFICULTIES)}"
        )
    if (tier := meta.get("tier")) is not None and tier not in TIERS:
        out.append(f"README.md: tier {tier!r} is not one of {' / '.join(TIERS)}")
    minutes = meta.get("minutes")
    if minutes is not None and (
        isinstance(minutes, bool) or not isinstance(minutes, int) or minutes <= 0
    ):
        out.append(f"README.md: minutes {minutes!r} is not a positive whole number")
    tags = meta.get("tags")
    if tags is not None and not isinstance(tags, list):
        out.append("README.md: tags must be a list")
    elif tags:
        out += [
            f"README.md: tag {t!r} is not lowercase kebab-case"
            for t in tags
            if not isinstance(t, str) or not TAG.match(t)
        ]
    for key in REFERENCES:
        value = meta.get(key)
        if value is not None and (
            not isinstance(value, list) or not all(isinstance(n, int) for n in value)
        ):
            out.append(f"README.md: {key} must be a list of task numbers")
    return out


def _refs(meta, key):
    """The task numbers under `key` that can actually be walked. `prereqs: 3` and
    `prereqs: [a, 2]` are both already reported as bad frontmatter by `_value_rules` —
    doctor's whole job is to say why a folder is wrong, so nothing downstream of that
    report may crash on the same value before it reaches the screen."""
    refs = meta.get(key)
    return [n for n in refs if isinstance(n, int)] if isinstance(refs, list) else []


def _set_problems(metas):
    """The rules no folder can check alone: task numbers are unique, every reference
    names a real task, nothing gates itself, and no chain of prereqs closes into a loop.

    The loop check is also the reachability check — a task whose prereqs all exist and
    never cycle can always be reached by working through them. Only the first cycle is
    named; the next run finds the next one."""
    out, topics = [], {}
    for name in metas:
        if m := SLUG.match(name):
            topic = int(m.group(1))
            if topic in topics:
                out.append(
                    (
                        name,
                        f"task number {m.group(1)} is already used by {topics[topic]}",
                    )
                )
            else:
                topics[topic] = name
    for name, meta in metas.items():
        mine = SLUG.match(name)
        for key in REFERENCES:
            for n in _refs(meta, key):
                if mine and n == int(mine.group(1)):
                    out.append((name, f"{key} lists the task itself"))
                elif n not in topics:
                    out.append((name, f"{key} names task {n}, which does not exist"))
    graph = {
        t: [n for n in _refs(metas[name], "prereqs") if n in topics]
        for t, name in topics.items()
    }
    try:
        graphlib.TopologicalSorter(graph).prepare()
    except graphlib.CycleError as err:
        loop = err.args[1]
        out.append(
            (
                topics[loop[0]],
                "prereqs form a cycle: " + " → ".join(f"{n:03d}" for n in loop),
            )
        )
    return out


def problems():
    """[(folder name, reason)] for everything wrong under tasks/, folder by folder.

    Nothing here stops at the first failure: a contributor should learn all of it in one
    run. The catalogue's own reasons come first, then the value rules, then the rules that
    need the whole set."""
    out, metas = [], {}
    for name, record, why in scan():
        metas[name] = record or {}
        out += [(name, r) for r in why]
        if record is not None:
            out += [(name, r) for r in _value_rules(record)]
    out += _set_problems(metas)
    out.sort(key=lambda pair: pair[0])  # stable: reasons keep their reading order
    return out


def doctor():
    """Print every problem under tasks/, one line each, and return how many there were.
    Non-zero from the CLI on any, so CI can gate a contribution on it."""
    found = problems()
    if found:
        width = max(len(name) for name, _ in found) + 8
        for name, reason in found:
            print(f"tasks/{name}/".ljust(width), reason)
    folders = scan()
    if not found:
        print(f"{len(folders)} tasks, no problems")
    else:
        bad = {name for name, _ in found}
        skipped = sum(1 for _, _, why in folders if why)
        print(
            f"{len(found)} problems in {len(bad)} of {len(folders)} tasks; "
            f"{skipped} would be skipped by the catalogue"
        )
    return len(found)
