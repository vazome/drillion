#!/usr/bin/env python3
"""Drill core: catalogue, region splice, scheduling, grading, attempts.

    uv run study.py            open the web UI (web.py)
    uv run study.py selfcheck  solve every exercise with its own _reference

The browser edits only the region between META and HINTS; everything here is
data in, data out so the rules can be tested without a server. This module
never imports web.py and never execs an exercise: the catalogue is read with
ast, and tests only ever run in a pytest subprocess.

Design notes live in STUDY.md. The scheduler is a 5-box Leitner ladder, not
FSRS: the horizon is 12 weeks and Cepeda 2008 puts the optimal gap at 10-20%
of that, so intervals are fixed rather than fitted. ponytail: a 5-element list
beats a dependency with 21 trained weights we have no data to fit.
"""

import ast
import hashlib
import json
import os
import random
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).parent
EXDIR = ROOT / "exercises"
STATE = ROOT / "progress.json"

LADDER = [2, 4, 8, 16, 28]           # days until the next sighting, per box
INTERVIEW = date(2026, 11, 2)        # everything recycles before this
NEW_PER_DAY = 2
GRADES = {"fail": -2, "struggled": 0, "pass": +1, "easy": +2}
HINT_GAP = 60                        # active seconds between hints, times the level
SOLUTION_GATE = (3, 600)             # attempts, active seconds


class Invalid(Exception):
    """A rejected edit. line/col are 1-based editor coordinates when known."""

    def __init__(self, msg, line=None, col=None):
        super().__init__(msg)
        self.msg, self.line, self.col = msg, line, col


class Gated(Exception):
    """A hint (or the solution) that has not been earned yet."""

    def __init__(self, wait_secs=0):
        super().__init__(f"wait {wait_secs}s")
        self.wait_secs = wait_secs


# ---------------------------------------------------------------- state
def load():
    st = json.loads(STATE.read_text()) if STATE.exists() else {}
    return {"focus": None, "cards": {}, "open": {}, "log": [], "archive": {}, **st}


def save(st):
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(st, indent=1))
    os.replace(tmp, STATE)          # atomic: a crash mid-write can't eat months of progress


def today():
    return date.today().isoformat()


def card(st, slug):
    return st["cards"].setdefault(slug, {"box": 0, "due": today(), "seen": 0})


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


def has_given(body):
    """True when the region has code above solve() that the learner must keep."""
    tree = ast.parse(body)
    above = tree.body[:tree.body.index(_solve(tree))]
    return any(not isinstance(n, (ast.Import, ast.ImportFrom)) for n in above)


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


# ---------------------------------------------------------------- catalogue
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
    return block if block and block[0].strip().startswith("READ FIRST") else []


def exercises():
    """{slug: META + path, hints, read_first, region_start, hints_line}.

    ast only: a half-edited file is skipped instead of breaking the menu, and
    nothing in exercises/ is ever imported into this process."""
    out = {}
    for path in sorted(EXDIR.glob("ex_*.py")):
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


def _solution(path):
    txt = path.read_text()
    marker = "def _reference("
    return txt[txt.index(marker):].split("\ndef test_")[0].strip()


# ---------------------------------------------------------------- scheduler
def due_today(st, exs):
    return [s for s in exs if card(st, s)["seen"] > 0 and card(st, s)["due"] <= today()]


def unseen(st, exs):
    """Unstarted exercises whose prereqs are cleared. Under a focus tag, prereqs
    outside the tag are ignored — else a track stalls on an exercise it lacks."""
    focus = st.get("focus")
    by_topic = {m["topic"]: s for s, m in exs.items()}
    ready = []
    for slug, meta in exs.items():
        if card(st, slug)["seen"] or (focus and focus not in meta.get("tags", [])):
            continue
        prereqs = [by_topic[p] for p in meta.get("prereqs", []) if p in by_topic]
        if focus:
            prereqs = [s for s in prereqs if focus in exs[s].get("tags", [])]
        if all(card(st, s)["box"] >= 1 for s in prereqs):
            ready.append(slug)
    return ready


def queue(st, exs):
    """Today: every due review (most overdue first), then the new picks left."""
    done_today = sum(1 for e in st["log"] if e["date"] == today() and e["new"])
    fresh = sorted((s for s in unseen(st, exs) if s not in st["open"]),
                   key=lambda s: exs[s]["topic"])
    return {"review": sorted(due_today(st, exs), key=lambda s: card(st, s)["due"]),
            "new": fresh[:max(0, NEW_PER_DAY - done_today)],
            "done_today": done_today}


def pick(st, exs):
    """The one suggestion. Interleaved by construction: due dates scatter topics."""
    q = queue(st, exs)
    for kind in ("review", "new"):
        if q[kind]:
            return q[kind][0], kind
    return None, None


def grade_of(attempts, secs, par, solution_shown):
    if solution_shown:
        return "struggled"          # a peeked answer never promotes (Aleven: hint abuse)
    if attempts == 1 and secs < par * 60:
        return "easy"
    if attempts <= 2 and secs < par * 60 * 2:
        return "pass"
    return "struggled"


def reschedule(c, grade):
    c["box"] = max(0, min(len(LADDER) - 1, c["box"] + GRADES[grade]))
    gap = LADDER[c["box"]]
    nxt = date.today() + timedelta(days=gap)
    cutoff = INTERVIEW - timedelta(days=7)
    c["due"] = min(nxt, cutoff).isoformat()
    return (min(nxt, cutoff) - date.today()).days


# ---------------------------------------------------------------- attempts
def touch(o):
    """Active seconds only: a gap longer than two minutes was a break, not work."""
    now = datetime.now()
    o["active"] += int(min((now - datetime.fromisoformat(o["last"])).total_seconds(), 120))
    o["last"] = now.isoformat()
    return o["active"]


def open_attempt(st, slug):
    """The attempt is the timer: it lives from the first open until the pass.
    The file is already a stub, so nothing is written here."""
    o = st["open"].get(slug)
    if o:
        touch(o)
        return o
    now = datetime.now().isoformat()
    st["open"][slug] = {"seed": random.randint(1000, 9999), "attempts": 0, "hints": 0,
                        "new": card(st, slug)["seen"] == 0, "started": now, "last": now,
                        "active": 0, "solution_shown": False}
    return st["open"][slug]


def record_pass(st, slug, meta, code):
    """Grade, reschedule, log and archive a pass; return (grade, gap_days, box).
    The caller writes stub(body) back to the file."""
    o = st["open"][slug]
    touch(o)
    c = card(st, slug)
    grade = grade_of(o["attempts"], o["active"], meta["minutes"], o["solution_shown"])
    gap = reschedule(c, grade)
    c["seen"] += 1
    st["log"].append({"date": today(), "slug": slug, "grade": grade,
                      "attempts": o["attempts"], "secs": o["active"], "new": o["new"]})
    st["archive"].setdefault(slug, []).append({"date": today(), "grade": grade, "code": code})
    del st["open"][slug]
    return grade, gap, c["box"]


def abandon(st, slug, disk_src):
    """Drop the attempt and return the stubbed source; keep the work if it got anywhere."""
    body = cut(disk_src).body
    stubbed = stub(body)
    if body.strip() != stubbed.strip():
        st["archive"].setdefault(slug, []).append(
            {"date": today(), "grade": "abandoned", "code": strip_spec(body).editor})
    st["open"].pop(slug, None)
    return splice(disk_src, stubbed)


def next_hint(st, slug, hints):
    """Hints cost active time — clicking through them teaches nothing."""
    o = st["open"][slug]
    level = o["hints"]
    if level >= len(hints):
        raise Gated(0)                              # exhausted: the solution is the next step
    wait = HINT_GAP * (level + 1) - o["active"]
    if level and wait > 0:
        raise Gated(int(wait))
    o["hints"] += 1
    return level + 1, hints[level]


def unlock_solution(st, slug):
    """The answer opens only after real effort, and marks the attempt as peeked."""
    o = st["open"][slug]
    attempts, secs = SOLUTION_GATE
    if o["attempts"] < attempts or o["active"] < secs:
        return False
    o["solution_shown"] = True
    return True


# ---------------------------------------------------------------- running tests
_FILE_LINE = re.compile(r"[\w./\\-]*\.py:(\d+)")


def run_tests(path, seed):
    """Exercise code only ever runs here, in its own process."""
    cmd = [sys.executable, "-m", "pytest", str(path), "-x", "-q", "--no-header",
           "--timeout=10", "-p", "no:cacheprovider"]
    try:
        r = subprocess.run(cmd, env={**os.environ, "STUDY_SEED": str(seed)}, cwd=ROOT,
                           capture_output=True, text=True, check=False, timeout=60)
    except subprocess.TimeoutExpired:
        return False, "timed out after 60s — an endless loop, most likely"
    return r.returncode == 0, r.stdout


def summarise(out, region_start, doc_offset, hints_line):
    """pytest output for the browser: the assertion lines, in editor coordinates."""
    # ponytail: the last docstring line, under-counted when code sits above solve() — but
    # only by lines inside the docstring itself, which never appear in a traceback
    doc_end = region_start + doc_offset

    def editor_line(m):
        n = int(m.group(1))
        if not region_start <= n < hints_line:
            return m.group(0)             # a frame in the test or the machinery: leave it alone
        return f"line {n - region_start + 1 - (doc_offset if n > doc_end else 0)}"

    text = _FILE_LINE.sub(editor_line, out)
    lines = text.split("\n")
    head = [ln for ln in lines if ln.startswith("E   ")][:6]
    return {"headline": head or [ln for ln in lines if ln.startswith(("FAILED", "ERROR"))][:6],
            "output": text[-8192:]}


def _reference_call(body):
    """solve()'s own signature, wired straight to the reference answer."""
    fn = _solve(ast.parse(body))
    a = fn.args
    args = [p.arg for p in a.posonlyargs + a.args]
    args += [f"*{a.vararg.arg}"] if a.vararg else []
    args += [f"{p.arg}={p.arg}" for p in a.kwonlyargs]
    args += [f"**{a.kwarg.arg}"] if a.kwarg else []
    stubbed = stub(body)
    return stubbed[:stubbed.rindex("raise NotImplementedError")] + f"return _reference({', '.join(args)})"


def selfcheck():
    """Does the whole set still work? Solve every exercise with its own _reference.
    Returns the number of failures."""
    exs = exercises()
    made = []
    try:
        for slug, meta in exs.items():
            src = meta["path"].read_text()
            path = EXDIR / f"_selfcheck_{slug}.py"
            path.write_text(splice(src, _reference_call(cut(src).body)))
            made.append(path)
        r = subprocess.run([sys.executable, "-m", "pytest", *map(str, made), "-q", "--no-header",
                            "--timeout=60", "-p", "no:cacheprovider"],
                           cwd=ROOT, capture_output=True, text=True, check=False)
    finally:
        for path in made:
            path.unlink(missing_ok=True)
    failed = sorted({ln.split("_selfcheck_", 1)[-1].split(".py")[0]
                     for ln in r.stdout.split("\n") if ln.startswith(("FAILED", "ERROR"))})
    if r.returncode and not failed:
        print(r.stdout[-2000:].strip() or "pytest did not run")
        return 1
    for slug in failed:
        print("FAILED", slug)
    print(f"{len(exs) - len(failed)}/{len(exs)} ok")
    return len(failed)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "serve"
    if cmd == "selfcheck":
        raise SystemExit(1 if selfcheck() else 0)
    if cmd != "serve":
        raise SystemExit("usage: study.py [serve|selfcheck]")
    try:
        from web import serve  # lazy: the core must not depend on the web layer
    except ImportError as err:
        raise SystemExit(f"no web UI yet ({err}) — try: uv run study.py selfcheck") from None
    serve()


if __name__ == "__main__":
    main()
