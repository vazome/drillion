"""Spaced-repetition Python tasks: catalogue, region splice, scheduling, grading.

The task files under `settings.root` are the source of truth; this package
reads them with `ast`, splices the learner's region back in, and runs the tests
in a subprocess. Design notes live in DESIGN.md.
"""

from importlib.metadata import version

# The one place the number is read from. It is declared once, in pyproject.toml,
# and baked into the installed metadata; nothing in the source repeats it.
__version__ = version("drillion")
