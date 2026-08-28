"""Catalogue: one folder per task, README.md frontmatter and Markdown guidance."""

import os
import shutil

from drillion import catalogue
from drillion.settings import settings
from tests.fixtures import README, TASK, tasks_root

DIRS = sorted(p for p in settings.tasks_dir.iterdir() if (p / "task.py").exists())


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
    gated = README.replace("prereqs: []", "prereqs: [1]")
    tmp = tasks_root(**{"042_thing": {"README.md": gated, "task.py": TASK}})
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
    """And `scan()` still names it, with why — the menu and doctor read one parse."""
    keep = settings.root
    tmp = tasks_root(
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
            "050_noreference": {
                "README.md": README,
                "task.py": TASK.replace("def _reference", "def _answer"),
            },
            "051_notutf8": {"README.md": README, "task.py": TASK.encode() + b"\xff"},
            "052_readmenotutf8": {
                "README.md": README.encode() + b"\xff",
                "task.py": TASK,
            },
            "042_Thing": {"README.md": README, "task.py": TASK},
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
        reasons = {n: why for n, _, why in catalogue.scan()}
        assert set(reasons) == {f.name for f in (tmp / "tasks").iterdir()}
        assert reasons["042_thing"] == []
        assert all(why for n, why in reasons.items() if n != "042_thing")
        assert reasons["046_nomarker"] == ["task.py: a task needs the machinery marker"]
        assert reasons["050_noreference"] == [
            "task.py: the machinery has no `def _reference(`"
        ]
        assert reasons["051_notutf8"] == ["task.py: is not valid UTF-8"]
        assert reasons["052_readmenotutf8"] == ["README.md: is not valid UTF-8"]
        assert reasons["042_Thing"][0].startswith("folder name is not")
    finally:
        settings.root = keep
        shutil.rmtree(tmp)


def test_the_scan_is_cached_but_an_edited_task_is_re_read():
    tmp, keep = (
        tasks_root(**{"001_a": {"README.md": README, "task.py": TASK}}),
        settings.root,
    )
    try:
        settings.root = tmp
        first = catalogue.tasks()
        assert catalogue.tasks() is first  # same folders, same mtimes
        task = tmp / "tasks" / "001_a" / "task.py"
        task.write_text(
            TASK.replace("def solve(x):", "def solve(x, y):"), encoding="utf-8"
        )
        os.utime(task, (0, 0))  # a same-nanosecond edit is still an edit
        assert catalogue.tasks() is not first
        (tmp / "tasks" / "002_b").mkdir()
        assert catalogue.tasks() is not first  # a new folder counts too
    finally:
        settings.root = keep
        shutil.rmtree(tmp)


def test_no_task_declares_practices():
    """`practices` was authored on a handful of tasks and read by nothing. It is gone, and
    nothing may quietly start shipping it to the browser again."""
    assert "practices" not in catalogue.BROWSER
    for slug, m in catalogue.tasks().items():
        assert "practices" not in m, slug


def test_search_text_carries_the_prose_and_not_the_furniture():
    """The row carries the four authored sections, flattened to one lowercase line the client
    substring-matches. Fenced code, links and the imported prose are dropped."""
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
