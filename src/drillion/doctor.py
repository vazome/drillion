"""Why a task folder was skipped, said out loud: every reason, never just the first."""

import graphlib
import re

from . import sandbox
from .catalogue import SLUG, scan

TAG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DIFFICULTIES = ("easy", "medium", "hard")
TIERS = ("core", "advanced", "packages")
REFERENCES = ("prereqs",)  # optional frontmatter lists of task numbers


def _value_rules(meta):
    """The rules the catalogue never had to check: what a filled-in field actually says."""
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
    """The task numbers under `key` that can actually be walked: a bad value is already
    reported by `_value_rules`, and nothing downstream of that report may crash on it."""
    refs = meta.get(key)
    return [n for n in refs if isinstance(n, int)] if isinstance(refs, list) else []


def _set_problems(metas):
    """The rules no folder can check alone: task numbers are unique, every reference
    names a real task, nothing gates itself, and no chain of prereqs closes into a loop.
    Only the first cycle is named; the next run finds the next one."""
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
                elif key == "prereqs" and mine and n > int(mine.group(1)):
                    # the number is the curriculum position, so what gates a task precedes it
                    out.append((name, f"prereqs names task {n}, which comes later"))
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
    """[(folder name, reason)] for everything wrong under tasks/, folder by folder."""
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
    """Print what is confining graded code and every problem under tasks/, one line each,
    and return how many problems there were. Non-zero from the CLI on any, so CI can gate a
    contribution on it — the sandbox line is information, never a failure."""
    tier, why = sandbox.status()
    print(f"sandbox: {tier} — {why}")
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
