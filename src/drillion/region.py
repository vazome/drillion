"""The learner's region: cut a task file in two, splice it back, guard the write.

Text and `ast` only: no settings, no state, and the one function that writes takes
the path from its caller. A task file starts with the learner's code and ends with
the grader's, separated by one marker line, so the rules that decide what lands on
disk are testable without a server. The spec is not in here at all — it lives in the
task's README.md — which is why a learner may write a docstring like any other code.
"""

import ast
import hashlib
import os
from typing import NamedTuple

MARKER = "# ══ machinery — everything below is the grader's, not yours ══"
_MARKER_HEAD = "# ══ machinery"


class Invalid(Exception):
    """A rejected edit. line/col are 1-based editor coordinates when known."""

    def __init__(self, msg, line=None, col=None):
        super().__init__(msg)
        self.msg, self.line, self.col = msg, line, col


def _solve(tree):
    """The learner's function: the last top-level def named solve."""
    fns = [
        n
        for n in tree.body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "solve"
    ]
    if not fns:
        raise Invalid("the region must define solve()")
    return fns[-1]


# ---------------------------------------------------------------- region + splice
class Region(NamedTuple):
    """A file cut in two at the marker: only `body` belongs to the learner."""

    body: str
    tail: str


def bounds(src):
    """The 1-based line of the marker — everything above it is the learner's."""
    for n, line in enumerate(src.split("\n"), 1):
        if line.startswith(_MARKER_HEAD):
            return n
    raise Invalid("a task needs the machinery marker")


def cut(src):
    """Split a file at the marker. Blank lines around the region are dropped."""
    lines = src.split("\n")
    at = bounds(src)
    return Region("\n".join(lines[: at - 1]).strip("\n"), "\n".join(lines[at - 1 :]))


def splice(src, body):
    """`src` with the region replaced. splice(src, cut(src).body) == src."""
    return body.strip("\n") + "\n\n\n" + cut(src).tail


def stub(body):
    """The region as the learner first met it: imports, given code, decorators, the
    signature, `raise`. Passing rewrites the file to this, so a review can never show
    last time's code."""
    fn = _solve(ast.parse(body))
    lines = body.split("\n")
    first = fn.body[0]
    pre = lines[first.lineno - 1][: first.col_offset]
    if pre.strip():  # `def solve(x): return x` — no room for a stub body
        raise Invalid(
            "put solve()'s body on its own line", first.lineno, first.col_offset + 1
        )
    return "\n".join(lines[: first.lineno - 1] + [pre + "raise NotImplementedError"])


def has_given(body):
    """True when the region has code above solve() that the learner must keep."""
    tree = ast.parse(body)
    above = tree.body[: tree.body.index(_solve(tree))]
    return any(not isinstance(n, (ast.Import, ast.ImportFrom)) for n in above)


def etag(disk_src):
    """Optimistic-lock token over the region only: the machinery never moves it."""
    return hashlib.sha256(cut(disk_src).body.encode()).hexdigest()[:12]


def validate(edited, disk_src):
    """The write gate: return the new file source, or raise Invalid(msg, line, col)."""
    if not edited.strip():
        raise Invalid("write something in solve() first")
    if _MARKER_HEAD in edited:
        raise Invalid("that marker line belongs to the grader — leave it below you")
    try:
        tree = ast.parse(edited)
    except SyntaxError as err:
        raise Invalid(err.msg, err.lineno, err.offset) from None
    solves = [
        n
        for n in tree.body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "solve"
    ]
    if len(solves) != 1:
        raise Invalid("the region must define solve() exactly once")
    for node in tree.body:
        for name in [getattr(node, "name", "")] + [
            t.id for t in getattr(node, "targets", []) if isinstance(t, ast.Name)
        ]:
            if name in ("_reference", "_gen") or name.startswith("test_"):
                raise Invalid(
                    f"{name} belongs to the machinery below the marker", node.lineno
                )
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == "_reference":
            raise Invalid(
                "_reference is the answer — write your own",
                node.lineno,
                node.col_offset + 1,
            )
    stub(edited)  # a pass rewrites the file to the stub: it must be possible
    new_src = splice(disk_src, edited)
    try:
        ast.parse(new_src)
    except SyntaxError as err:
        raise Invalid(err.msg) from None
    return new_src


def write_region(path, new_src):
    """Atomic write: a crash mid-save cannot leave half a task on disk."""
    tmp = path.with_suffix(".tmp")
    tmp.write_text(new_src)
    os.replace(tmp, path)
