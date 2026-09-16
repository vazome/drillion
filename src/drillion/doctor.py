"""Why a task folder was skipped, said out loud: every reason, never just the first."""

import graphlib
import re

import yaml

from . import sandbox, tools
from .catalogue import PYTHON, SECTION, SLUG, scan
from .manifest import MAX_SPEC_CHARS

TAG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DIFFICULTIES = ("easy", "medium", "hard")
TIERS = ("core", "advanced", "packages")
REFERENCES = ("prereqs",)  # optional frontmatter lists of task numbers
# the sections a manifest shows before any sitting has filled a placeholder in
PLAIN_SECTIONS = ("why", "you get")
# Templates such as `name: {name}-web` need a line-based fallback.
SCHEMA_FIELD = re.compile(r"^(apiVersion|kind):[ \t]*(\S+)", re.MULTILINE)


def _placeholder_rules(spec_md):
    """A manifest with no sitting open serves its README as written, so only the sections
    that carry the requirements may hold a placeholder for one to fill in."""
    parts = SECTION.split(spec_md)  # [before, head, body, head, body, ...]
    return [
        f"README.md: {head.strip()} has a placeholder in it, and that section is "
        "shown before a sitting fills one in"
        for head, body in zip(parts[1::2], parts[2::2])
        if head.strip().lower() in PLAIN_SECTIONS and "{" in body
    ]


def _render_rules(meta):
    """Does the README actually fit a brief this task produces? `_placeholder_rules` asks
    only about the two sections shown before a sitting opens; a stray brace anywhere else,
    or a placeholder the grader never fills, reaches the learner as a failed open."""
    if "dir" not in meta:
        return []
    from . import manifest

    try:
        manifest.render(meta.get("spec_md", ""), manifest.generate_brief(meta, 1))
    except manifest.Rejected as err:
        return [f"README.md: the spec does not render against a brief - {err}"]
    return []


def _schema_rules(meta):
    """Does drillion actually package a schema for the kind this task teaches? kubeconform
    answers a kind it has no schema for the same way it answers a typo, so a task nobody
    packaged a schema for tells every learner who gets it right that they got it wrong.
    Caught here, at contribution time, because at grading time the two are one string."""
    try:
        with (meta["dir"] / "solution.yaml").open(encoding="utf-8") as stream:
            text = stream.read(MAX_SPEC_CHARS + 1)
    except UnicodeDecodeError:
        return ["solution.yaml: is not valid UTF-8"]
    except KeyError, OSError:
        return []  # a solution.yaml that is missing or unreadable is its own reason
    if len(text) > MAX_SPEC_CHARS:
        return [f"solution.yaml: exceeds {MAX_SPEC_CHARS} characters"]
    if not text:
        return []
    try:
        fields = yaml.safe_load(text)
    except yaml.YAMLError:
        fields = {}
        for key, value in SCHEMA_FIELD.findall(text):
            fields.setdefault(key, value)
    if not isinstance(fields, dict):
        fields = {}
    kind = fields.get("kind")
    if not isinstance(kind, str) or not kind:
        return ["solution.yaml: cannot determine kind"]
    api = fields.get("apiVersion", "")
    if not isinstance(api, str):
        return ["solution.yaml: cannot determine apiVersion"]
    group_parts = api.split("/")
    suffix = "-" + group_parts[0].split(".")[0].lower()
    if len(group_parts) > 1:
        suffix += "-" + group_parts[1].lower()
    name = kind.lower() + suffix + ".json"
    if (tools.SCHEMAS / name).is_file():
        return []
    packaged = ", ".join(sorted(p.stem for p in tools.SCHEMAS.glob("*.json")))
    return [
        (
            f"solution.yaml: no packaged schema for {kind} ({api or 'no apiVersion'}); "
            f"drillion packages {packaged}"
        )
    ]


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
    tier = meta.get("tier")
    if meta.get("kind", PYTHON) == PYTHON:
        if tier is not None and tier not in TIERS:
            out.append(f"README.md: tier {tier!r} is not one of {' / '.join(TIERS)}")
    else:
        if tier is not None:
            out.append("README.md: tier belongs to a python task, not a manifest")
        out += _placeholder_rules(meta.get("spec_md", ""))
        out += _render_rules(meta)
        out += _schema_rules(meta)
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


def _graders(fetch):
    """Print where each pinned external grader stands, downloading the ones that are
    missing or altered when asked to. Information, never a failure: a machine that has not
    fetched a grader yet has nothing wrong with its tasks, and only an explicit `--fetch`
    ever reaches the network."""
    if fetch:
        for name in tools.PINS:
            try:
                if tools.installed(name) is None:
                    tools.acquire(name)
            except (tools.Unsupported, tools.Rejected, OSError) as exc:
                print(f"{name}: {exc}")
    for name, status in tools.report():
        print(f"{name}: {status}")


def doctor(fetch=False):
    """Print what is confining graded code, which interpreter grades it, where the pinned
    graders stand, and every problem under tasks/, one line each,
    and return how many problems there were. Non-zero from the CLI on any, so CI can gate a
    contribution on it — the sandbox and grader lines are information, never a failure."""
    tier, why = sandbox.status()
    print(f"sandbox: {tier} — {why}")
    print(
        f"python: {sandbox.grading_python()} — every task is graded on this interpreter"
    )
    _graders(fetch)
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
