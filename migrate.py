#!/usr/bin/env python3
"""One-off: fold rsample_drill/ into exercises/ as a single tagged catalogue.

Run once, verify, commit, delete. Nothing here is imported by the app.
"""

import ast
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import study

ROOT = Path(__file__).parent
EX = ROOT / "exercises"
ECO = ROOT / "rsample_drill"

# rsample stem -> general file it is a copy of
COPIES = {
    "ex_01_sortkey": "ex_009_sortkey.py",
    "ex_02_sets": "ex_022_sets.py",
    "skipped_ex_03_regex": "ex_029_regex.py",
    "ex_04_typehints": "ex_016_typehints.py",
    "ex_05_decorators": "ex_012_decorators.py",
    "ex_06_contextmanager": "ex_013_contextmanager.py",
    "ex_07_concurrency": "ex_055_concurrency.py",
    "ex_08_asyncio": "ex_056_asyncio.py",
    "ex_13_mock": "ex_059_mock.py",
    "ex_17_whattotest": "ex_061_whattotest.py",
}

# rsample stem -> (new exercises/ filename, topic, prereqs)
ORIGINALS = {
    "ex_09_await_under_lock": ("ex_094_await_under_lock.py", 94, [56]),
    "ex_10_semaphore": ("ex_095_semaphore.py", 95, [56]),
    "ex_11_async_cm": ("ex_096_async_cm.py", 96, [13, 56]),
    "ex_12_lazy_init_lock": ("ex_097_lazy_init_lock.py", 97, [56, 95]),
    "ex_14_fixtures": ("ex_098_fixtures.py", 98, [59]),
    "ex_15_asgi_test": ("ex_099_asgi_test.py", 99, [98]),
    "ex_16_rerank": ("ex_100_rerank.py", 100, [9, 22, 29]),
    "ex_18_explain_takehome": ("ex_101_explain_takehome.py", 101, [94, 100]),
}

# rsample stem -> the line from rsample_drill/README.md's "in the take-home" column
TAKEHOME = {
    "ex_01_sortkey": "`sorted(rows, key=score)` in main.py",
    "ex_02_sets": "`query_words & content_words` in reranker.py",
    "skipped_ex_03_regex": "`_tokenize` in reranker.py",
    "ex_04_typehints": "required on every signature",
    "ex_05_decorators": '`@app.get("/search")`, `@pytest.fixture`',
    "ex_06_contextmanager": "the sync half of `async with pool.acquire()`",
    "ex_07_concurrency": '"why async here?"',
    "ex_08_asyncio": "`loadtest.py`, your concurrency test",
    "ex_09_await_under_lock": "`embed_query` outside `pool.acquire()`",
    "ex_10_semaphore": "why `FakePool` is a `Semaphore(max_size)`",
    "ex_11_async_cm": "your `tests/test_search.py`",
    "ex_12_lazy_init_lock": "`app/db.py` (given — you must explain it)",
    "ex_13_mock": "`monkeypatch.setattr(...)`",
    "ex_14_fixtures": "what the README asked and you skipped",
    "ex_15_asgi_test": "`httpx.ASGITransport(app=app)`",
    "ex_16_rerank": 'Task 2 + the "fraction, not count" upgrade',
    "ex_17_whattotest": "Task 3 judgement",
    "ex_18_explain_takehome": "the interview",
}

SECTIONS = [
    (range(1, 18), "core"),
    (range(18, 26), "data-structures"),
    (range(26, 35), "files-text"),
    (range(35, 43), "stdlib-ops"),
    ([*range(43, 48), 81], "errors"),
    (range(48, 54), "http"),
    (range(54, 57), "concurrency"),
    (range(57, 62), "testing"),
    (range(62, 68), "packaging"),
    (range(68, 73), "cloud"),
    ([*range(73, 81), *range(82, 87)], "whole-task"),
    (range(88, 94), "llm"),
    (range(94, 98), "concurrency"),
    (range(98, 100), "testing"),
    (range(100, 102), "whole-task"),
]

LIBS = {"boto3": "boto3", "moto": "boto3", "requests": "requests", "responses": "requests",
        "langchain_core": "langchain", "fastapi": "fastapi", "httpx": "fastapi",
        "asyncio": "asyncio"}


def git(*args):
    subprocess.run(["git", *args], cwd=ROOT, check=True)


def clean():
    lines = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                           capture_output=True, text=True, check=True).stdout.split("\n")
    out = "\n".join(ln for ln in lines if ln.strip() and not ln.endswith("migrate.py"))
    if out:
        sys.exit(f"refusing to migrate a dirty tree:\n{out}")


# ---------------------------------------------------------------- READ FIRST block
def rf_span(src):
    """(line after the module docstring, start, end) of the READ FIRST block.

    start/end are None when the file has no such block. Indexes are 0-based
    into src.split("\\n"), end exclusive — the same block study.read_first reads.
    """
    tree = ast.parse(src)
    lines = src.split("\n")
    doc_end = tree.body[0].end_lineno if tree.body and study._str_expr(tree.body[0]) else 0
    at = doc_end
    while at < len(lines) and not lines[at].strip():
        at += 1
    end = at
    while end < len(lines) and lines[end].startswith("#"):
        end += 1
    if end > at and lines[at].lstrip("# ").startswith("READ FIRST"):
        return doc_end, at, end
    return doc_end, None, None


def takehome_line(stem):
    return f"#   TAKE-HOME: {TAKEHOME[stem]}"


def append_takehome(src, stem):
    """Add the TAKE-HOME line at the end of the file's own READ FIRST block."""
    _, start, end = rf_span(src)
    assert start is not None, "expected a READ FIRST block"
    lines = src.split("\n")
    return "\n".join(lines[:end] + [takehome_line(stem)] + lines[end:])


def graft_read_first(general_src, copy_src, stem):
    """Move the copy's READ FIRST block onto the general file, plus TAKE-HOME."""
    doc_end, start, end = rf_span(copy_src)
    assert start is not None, stem
    block = [ln for ln in copy_src.split("\n")[start:end] if "copy of" not in ln]
    block.append(takehome_line(stem))

    doc_end, own_start, _ = rf_span(general_src)
    assert own_start is None, "general file already has a READ FIRST block — merge by hand"
    lines = general_src.split("\n")
    at = doc_end
    while at < len(lines) and not lines[at].strip():
        at += 1                                  # swallow the blank lines, put one back below
    return "\n".join(lines[:doc_end] + block + [""] + lines[at:])


# ---------------------------------------------------------------- META surgery
def _meta(src):
    return study._assign(ast.parse(src), "META").value


def _cut(line, col):
    """(before, after) around an ast column — which is a UTF-8 byte offset, not a char one."""
    b = line.encode()
    return b[:col].decode(), b[col:].decode()


def set_meta(src, key, value_src):
    """Replace one single-line META value in place."""
    d = _meta(src)
    for k, v in zip(d.keys, d.values, strict=True):
        if k.value == key:
            assert v.lineno == v.end_lineno, f"{key} spans lines"
            lines = src.split("\n")
            ln = lines[v.lineno - 1]
            lines[v.lineno - 1] = _cut(ln, v.col_offset)[0] + value_src + _cut(ln, v.end_col_offset)[1]
            return "\n".join(lines)
    raise KeyError(key)


def add_tags(src, tags):
    """Insert `"tags": [...]` as META's last key, keeping the file readable."""
    d = _meta(src)
    assert not any(k.value == "tags" for k in d.keys), "already tagged"
    lines = src.split("\n")
    last = d.values[-1]
    i = last.end_lineno - 1
    before, after = _cut(lines[i], last.end_col_offset)
    entry = f'"tags": {json.dumps(tags)}'
    inline = f"{before}, {entry}{after}"
    if lines[d.end_lineno - 1].strip() == "}" or len(inline) > 100:
        indent = re.match(r"\s*", lines[i]).group(0) or "    "
        lines[i:i + 1] = [before + ",", indent + entry + after]
    else:
        lines[i] = inline
    out = "\n".join(lines)
    meta = ast.literal_eval(_meta(out))            # parses, and is still a literal dict
    assert meta["tags"] == tags and list(meta)[-1] == "tags"
    return out


def tags_for(topic, src, rsample):
    section = next(name for span, name in SECTIONS if topic in span)
    libs = set()
    for node in ast.parse(src).body:
        if isinstance(node, ast.Import):
            libs |= {LIBS[a.name.split(".")[0]] for a in node.names
                     if a.name.split(".")[0] in LIBS}
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            root = node.module.split(".")[0]
            if root in LIBS:
                libs.add(LIBS[root])
    return [section, *sorted(libs)] + (["rsample"] if rsample else [])


# ---------------------------------------------------------------- state
def new_state(copy_src):
    """Root progress.json, rebuilt from rsample_drill's."""
    old = json.loads((ECO / "progress.json").read_text())
    slug_of = {stem: COPIES[stem].removesuffix(".py") for stem in COPIES}
    slug_of["ex_03_regex"] = COPIES["skipped_ex_03_regex"].removesuffix(".py")
    now = datetime.now().isoformat()             # noqa: DTZ005 — local clock, like study.py
    cards, archive = {}, {}
    for stem, c in old["cards"].items():
        if c["seen"] > 0:
            cards[slug_of[stem]] = {"box": c["box"], "due": c["due"], "seen": c["seen"]}
    log = []
    for entry in old["log"]:
        slug = slug_of[entry["slug"]]
        log.append({**entry, "slug": slug})
        archive.setdefault(slug, []).append({
            "date": entry["date"], "grade": entry["grade"],
            "code": study.strip_spec(study.cut(copy_src[entry["slug"]]).body).editor})
    return {"focus": None, "cards": cards,
            "open": {"ex_016_typehints": {"seed": 4357, "attempts": 0, "hints": 0, "new": True,
                                          "started": now, "last": now, "active": 0,
                                          "solution_shown": False}},
            "log": log, "archive": archive}


def draft_ex_016(copy_src):
    """ex_04's half-solved body, moved onto the general file through the write gate."""
    path = EX / "ex_016_typehints.py"
    disk = path.read_text()
    spec = study.strip_spec(study.cut(disk).body)
    eco_body = study.cut(copy_src).body
    fn = study._solve(ast.parse(eco_body))
    rest = eco_body.split("\n")[study._docstring(fn).end_lineno:]
    head = spec.editor.split("\n")[:-1]           # the general signature, minus the `raise`
    edited = "\n".join([*head, "    from typing import get_type_hints", *rest])
    study.write_region(path, study.validate(edited, spec.spec_src, disk))


# ---------------------------------------------------------------- run
def main():
    clean()
    copy_src = {p.stem: p.read_text() for p in ECO.glob("*ex_*.py")}

    git("mv", "exercises/ex_070_ebscleanup.py", "exercises/ex_072_ebscleanup.py")
    for stem, (name, topic, prereqs) in ORIGINALS.items():
        git("mv", f"rsample_drill/{stem}.py", f"exercises/{name}")
        path = EX / name
        src = append_takehome(path.read_text(), stem)
        src = set_meta(src, "topic", str(topic))
        path.write_text(set_meta(src, "prereqs", json.dumps(prereqs)))

    for stem, name in COPIES.items():
        path = EX / name
        path.write_text(graft_read_first(path.read_text(), copy_src[stem], stem))

    draft_ex_016(copy_src["ex_04_typehints"])

    rsample = {COPIES[s] for s in COPIES} | {name for name, _, _ in ORIGINALS.values()}
    for path in sorted(EX.glob("ex_*.py")):
        src = path.read_text()
        topic = ast.literal_eval(_meta(src))["topic"]
        path.write_text(add_tags(src, tags_for(topic, src, path.name in rsample)))

    study.save(new_state(copy_src))
    git("rm", "-r", "-q", "rsample_drill")
    shutil.rmtree(ECO, ignore_errors=True)       # __pycache__ is untracked, git rm leaves it
    print("migrated:", len(list(EX.glob("ex_*.py"))), "exercises")


if __name__ == "__main__":
    main()
