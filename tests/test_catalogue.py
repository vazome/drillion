"""Catalogue: one folder per drill, README.md frontmatter and Markdown guidance."""

import shutil
import tempfile
from pathlib import Path

from study import catalogue, region
from study.settings import settings

DIRS = sorted(p for p in settings.exercises_dir.iterdir() if (p / "drill.py").exists())

README = """\
---
title: A test drill
minutes: 7
prereqs: [1]
tags: [core]
---
# A test drill

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
DRILL = ("def solve(x):\n    raise NotImplementedError\n\n\n"
         f"{region.MARKER}\nfrom _lib import rng  # noqa: E402\n\n\n"
         "def _reference(x):\n    return x\n\n\ndef test_solve():\n    assert rng()\n")


def _root(**folders):
    """A throwaway exercises/ root: {folder: {file: text}}."""
    tmp = Path(tempfile.mkdtemp(prefix="study_cat_"))
    for name, files in folders.items():
        (tmp / "exercises" / name).mkdir(parents=True)
        for fname, text in files.items():
            (tmp / "exercises" / name / fname).write_text(text)
    return tmp


def test_every_drill_folder_is_read():
    exs = catalogue.exercises()
    assert len(exs) == len(DIRS) >= 104
    m = exs["001_fstrings"]
    assert m["topic"] == 1 and m["minutes"] == 10 and len(m["hints"]) == 3
    assert m["path"] == settings.exercises_dir / "001_fstrings" / "drill.py"
    assert m["dir"].name == "001_fstrings" and isinstance(m["tags"], list)
    assert m["spec_md"].startswith("# ") and "## Why" in m["spec_md"]
    assert "## Hints" not in m["spec_md"]                    # hints are never in the spec
    assert m["marker_line"] > 1


def test_every_readme_has_the_contract():
    for slug, m in catalogue.exercises().items():
        assert m["title"] and isinstance(m["minutes"], int) and m["tags"], slug
        assert m["spec_md"].startswith(f"# {m['title']}"), slug
        for heading in ("## Why", "## You get", "## You return", "## Rules"):
            assert f"\n{heading}\n" in m["spec_md"], f"{slug} {heading}"
        assert len(m["hints"]) == 3 and all(h.strip() for h in m["hints"]), slug


def test_topic_comes_from_the_folder_name():
    keep = settings.root
    tmp = _root(**{"042_thing": {"README.md": README, "drill.py": DRILL}})
    try:
        settings.root = tmp
        exs = catalogue.exercises()
        assert list(exs) == ["042_thing"]
        assert exs["042_thing"]["topic"] == 42            # not in the frontmatter
        assert exs["042_thing"]["prereqs"] == [1] and exs["042_thing"]["practices"] == []
        assert exs["042_thing"]["hints"] == ["one", "two", "three"]
    finally:
        settings.root = keep
        shutil.rmtree(tmp)


def test_a_broken_folder_is_skipped_instead_of_breaking_the_menu():
    keep = settings.root
    tmp = _root(**{
        "042_thing": {"README.md": README, "drill.py": DRILL},
        "043_nofrontmatter": {"README.md": README.split("---\n")[2], "drill.py": DRILL},
        "044_notitle": {"README.md": README.replace("title: A test drill\n", ""),
                        "drill.py": DRILL},
        "045_twohints": {"README.md": README.replace("### Hint 3\nthree\n", ""),
                         "drill.py": DRILL},
        "046_nomarker": {"README.md": README,
                         "drill.py": "def solve(x):\n    raise NotImplementedError\n"},
        "047_nosolve": {"README.md": README, "drill.py": DRILL.replace("def solve", "def nope")},
        "048_noreadme": {"drill.py": DRILL},
        "notanumber": {"README.md": README, "drill.py": DRILL},
    })
    try:
        settings.root = tmp
        assert list(catalogue.exercises()) == ["042_thing"]
    finally:
        settings.root = keep
        shutil.rmtree(tmp)
