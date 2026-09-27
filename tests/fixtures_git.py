"""The fixture git task the git tests grade against. It never enters tasks/."""

README = """\
---
title: A fixture repository
kind: git
difficulty: easy
minutes: 5
track: git
tags: [commits, staging]
---
# A fixture repository

## Why
Because a first commit is the first thing anyone does with git.

## You get
A repository with one commit and one file nobody has added yet.

## You return
One new commit, `add {name}`, holding `{name}.md`.

## Rules
Nothing else changes.

## Hints
### Hint 1
one
### Hint 2
two
### Hint 3
three
"""

GRADE = """\
NAMES = ["notes", "plans"]


def brief(r):
    return {"name": r.choice(NAMES)}


def setup(repo, b):
    repo.commit("start", {"README.md": "# Fixture\\n"})
    repo.write(f"{b['name']}.md", "- one\\n")
"""

SOLUTION = """\
git add {name}.md
git commit -m "add {name}"
"""


def fixture_task():
    """{filename: text} for `tests.fixtures.tasks_root`."""
    return {
        "README.md": README,
        "grade.py": GRADE,
        "solution.sh": SOLUTION,
        "history.sh": "",
    }
