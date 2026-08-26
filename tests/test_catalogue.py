"""Catalogue: one folder per task, README.md frontmatter and Markdown guidance."""

import os
import shutil
import tempfile
from pathlib import Path

from drillion import catalogue, region
from drillion.settings import settings

DIRS = sorted(p for p in settings.tasks_dir.iterdir() if (p / "task.py").exists())

README = """\
---
title: A test task
difficulty: easy
tier: core
minutes: 7
prereqs: [1]
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


def _root(**folders):
    """A throwaway tasks/ root: {folder: {file: text}}."""
    tmp = Path(tempfile.mkdtemp(prefix="drillion_cat_"))
    for name, files in folders.items():
        (tmp / "tasks" / name).mkdir(parents=True)
        for fname, text in files.items():
            (tmp / "tasks" / name / fname).write_text(text)
    return tmp


def test_every_task_folder_is_read():
    all_tasks = catalogue.tasks()
    assert len(all_tasks) == len(DIRS) >= 104
    m = all_tasks["001_fstrings"]
    assert m["topic"] == 1 and m["minutes"] == 10 and len(m["hints"]) == 3
    assert m["path"] == settings.tasks_dir / "001_fstrings" / "task.py"
    assert m["dir"].name == "001_fstrings" and isinstance(m["tags"], list)
    assert m["spec_md"].startswith("# ") and "## Why" in m["spec_md"]
    assert "## Hints" not in m["spec_md"]  # hints are never in the spec
    assert set(catalogue.public(m)) <= set(catalogue.BROWSER)  # no paths, hints or spec
    assert "hints" not in catalogue.public(m) and "path" not in catalogue.public(m)


def test_every_readme_has_the_contract():
    for slug, m in catalogue.tasks().items():
        assert m["title"] and isinstance(m["minutes"], int) and m["tags"], slug
        assert m["spec_md"].startswith(f"# {m['title']}"), slug
        for heading in ("## Why", "## You get", "## You return", "## Rules"):
            assert f"\n{heading}\n" in m["spec_md"], f"{slug} {heading}"
        assert len(m["hints"]) == 3 and all(h.strip() for h in m["hints"]), slug


def test_topic_comes_from_the_folder_name():
    keep = settings.root
    tmp = _root(**{"042_thing": {"README.md": README, "task.py": TASK}})
    try:
        settings.root = tmp
        all_tasks = catalogue.tasks()
        assert list(all_tasks) == ["042_thing"]
        assert all_tasks["042_thing"]["topic"] == 42  # not in the frontmatter
        assert all_tasks["042_thing"]["prereqs"] == [1]
        assert all_tasks["042_thing"]["hints"] == ["one", "two", "three"]
    finally:
        settings.root = keep
        shutil.rmtree(tmp)


def test_a_broken_folder_is_skipped_instead_of_breaking_the_menu():
    keep = settings.root
    tmp = _root(
        **{
            "042_thing": {"README.md": README, "task.py": TASK},
            "043_nofrontmatter": {
                "README.md": README.split("---\n")[2],
                "task.py": TASK,
            },
            "044_notitle": {
                "README.md": README.replace("title: A test task\n", ""),
                "task.py": TASK,
            },
            "045_twohints": {
                "README.md": README.replace("### Hint 3\nthree\n", ""),
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
            "049_notier": {
                "README.md": README.replace("tier: core\n", ""),
                "task.py": TASK,
            },
            "notanumber": {"README.md": README, "task.py": TASK},
        }
    )
    try:
        settings.root = tmp
        assert list(catalogue.tasks()) == ["042_thing"]
    finally:
        settings.root = keep
        shutil.rmtree(tmp)


def test_the_scan_is_cached_but_an_edited_task_is_re_read():
    tmp, keep = (
        _root(**{"001_a": {"README.md": README, "task.py": TASK}}),
        settings.root,
    )
    try:
        settings.root = tmp
        first = catalogue.tasks()
        assert catalogue.tasks() is first  # same folders, same mtimes
        task = tmp / "tasks" / "001_a" / "task.py"
        task.write_text(TASK.replace("def solve(x):", "def solve(x, y):"))
        os.utime(task, (0, 0))  # a same-nanosecond edit is still an edit
        assert catalogue.tasks() is not first
        (tmp / "tasks" / "002_b").mkdir()
        assert catalogue.tasks() is not first  # a new folder counts too
    finally:
        settings.root = keep
        shutil.rmtree(tmp)


def test_no_task_declares_practices():
    """`practices` was a list of earlier tasks a task rehearses, authored on 16 of 171 and
    read by nothing — not the scheduler, not the page. A field that 155 tasks lack cannot
    be load-bearing, and read as a noun it invents a second unit of practice next to
    **task**. It is gone; nothing may quietly start shipping it to the browser again (#6).
    Rehearsal credit, if it is ever wanted, is a scheduler feature and needs the name
    `rehearses`."""
    assert "practices" not in catalogue.BROWSER
    for slug, m in catalogue.tasks().items():
        assert "practices" not in m, slug


def test_search_text_carries_the_prose_and_not_the_furniture():
    """The catalogue's search box searched titles only, so a learner had to already know a
    task's name to find it (#14). `search_text` is what the row carries instead: the four
    sections every task authors, flattened to one lowercase line the client substring-matches.

    Fenced code is dropped — every task's fences are full of `def`, `return` and `assert`,
    which would match everything — and so are `## Read first` (links) and the imported
    Exercism `## Introduction` / `## Instructions`, which together triple the payload for
    words the four sections have already said."""
    spec = (
        "# A task\n\n## Why\nA growing LOG file.\n\n"
        "```python\ndef solve(x):\n    return x\n```\n\n"
        "## You get\nOne path.\n\n## You return\nOne str.\n\n## Rules\nNo imports.\n\n"
        "## Read first\n- https://docs.python.org/3/\n\n## Instructions\nExercism prose.\n"
    )
    text = catalogue.search_text(spec)
    assert "growing log file" in text  # lowercased, so the needle can be too
    assert "one path" in text and "one str" in text and "no imports" in text
    assert "\n" not in text and "  " not in text  # one line, single spaces
    assert "def solve" not in text  # the fence went
    assert "docs.python.org" not in text and "exercism prose" not in text
    assert "# a task" not in text  # the title is matched separately


def test_every_task_ships_searchable_text():
    for slug, m in catalogue.tasks().items():
        assert (
            m["search_text"] == m["search_text"].lower() and m["search_text"].strip()
        ), slug
        assert "search_text" not in catalogue.public(m), (
            slug
        )  # the catalogue route adds it
