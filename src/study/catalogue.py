"""The catalogue: what drills exist, read with `ast` and never executed.

A half-edited file is skipped instead of breaking the menu, and nothing in
`exercises/` is ever imported into this process — the answers stay on disk.
"""

import ast

from .region import _assign, _solve, _str_expr, bounds, cut
from .settings import settings


def has_given(body):
    """True when the region has code above solve() that the learner must keep."""
    tree = ast.parse(body)
    above = tree.body[:tree.body.index(_solve(tree))]
    return any(not isinstance(n, (ast.Import, ast.ImportFrom)) for n in above)


def read_first(src):
    """The `# READ FIRST:` block after the module docstring, `#` stripped."""
    tree = ast.parse(src)
    lines = src.split("\n")
    at = tree.body[0].end_lineno if tree.body and _str_expr(tree.body[0]) else 0
    while at < len(lines) and not lines[at].strip():
        at += 1
    block = []
    for line in lines[at:]:
        if not line.startswith("#"):
            break
        block.append(line[1:].removeprefix(" "))
    if block and block[0].startswith("SOURCE:"):  # exercism attribution line
        block = block[1:]
    return block if block and block[0].strip().startswith("READ FIRST") else []


def exercises():
    """{slug: META + path, hints, read_first, region_start, hints_line}.

    ast only: a half-edited file is skipped instead of breaking the menu, and
    nothing in exercises/ is ever imported into this process."""
    out = {}
    for path in sorted(settings.exercises_dir.glob("ex_*.py")):
        try:
            src = path.read_text()
            tree = ast.parse(src)
            meta = ast.literal_eval(_assign(tree, "META").value)
            hints = ast.literal_eval(_assign(tree, "HINTS").value)
            meta_end, hints_line = bounds(src)
            region = cut(src)
            _solve(ast.parse(region.body))
        except Exception:  # noqa: BLE001, S112 — a half-edited file must not break the menu
            continue
        out[path.stem] = {**meta, "path": path, "hints": hints, "tags": meta.get("tags", []),
                          "read_first": read_first(src), "hints_line": hints_line,
                          "region_start": meta_end + 1 + region.lead.count("\n")}
    return out
