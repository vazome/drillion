"""The throwaway tasks/ root the catalogue and doctor suites are both written against."""

import tempfile
from pathlib import Path

from drillion import region

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


def tasks_root(**folders):
    """A throwaway tasks/ root from {folder: {file: text}}. The caller points
    `settings.root` at it and removes it."""
    tmp = Path(tempfile.mkdtemp(prefix="drillion_test_"))
    for name, files in folders.items():
        (tmp / "tasks" / name).mkdir(parents=True)
        for fname, text in files.items():
            path = tmp / "tasks" / name / fname
            if isinstance(text, bytes):
                path.write_bytes(text)
            else:
                path.write_text(text, encoding="utf-8")
    return tmp
