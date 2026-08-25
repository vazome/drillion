"""The learner's region: cut a drill file in three, splice it back, guard the write.

Text and `ast` only: no settings, no state, and the one function that writes
takes the path from its caller. The region between META and HINTS is the only
text an edit may replace, so the rules that decide what lands on disk are
testable without a server.
"""

import ast
import hashlib
import os
from dataclasses import dataclass


class Invalid(Exception):
    """A rejected edit. line/col are 1-based editor coordinates when known."""

    def __init__(self, msg, line=None, col=None):
        super().__init__(msg)
        self.msg, self.line, self.col = msg, line, col


# ---------------------------------------------------------------- ast helpers
def _assign(tree, name):
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == name for t in node.targets):
            return node
    return None


def _solve(tree):
    """The learner's function: the last top-level def named solve."""
    fns = [n for n in tree.body
           if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "solve"]
    if not fns:
        raise Invalid("the region must define solve()")
    return fns[-1]


def _str_expr(node):
    return (isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str))


def _docstring(fn):
    """solve()'s docstring node, or None — it is the spec, so it is never optional."""
    return fn.body[0] if _str_expr(fn.body[0]) else None


# ---------------------------------------------------------------- region + splice
@dataclass
class Region:
    """A file cut in three: only `body` belongs to the learner."""
    head: str
    lead: str
    body: str
    trail: str
    tail: str


@dataclass
class Spec:
    """The region split into what the editor shows and what it must not."""
    editor: str
    spec_src: str | None
    spec_text: str | None
    doc_offset: int


def bounds(src):
    """(last line of META, line of HINTS) — the learner's region lies between them."""
    tree = ast.parse(src)
    meta, hints = _assign(tree, "META"), _assign(tree, "HINTS")
    if meta is None or hints is None or hints.lineno <= meta.end_lineno:
        raise Invalid("an exercise needs META, then solve(), then HINTS")
    return meta.end_lineno, hints.lineno


def cut(src):
    """Split a file around the region. Blank lines at its ends are kept verbatim."""
    meta_end, hints_start = bounds(src)
    lines = src.split("\n")
    mid = "\n".join(lines[meta_end:hints_start - 1])
    lead = mid[:len(mid) - len(mid.lstrip("\n"))]
    rest = mid[len(lead):]
    body = rest.rstrip("\n")
    return Region("\n".join(lines[:meta_end]), lead, body,
                  rest[len(body):], "\n".join(lines[hints_start - 1:]))


def splice(src, body):
    """`src` with the region replaced. splice(src, cut(src).body) == src."""
    r = cut(src)
    return "\n".join([r.head, r.lead + body.strip("\n") + r.trail, r.tail])


def strip_spec(body):
    """The region minus solve()'s docstring: the spec is shown beside the editor,
    never inside it, so it cannot be mangled or deleted."""
    fn = _solve(ast.parse(body))
    doc = _docstring(fn)
    if doc is None:
        return Spec(body, None, None, 0)
    lines = body.split("\n")
    spec = lines[doc.lineno - 1:doc.end_lineno]
    return Spec("\n".join(lines[:doc.lineno - 1] + lines[doc.end_lineno:]),
                "\n".join(spec), ast.get_docstring(fn), len(spec))


def merge_spec(edited, spec_src):
    """Put the spec back at the top of solve(), at the learner's own indentation."""
    if spec_src is None:
        return edited
    fn = _solve(ast.parse(edited))
    lines = edited.split("\n")
    first = fn.body[0]
    pre = lines[first.lineno - 1][:first.col_offset]
    if pre.strip():                 # a one-liner def, or `): return x` — no room for the spec
        raise Invalid("put solve()'s body on its own line", first.lineno, first.col_offset + 1)
    drop = first.end_lineno - first.lineno + 1 if _docstring(fn) else 0
    rest = lines[first.lineno - 1 + drop:]
    if not any(ln.strip() for ln in rest):
        raise Invalid("solve() has no body", first.lineno)
    margin = len(spec_src) - len(spec_src.lstrip(" \t"))   # 4 on a pristine file, 2 after a 2-space save
    spec = [pre + ln[margin:] if ln.strip() else ln for ln in spec_src.split("\n")]
    return "\n".join(lines[:first.lineno - 1] + spec + rest)


def stub(body):
    """The region as the learner first met it: given code, signature, spec, `raise`.
    Passing rewrites the file to this, so a review can never show last time's answer."""
    fn = _solve(ast.parse(body))
    lines = body.split("\n")
    doc = _docstring(fn)
    keep = doc.end_lineno if doc else fn.body[0].lineno - 1
    pre = lines[fn.body[0].lineno - 1][:fn.body[0].col_offset]
    return "\n".join(lines[:keep] + [pre + "raise NotImplementedError"])



def etag(disk_src):
    """Optimistic-lock token over the region only: editing HINTS does not invalidate it."""
    return hashlib.sha256(cut(disk_src).body.encode()).hexdigest()[:12]


def validate(edited, spec_src, disk_src):
    """The write gate: return the new file source, or raise Invalid(msg, line, col)."""
    if not edited.strip():
        raise Invalid("write something in solve() first")
    try:
        tree = ast.parse(edited)
    except SyntaxError as err:
        raise Invalid(err.msg, err.lineno, err.offset) from None
    solves = [n for n in tree.body
              if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "solve"]
    if len(solves) != 1:
        raise Invalid("the region must define solve() exactly once")
    for node in tree.body:
        for name in [getattr(node, "name", "")] + [t.id for t in getattr(node, "targets", [])
                                                   if isinstance(t, ast.Name)]:
            if name in ("_reference", "_gen", "META", "HINTS") or name.startswith("test_"):
                raise Invalid(f"{name} belongs to the machinery below HINTS", node.lineno)
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == "_reference":
            raise Invalid("_reference is the answer — write your own",
                          node.lineno, node.col_offset + 1)
    body = merge_spec(edited, spec_src)
    try:
        merged = ast.parse(body)
    except SyntaxError as err:                  # a mangled spec: never the learner's fault
        raise Invalid(f"could not put the spec back ({err.msg})") from None
    if not ast.get_docstring(_solve(merged)):
        raise Invalid("solve() lost its docstring")
    new_src = splice(disk_src, body)
    try:
        ast.parse(new_src)
    except SyntaxError as err:
        raise Invalid(err.msg) from None
    bounds(new_src)
    if "def _reference(" not in new_src:
        raise Invalid("that edit would delete the reference solution")
    return new_src


def write_region(path, new_src):
    """Atomic write, with one last look for the spec — the file is the source of truth."""
    if not ast.get_docstring(_solve(ast.parse(cut(new_src).body))):
        raise Invalid("refusing to write solve() without its docstring")
    tmp = path.with_suffix(".tmp")
    tmp.write_text(new_src)
    os.replace(tmp, path)
