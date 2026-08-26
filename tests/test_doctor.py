"""doctor: every reason a task folder would be skipped, and never just the first one."""

import shutil
import tempfile
from pathlib import Path

from drillion import doctor, region
from drillion.settings import settings

README = """\
---
title: A test task
difficulty: easy
tier: core
minutes: 7
prereqs: []
tags: [core]
---
# A test task

## Why
Because.

## Hints
### Hint 1
one
### Hint 2
two
### Hint 3
three
"""
TASK = (
    "def solve(x):\n    raise NotImplementedError\n\n\n"
    f"{region.MARKER}\nfrom _lib import rng  # noqa: E402\n\n\n"
    "def _reference(x):\n    return x\n\n\ndef test_solve():\n    assert rng()\n"
)


def _reasons(**folders):
    """{folder: [reason]} from a throwaway tasks/ root of {folder: {file: text}}."""
    tmp, keep = Path(tempfile.mkdtemp(prefix="drillion_doc_")), settings.root
    for name, files in folders.items():
        (tmp / "tasks" / name).mkdir(parents=True)
        for fname, text in files.items():
            (tmp / "tasks" / name / fname).write_text(text)
    try:
        settings.root = tmp
        out = {}
        for name, reason in doctor.problems():
            out.setdefault(name, []).append(reason)
        return out
    finally:
        settings.root = keep
        shutil.rmtree(tmp)


def test_a_good_task_has_nothing_said_about_it():
    assert _reasons(**{"042_thing": {"README.md": README, "task.py": TASK}}) == {}


def test_a_malformed_prereqs_is_reported_rather_than_crashed_on():
    """`prereqs: 3` — a scalar where a list belongs — is reported, not crashed on."""
    scalar = README.replace("prereqs: []", "prereqs: 3")
    assert _reasons(**{"042_thing": {"README.md": scalar, "task.py": TASK}}) == {
        "042_thing": ["README.md: prereqs must be a list of task numbers"]
    }


def test_every_reason_is_reported_not_just_the_first():
    """One folder can break several rules at once, and all of them come back."""
    both = README.replace("tags: [core]\n", "").replace("### Hint 3\nthree\n", "")
    reasons = _reasons(**{"172_asyncqueue": {"README.md": both, "task.py": TASK}})
    assert reasons["172_asyncqueue"] == [
        "README.md: frontmatter is missing `tags`",
        "README.md: found 2 hints, need exactly 3",
    ]


def test_each_skipping_rule_says_which_one_was_broken():
    """One folder per rule the catalogue drops a task for; each must come back named."""
    reasons = _reasons(
        **{
            "043_nofrontmatter": {
                "README.md": README.split("---\n")[2],
                "task.py": TASK,
            },
            "044_notitle": {
                "README.md": README.replace("title: A test task\n", ""),
                "task.py": TASK,
            },
            "045_badyaml": {
                "README.md": README.replace("tags: [core]", "tags: [core"),
                "task.py": TASK,
            },
            "046_nomarker": {
                "README.md": README,
                "task.py": "def solve(x):\n    raise NotImplementedError\n",
            },
            "047_nosolve": {
                "README.md": README,
                "task.py": TASK.replace("def solve", "def nope"),
            },
            "048_noreadme": {"task.py": TASK},
            "049_notaskpy": {"README.md": README},
            "050_syntax": {"README.md": README, "task.py": "def solve(:\n" + TASK},
            "notanumber": {"README.md": README, "task.py": TASK},
        }
    )
    assert "frontmatter" in reasons["043_nofrontmatter"][0]
    assert reasons["044_notitle"] == ["README.md: frontmatter is missing `title`"]
    assert "not valid YAML" in reasons["045_badyaml"][0]
    assert reasons["046_nomarker"] == ["task.py: a task needs the machinery marker"]
    assert reasons["047_nosolve"] == ["task.py: the region must define solve()"]
    assert reasons["048_noreadme"] == ["README.md: missing"]
    assert reasons["049_notaskpy"] == ["task.py: missing"]
    assert "not valid Python" in reasons["050_syntax"][0]
    assert reasons["notanumber"][0].startswith("folder name is not")


def test_the_value_rules_the_catalogue_never_checked():
    """The catalogue only asks whether a key is filled in; doctor asks what it says."""
    bad = (
        README.replace("difficulty: easy", "difficulty: simple")
        .replace("tier: core", "tier: basics")
        .replace("minutes: 7", "minutes: 0")
        .replace("tags: [core]", "tags: [Core Strings]")
        .replace("prereqs: []", "prereqs: [9]")
    )
    reasons = _reasons(**{"042_thing": {"README.md": bad, "task.py": TASK}})[
        "042_thing"
    ]
    assert reasons == [
        "README.md: difficulty 'simple' is not one of easy / medium / hard",
        "README.md: tier 'basics' is not one of core / advanced / packages",
        "README.md: minutes 0 is not a positive whole number",
        "README.md: tag 'Core Strings' is not lowercase kebab-case",
        "prereqs names task 9, which does not exist",
    ]


def test_the_rules_that_need_the_whole_set():
    """Gating is only wrong in company: a missing prereq, a self-gate, or a loop."""
    loop = README.replace("prereqs: []", "prereqs: [43]")
    reasons = _reasons(
        **{
            "042_thing": {"README.md": loop, "task.py": TASK},
            "043_other": {
                "README.md": README.replace("prereqs: []", "prereqs: [42]"),
                "task.py": TASK,
            },
            "044_itself": {
                "README.md": README.replace("prereqs: []", "prereqs: [44]"),
                "task.py": TASK,
            },
        }
    )
    assert reasons["044_itself"] == ["prereqs lists the task itself"]
    cycle = [
        r for rs in reasons.values() for r in rs if r.startswith("prereqs form a cycle")
    ]
    assert len(cycle) == 1 and "042" in cycle[0] and "043" in cycle[0]


def test_a_duplicate_task_number_is_reported():
    """Two folders numbered 042: one silently shadows the other in every ordering."""
    reasons = _reasons(
        **{
            "042_thing": {"README.md": README, "task.py": TASK},
            "042_other": {"README.md": README, "task.py": TASK},
        }
    )
    assert reasons == {"042_thing": ["task number 042 is already used by 042_other"]}


def test_the_shipped_catalogue_is_clean():
    """doctor gates contributions, so the tasks already here must pass it."""
    assert doctor.problems() == []


def test_tooling_directories_are_not_broken_tasks():
    """`tasks/__pycache__` is not an attempt at a task; a misnamed folder still is."""
    reasons = _reasons(
        **{
            "__pycache__": {"whatever.pyc": "x"},
            ".ruff_cache": {"x": "y"},
            "001_ok": {"README.md": README, "task.py": TASK},
        }
    )
    assert "__pycache__" not in reasons and ".ruff_cache" not in reasons
    assert reasons.get("001_ok", []) == []

    named = _reasons(bad_name={"README.md": README, "task.py": TASK})
    assert any("three digits" in r for r in named["bad_name"]), named
