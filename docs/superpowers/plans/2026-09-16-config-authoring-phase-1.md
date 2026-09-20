# Config authoring phase 1 implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A learner opens an empty YAML editor on a fixture task, reads requirements that were generated in a sandbox and persisted on the attempt, types a Kubernetes Deployment, and gets strict schema and semantic feedback through the existing output panel, all the way through pass, archive and reset.

**Architecture:** A second task kind alongside Python. One new module, `kinds.py`, is the platform seam: a kind owns its filename, its editor language, the learner's text inside its file, what a folder of that kind must contain, what opening an attempt on it produces, and how it is graded. Every lifecycle consumer asks the kind instead of branching on its name. Task-authored Python (`brief()`, `check()`) only ever executes inside the existing sandboxed pytest child, never in the server. Grading is `kubeconform` against packaged offline schemas, then plain asserts against the brief that was persisted when the attempt opened.

**Tech Stack:** Python 3.14, FastAPI, pytest, pyyaml and requests (both already runtime dependencies), kubeconform (pinned Go binary fetched by `drillion doctor`), Monaco via `@codingame/monaco-vscode-standalone-languages`, React 19.

**Spec:** `docs/superpowers/specs/2026-09-16-config-authoring-design.md`

## Global Constraints

- Python floor is `>=3.14`. The repo runs on 3.14.
- No new runtime dependencies. `pyyaml>=6.0.3` and `requests>=2.34.2` are already in `[project] dependencies`.
- `uv run ruff check` and `uv run ruff format --check` must pass. `tasks/**` is excluded from formatting and must stay excluded.
- Task-authored code never executes in the server process. `brief()` and `check()` run only inside `sandbox.run`.
- Grading never reaches the network. Landlock denies TCP; schemas are packaged, not downloaded.
- The fixture task lives under `tests/`, never under `tasks/`, for this entire phase. `runner.selfcheck()` walks the real catalogue on every OS in CI, and a manifest in `tasks/` before phase 2 turns that red.
- Conventional commit titles with a scope: `feat(artifact): ...`, `fix(state): ...`.
- Commits are signed. Do not pass `--no-gpg-sign`.
- Every task ends green on `uv run pytest tests/ -q`, not only on its own new test.

---

## Platform shape

drillion is the platform; Python and Kubernetes are kinds that plug into it. A third kind
(Helm, Compose, Terraform) must be a new class in `kinds.py` plus a task-folder convention,
never a seventh pass through the same six modules.

The rule for this plan: **kind-specific behavior lives on the kind.** Any consumer that
would write `if meta["kind"] == MANIFEST` calls a method on `kinds.of(meta)` instead. There
are exactly two places a kind name is compared to a literal, both of them in `kinds.py`
itself: the `KINDS` registry, and `of()`.

This costs nothing now. It is the same code in a different file, and it is what makes the
third kind cheap.

`kinds.py` imports `runner` and `manifest` inside the methods that need them rather than at
module scope, because both import `kinds`. The codebase already does this where a cycle
would otherwise form; `sandbox.run` importing `winsandbox` inside the function is the
precedent to follow.

---

## File Structure

**New:**
- `src/drillion/kinds.py` - the platform seam. Two kinds, one shape. Owns filename, editor language, required folder contents, body extraction, composition, validation, empty state, etag, attempt opening, the spec served, and grading.
- `src/drillion/tools.py` - pinned external graders: the pin table, verification, acquisition, and resolving an installed binary.
- `src/drillion/manifest.py` - everything specific to grading a manifest: generating a brief in a child, rendering a template, and building the pytest harness.
- `src/drillion/_schemas/` - packaged Kubernetes JSON schemas plus `manifest.json` recording version and digest.
- `tests/fixtures_manifest.py` - the fixture manifest task used by every test in this phase.
- `tests/test_kinds.py`, `tests/test_tools.py`, `tests/test_manifest.py`, `tests/test_manifest_e2e.py`.

**Modified:**
- `src/drillion/catalogue.py` - `kind` frontmatter, conditional required fields, `kind` and `filename` in `public()`.
- `src/drillion/state.py` - pending resets keyed by kind and relative path; `DB_SCHEMA` bump and migration.
- `src/drillion/cli.py` - `seed()` preserves any learner-owned file, not just `task.py`.
- `src/drillion/sandbox.py` - tools and schema directories readable and executable.
- `src/drillion/runner.py` - `run_tests` dispatches by kind.
- `src/drillion/attempts.py` - the brief and rendered spec persist on the attempt.
- `src/drillion/api.py` - `_payload` and the run route go through the adapter.
- `src/drillion/doctor.py` - a tools section, and value rules conditional on kind.
- `web/src/api.ts`, `web/src/Editor.tsx`, `web/src/Task.tsx` - optional `tier`, YAML models, no Python LSP on a manifest, no case panel on a manifest.
- `pyproject.toml` - package `_schemas` into wheel and sdist.

---

### Task 1: The `kind` frontmatter and conditional catalogue rules

A manifest task has no Python tier. `catalogue.REQUIRED` demands one from every folder today, so a manifest README is rejected before anything else can be built.

**Files:**
- Modify: `src/drillion/catalogue.py:22` (`REQUIRED`, `BROWSER`), `src/drillion/catalogue.py:107` (`_read`)
- Modify: `src/drillion/doctor.py:12` (`_value_rules`)
- Test: `tests/test_catalogue.py`, `tests/test_doctor.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `catalogue.PYTHON = "python"`, `catalogue.MANIFEST = "manifest"`, `catalogue.KINDS = (PYTHON, MANIFEST)`. Every `TaskMeta` carries `meta["kind"]`, defaulted to `"python"`. `catalogue.public(meta)` includes `kind`.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_catalogue.py`:

```python
def test_kind_defaults_to_python_and_manifest_needs_no_tier():
    keep = settings.root
    manifest_readme = README.replace("tier: core\n", "").replace(
        "difficulty: easy", "kind: manifest\ndifficulty: easy"
    )
    tmp = tasks_root(
        **{
            "042_thing": {"README.md": README, "task.py": TASK},
            "043_manifest": {"README.md": manifest_readme, "task.yaml": ""},
        }
    )
    try:
        settings.root = tmp
        found = catalogue.tasks()
        assert found["042_thing"]["kind"] == "python"
        assert found["043_manifest"]["kind"] == "manifest"
        assert "tier" not in found["043_manifest"]
        assert catalogue.public(found["043_manifest"])["kind"] == "manifest"
    finally:
        settings.root = keep
        shutil.rmtree(tmp, ignore_errors=True)


def test_an_unknown_kind_is_rejected_by_name():
    keep = settings.root
    bad = README.replace("difficulty: easy", "kind: terraform\ndifficulty: easy")
    tmp = tasks_root(**{"044_bad": {"README.md": bad, "task.py": TASK}})
    try:
        settings.root = tmp
        why = dict((name, reasons) for name, _, reasons in catalogue.scan())
        assert any("terraform" in r for r in why["044_bad"])
    finally:
        settings.root = keep
        shutil.rmtree(tmp, ignore_errors=True)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_catalogue.py::test_kind_defaults_to_python_and_manifest_needs_no_tier -v`
Expected: FAIL. The manifest folder is dropped because `tier` is missing and `task.py` does not exist.

- [ ] **Step 3: Write the implementation**

In `src/drillion/catalogue.py`, replace the `REQUIRED` constant and add the kind constants:

```python
PYTHON = "python"
MANIFEST = "manifest"
KINDS = (PYTHON, MANIFEST)
# what every task needs, then what each kind adds. `tier` is Python depth and a manifest
# reaches nowhere into the language, so it is not asked of one.
REQUIRED = ("title", "difficulty", "minutes", "tags")
REQUIRED_BY_KIND = {PYTHON: ("tier",), MANIFEST: ()}
BROWSER = ("topic", "title", "difficulty", "tier", "track", "tags", "source", "kind")
```

In `_read`, resolve the kind before the per-kind file checks and use it for the required-field loop. Replace the `src = folder / "task.py"` block with a kind-aware one:

```python
    readme = folder / "README.md"
    ...  # frontmatter parsing is unchanged and still runs first
    kind = meta.get("kind", PYTHON)
    if kind not in KINDS:
        out.append(f"README.md: kind {kind!r} is not one of {' / '.join(KINDS)}")
        kind = PYTHON
    out += [
        f"README.md: frontmatter is missing `{k}`"
        for k in (*REQUIRED, *REQUIRED_BY_KIND[kind])
        if meta.get(k) in (None, "", [])
    ]
```

Move the existing `task.py` validation into a named function and register one per kind, so a
third kind adds a function and a dict entry rather than another branch. `catalogue` cannot
import `kinds` (that module imports these constants), so the registry lives here as data:

```python
def _check_python(folder):
    """Every rule a python task folder must pass. The body is the existing checks, moved."""
    out = []
    src = folder / "task.py"
    if not src.is_file():
        return ["task.py: missing"]
    ...  # the existing bounds/cut/_solve/_reference checks, unchanged
    return out


def _check_manifest(folder):
    """A manifest task is four files: the learner's, the grader's, and the reference."""
    return [
        f"{name}: missing"
        for name in ("task.yaml", "grade.py", "solution.yaml")
        if not (folder / name).is_file()
    ]


CHECKS = {PYTHON: _check_python, MANIFEST: _check_manifest}
```

`_read` then calls `out += CHECKS[kind](folder)` where the `task.py` block used to be.

Set `"kind": kind` in the returned record, and add `kind: str` to `TaskMeta`.

In `src/drillion/doctor.py`, make the tier rule conditional so a manifest is not asked for one:

```python
    tier = meta.get("tier")
    if meta.get("kind", "python") == "python":
        if tier is not None and tier not in TIERS:
            out.append(f"README.md: tier {tier!r} is not one of {' / '.join(TIERS)}")
    elif tier is not None:
        out.append("README.md: tier belongs to a python task, not a manifest")
```

- [ ] **Step 4: Run the tests**

Run: `uv run pytest tests/test_catalogue.py tests/test_doctor.py -q`
Expected: PASS, including the existing suites. Every task in `tasks/` keeps working because `kind` defaults to `python`.

- [ ] **Step 5: Run the full suite and lint**

Run: `uv run pytest tests/ -q && uv run ruff check && uv run ruff format --check`
Expected: all green.

- [ ] **Step 6: Commit**

```bash
git add src/drillion/catalogue.py src/drillion/doctor.py tests/test_catalogue.py tests/test_doctor.py
git commit -m "feat(catalogue): read a task's kind and ask each kind for its own fields"
```

---

### Task 2: The learner-artifact adapter, Python only

Introduce the boundary with one implementation and no behavior change. This task is pure refactoring: every existing test must pass untouched.

**Files:**
- Create: `src/drillion/kinds.py`
- Test: `tests/test_kinds.py`

**Interfaces:**
- Consumes: `catalogue.PYTHON`, `catalogue.MANIFEST` from Task 1.
- Produces: `kinds.of(meta) -> Kind`. A `Kind` has attributes `name: str`, `filename: str`, `language: str` and methods `path(meta) -> Path`, `body(src) -> str`, `compose(src, body) -> str`, `validate(edited, src) -> str`, `empty(src) -> str`, `etag(src) -> str`, plus the three platform-seam methods every consumer calls instead of branching: `opening(meta, seed) -> dict` (extra attempt state), `spec(meta, o) -> str` (the guidance to serve), and `grade(meta, o) -> tuple[bool, str, dict | None]`. `kinds.Invalid` is re-exported from `region` so callers catch one exception type.
- Note: `opening`, `spec` and `grade` are defined in this task with their Python behavior and are filled in for the manifest kind by Tasks 11, 12 and 13. Do not add a manifest branch to `attempts`, `runner` or `api` in those tasks.

- [ ] **Step 1: Write the failing test**

Create `tests/test_kinds.py`:

```python
"""The learner-artifact boundary: what a kind says about the learner's own text."""

from drillion import kinds, region
from tests.fixtures import TASK

META = {"kind": "python", "dir": None}


def test_python_body_is_the_region_above_the_marker():
    k = kinds.of(META)
    assert k.name == "python" and k.filename == "task.py" and k.language == "python"
    assert k.body(TASK) == region.cut(TASK).body
    assert "_reference" not in k.body(TASK)


def test_python_compose_round_trips():
    k = kinds.of(META)
    assert k.compose(TASK, k.body(TASK)) == TASK


def test_python_empty_is_the_stub_not_an_empty_file():
    k = kinds.of(META)
    emptied = k.empty(TASK.replace("raise NotImplementedError", "return x"))
    assert "raise NotImplementedError" in emptied
    assert region.MARKER in emptied


def test_python_etag_ignores_the_machinery():
    k = kinds.of(META)
    moved = TASK.replace("return x", "return x  # changed")
    assert k.etag(TASK) != k.etag(moved.replace("def solve(x)", "def solve(y)"))
    assert k.etag(TASK) == region.etag(TASK)


def test_an_unknown_kind_raises_rather_than_guessing():
    try:
        kinds.of({"kind": "terraform"})
    except KeyError:
        return
    raise AssertionError("an unknown kind must not silently fall back to python")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_kinds.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'drillion.artifact'`.

- [ ] **Step 3: Write the implementation**

Create `src/drillion/kinds.py`:

```python
"""The learner's own text, whatever kind of task it lives in.

A Python task's artifact is the region above the marker in `task.py`; a manifest task's is
the whole of `task.yaml`. Everything that reads, writes, resets, archives or fingerprints
a learner's work asks a kind rather than calling `region` directly."""

from . import region
from .catalogue import MANIFEST, PYTHON
from .region import Invalid

__all__ = ["Invalid", "of"]


class _Python:
    """The original artifact: a region inside a file it shares with the grader."""

    name = PYTHON
    filename = "task.py"
    language = "python"

    def path(self, meta):
        return meta["dir"] / self.filename

    def body(self, src):
        return region.cut(src).body

    def compose(self, src, body):
        return region.splice(src, body)

    def validate(self, edited, src):
        return region.validate(edited, src)

    def empty(self, src):
        return region.splice(src, region.stub(region.cut(src).body))

    def etag(self, src):
        return region.etag(src)

    def opening(self, meta, seed):
        """Extra state an attempt on this kind carries. A python sitting needs none: its
        cases come from the seed at grading time, not from anything stored."""
        return {}

    def spec(self, meta, o):
        """The guidance this sitting shows. A python task's is the README as written."""
        return meta["spec_md"]

    def grade(self, meta, o):
        """(passed, pytest output, case). The one place a kind's grader is chosen."""
        from . import runner

        return runner.run_python(meta, o["seed"])


KINDS = {PYTHON: _Python()}


def of(meta):
    """The kind that owns this task's learner artifact. Raises KeyError on an unknown
    kind rather than guessing: the catalogue has already rejected those by name."""
    return KINDS[meta.get("kind", PYTHON)]
```

- [ ] **Step 4: Run the tests**

Run: `uv run pytest tests/test_kinds.py -v`
Expected: PASS.

- [ ] **Step 5: Run the full suite and lint**

Run: `uv run pytest tests/ -q && uv run ruff check && uv run ruff format --check`
Expected: all green, nothing else touched.

- [ ] **Step 6: Commit**

```bash
git add src/drillion/kinds.py tests/test_kinds.py
git commit -m "feat(artifact): add the learner-artifact boundary with the python kind"
```

---

### Task 3: Route the API through the adapter

Still no behavior change. This is the task that proves the boundary is complete enough to carry a second kind, which is why it comes before the manifest kind exists.

**Files:**
- Modify: `src/drillion/api.py:241` (`_payload`), `src/drillion/api.py:428` (`save_task`), `src/drillion/api.py:441` (`run_task`), `src/drillion/api.py:542` (`abandon_task`), `src/drillion/api.py:183` (`_check_etag`)
- Modify: `src/drillion/attempts.py:157` (`abandon`)
- Test: `tests/test_api.py`

**Interfaces:**
- Consumes: `kinds.of` from Task 2.
- Produces: no new public names. `_payload(st, slug, meta, src)` now derives `code`, `etag` and `has_given` through `kinds.of(meta)`.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_api.py`:

```python
def test_payload_reads_the_learner_text_through_the_adapter(monkeypatch):
    """A kind whose body() is identity proves the payload is not calling cut() directly."""
    from drillion import api, kinds

    calls = []

    class _Spy(kinds.KINDS["python"].__class__):
        def body(self, src):
            calls.append(src)
            return super().body(src)

    monkeypatch.setitem(kinds.KINDS, "python", _Spy())
    with api_client() as client:
        client.post("/api/task/009_fstrings/open")
        assert client.get("/api/task/009_fstrings").status_code == 200
    assert calls, "_payload must go through kinds.of(meta).body"
```

Use the existing client helper in `tests/test_api.py`; if it is named differently there, use that name rather than `api_client`.

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_api.py::test_payload_reads_the_learner_text_through_the_adapter -v`
Expected: FAIL with `AssertionError: _payload must go through kinds.of(meta).body`.

- [ ] **Step 3: Write the implementation**

In `src/drillion/api.py`, replace the direct `region` imports at the call sites. `_payload` becomes:

```python
def _payload(st, slug, meta, src):
    """Everything the task page needs, and nothing the answer lives in."""
    kind = kinds.of(meta)
    body = kind.body(src)
    ...
        "code": body,
        "etag": kind.etag(src),
        "has_given": kind.has_given(body),
```

`_check_etag(src, sent)` takes the kind:

```python
def _check_etag(kind, src, sent):
    if sent and sent != kind.etag(src):
        raise HTTPException(409, "this task changed on disk; reload before saving")
```

In `save_task`, `run_task` and `abandon_task`, replace `validate(edit.code, src)` with `kind.validate(edit.code, src)`, `write_region(meta["path"], new_src)` with `write_region(kind.path(meta), new_src)`, and `cut(new_src).body` with `kind.body(new_src)`.

In `attempts.abandon`, take the kind as a parameter instead of importing `cut`/`stub`/`splice`:

```python
def abandon(st, slug, kind, disk_src):
    """Drop the attempt and return the emptied source; keep the work if it got anywhere."""
    body = kind.body(disk_src)
    emptied = kind.empty(disk_src)
    if body.strip() != kind.body(emptied).strip():
        st["archive"].setdefault(slug, []).append(
            {"date": today(), "grade": "abandoned", "code": body}
        )
    st["open"].pop(slug, None)
    return emptied
```

Update the one caller in `api.abandon_task` to pass `kinds.of(meta)`.

- [ ] **Step 4: Run the tests**

Run: `uv run pytest tests/test_api.py tests/test_attempts.py -q`
Expected: PASS.

- [ ] **Step 5: Run the full suite and lint**

Run: `uv run pytest tests/ -q && uv run ruff check && uv run ruff format --check`
Expected: all green.

- [ ] **Step 6: Commit**

```bash
git add src/drillion/api.py src/drillion/attempts.py tests/test_api.py
git commit -m "refactor(api): reach the learner's text through the artifact boundary"
```

---

### Task 4: The manifest kind

**Files:**
- Modify: `src/drillion/kinds.py`
- Test: `tests/test_kinds.py`

**Interfaces:**
- Consumes: `kinds.KINDS` from Task 2.
- Produces: `kinds.KINDS["manifest"]`, with `filename = "task.yaml"` and `language = "yaml"`. `validate` raises `region.Invalid` with a 1-based `line` when the YAML does not parse.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_kinds.py`:

```python
MANIFEST_META = {"kind": "manifest", "dir": None}
DEPLOY = "apiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: checkout\n"


def test_manifest_body_is_the_whole_file():
    k = kinds.of(MANIFEST_META)
    assert k.name == "manifest" and k.filename == "task.yaml" and k.language == "yaml"
    assert k.body(DEPLOY) == DEPLOY
    assert k.compose(DEPLOY, "other: 1\n") == "other: 1\n"


def test_manifest_empty_is_an_empty_file():
    assert kinds.of(MANIFEST_META).empty(DEPLOY) == ""


def test_manifest_etag_covers_every_byte():
    k = kinds.of(MANIFEST_META)
    assert k.etag(DEPLOY) != k.etag(DEPLOY + "\n")


def test_manifest_validate_accepts_a_draft_and_rejects_broken_yaml():
    k = kinds.of(MANIFEST_META)
    assert k.validate(DEPLOY, "") == DEPLOY
    assert k.validate("", "") == ""  # an unfinished draft saves; grading rejects it later
    try:
        k.validate("a:\n  - b\n c: broken\n", "")
    except kinds.Invalid as err:
        assert err.line
        return
    raise AssertionError("broken YAML must be rejected on save")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_kinds.py -v -k manifest`
Expected: FAIL with `KeyError: 'manifest'`.

- [ ] **Step 3: Write the implementation**

Add to `src/drillion/kinds.py`:

```python
import hashlib

import yaml


class _Manifest:
    """The learner's artifact is the entire file: no marker, no machinery below it."""

    name = MANIFEST
    filename = "task.yaml"
    language = "yaml"

    def path(self, meta):
        return meta["dir"] / self.filename

    def body(self, src):
        return src

    def compose(self, src, body):
        return body

    def validate(self, edited, src):
        """Saving only asks that it parses. An empty file is a legal draft and a legal
        reset state; whether it is a legal *submission* is the grader's line, not this one."""
        try:
            yaml.safe_load(edited)
        except yaml.YAMLError as err:
            mark = getattr(err, "problem_mark", None)
            raise Invalid(
                getattr(err, "problem", None) or "this is not valid YAML",
                mark.line + 1 if mark else None,
            ) from None
        return edited

    def empty(self, src):
        return ""

    def etag(self, src):
        return hashlib.sha256(src.encode()).hexdigest()[:12]


KINDS = {PYTHON: _Python(), MANIFEST: _Manifest()}
```

- [ ] **Step 4: Run the tests**

Run: `uv run pytest tests/test_kinds.py -v`
Expected: PASS.

- [ ] **Step 5: Run the full suite and lint**

Run: `uv run pytest tests/ -q && uv run ruff check && uv run ruff format --check`

- [ ] **Step 6: Commit**

```bash
git add src/drillion/kinds.py tests/test_kinds.py
git commit -m "feat(artifact): add the manifest kind, whose artifact is the whole file"
```

---

### Task 5: Kind-aware pending resets and crash recovery

`state._task_path()` builds `tasks/<slug>/task.py` from the slug, `reset_after_commit()` refuses any other path, and `_recover()` calls `region.cut`/`region.splice`. A manifest cannot pass until all three are general. The stored rows change shape, so `DB_SCHEMA` goes to 2 and existing rows migrate as Python.

**Files:**
- Modify: `src/drillion/state.py:19` (`DB_SCHEMA`), `src/drillion/state.py:204` (`_task_path`), `src/drillion/state.py:219` (`reset_after_commit`), `src/drillion/state.py:228` (`_recover`), and the `pending_resets` DDL
- Test: `tests/test_state.py`, `tests/test_sqlite.py`

**Interfaces:**
- Consumes: `kinds.of` from Tasks 2 and 4.
- Produces: `reset_after_commit(st, meta, path, original, replacement)` now takes `meta` so it can resolve the kind. `st.resets[slug]` becomes `(kind_name, original_body, replacement_body)`. The `pending_resets` table gains a `kind TEXT NOT NULL` column.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_state.py`:

```python
def test_a_manifest_reset_empties_the_yaml_file(tmp_path, monkeypatch):
    from drillion import state
    from drillion.settings import settings

    folder = tmp_path / "tasks" / "271_fixture"
    folder.mkdir(parents=True)
    (folder / "task.yaml").write_text("kind: Deployment\n", encoding="utf-8")
    monkeypatch.setattr(settings, "root", tmp_path)
    meta = {"kind": "manifest", "dir": folder}

    with state.writing() as st:
        state.reset_after_commit(st, meta, folder / "task.yaml", "kind: Deployment\n", "")

    assert (folder / "task.yaml").read_text(encoding="utf-8") == ""


def test_a_legacy_pending_reset_row_still_resets_python(tmp_path, monkeypatch):
    """Rows written by DB_SCHEMA 1 carry no kind and must migrate as python."""
    from drillion import state
    from drillion.settings import settings

    monkeypatch.setattr(settings, "root", tmp_path)
    folder = tmp_path / "tasks" / "009_fstrings"
    folder.mkdir(parents=True)
    (folder / "task.py").write_text(TASK.replace("raise NotImplementedError", "return x"), encoding="utf-8")
    _write_legacy_pending_reset(tmp_path, "009_fstrings", "    return x", "    raise NotImplementedError")

    with state.writing():
        pass

    assert "raise NotImplementedError" in (folder / "task.py").read_text(encoding="utf-8")
```

Write `_write_legacy_pending_reset` in the same test module: open `settings.state_path` with `sqlite3`, set `PRAGMA user_version = 1`, create the two-column `pending_resets` table as DB_SCHEMA 1 had it, and insert the row.

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_state.py -v -k "manifest_reset or legacy_pending"`
Expected: FAIL. `reset_after_commit` takes four arguments and rejects a path that is not `task.py`.

- [ ] **Step 3: Write the implementation**

In `src/drillion/state.py`, bump the schema and widen the table:

```python
DB_SCHEMA = 2  # pending resets carry the artifact kind
```

```sql
CREATE TABLE pending_resets (
    slug TEXT PRIMARY KEY,
    kind TEXT NOT NULL DEFAULT 'python',
    original TEXT NOT NULL,
    replacement TEXT NOT NULL)
```

Add a migration that runs when `PRAGMA user_version` reads 1: `ALTER TABLE pending_resets ADD COLUMN kind TEXT NOT NULL DEFAULT 'python'`, then set `user_version = 2`. Every existing row is a Python reset, which the default expresses exactly.

Generalize the path helper, keeping every containment check it already has:

```python
def _task_path(slug, kind_name):
    """The learner's file for this task. The slug checks are unchanged: a pending reset
    is the one place a stored string becomes a path."""
    if (
        not slug
        or slug in (".", "..")
        or "/" in slug
        or "\\" in slug
        or PureWindowsPath(slug).drive
    ):
        raise Unreadable("Invalid task slug in a pending reset.")
    kind = kinds.KINDS.get(kind_name)
    if kind is None:
        raise Unreadable(f"Unknown task kind {kind_name!r} in a pending reset.")
    path = settings.tasks_dir / slug / kind.filename
    if not path.resolve().is_relative_to(settings.tasks_dir.resolve()):
        raise Unreadable("Pending task reset points outside the tasks directory.")
    return path
```

```python
def reset_after_commit(st, meta, path, original, replacement):
    """Schedule an artifact reset only after the accompanying archive is durable."""
    slug = path.parent.name
    kind = kinds.of(meta)
    if path.resolve() != _task_path(slug, kind.name).resolve():
        raise Unreadable("Pending reset is not a task file.")
    st.resets[slug] = (kind.name, kind.body(original), kind.body(replacement))
```

In `_recover`, select the kind column, resolve the kind, and replace the `region` calls with `kind.body` and `kind.compose`. The "preserve an externally edited file" branch and the `FileNotFoundError` branch keep their exact current behavior.

Update the one caller in `api.run_task` to `reset_after_commit(st, meta, kind.path(meta), new_src, stubbed)`.

- [ ] **Step 4: Run the tests**

Run: `uv run pytest tests/test_state.py tests/test_sqlite.py -q`
Expected: PASS.

- [ ] **Step 5: Run the full suite and lint**

Run: `uv run pytest tests/ -q && uv run ruff check && uv run ruff format --check`

- [ ] **Step 6: Commit**

```bash
git add src/drillion/state.py src/drillion/api.py tests/test_state.py tests/test_sqlite.py
git commit -m "fix(state): key pending resets by artifact kind, not a task.py path"
```

---

### Task 6: `seed()` preserves every learner-owned file

`cli.seed()` merges `task.py` and `shutil.copy2` everything else. A packaged empty `task.yaml` therefore overwrites the learner's manifest on every single start, not only on upgrade. This is data loss and it must land before any manifest can be passed.

**Files:**
- Modify: `src/drillion/cli.py:23` (`_merge`), `src/drillion/cli.py:85` (`seed`)
- Test: `tests/test_seed.py`

**Interfaces:**
- Consumes: `kinds.KINDS` from Task 4.
- Produces: `cli.LEARNER_FILES = {kind.filename for kind in kinds.KINDS.values()}`.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_seed.py`:

```python
def test_seeding_never_overwrites_a_learner_manifest(tmp_path, monkeypatch):
    from drillion import cli
    from drillion.settings import settings

    template = tmp_path / "template"
    (template / "271_fixture").mkdir(parents=True)
    (template / "271_fixture" / "task.yaml").write_text("", encoding="utf-8")
    (template / "271_fixture" / "README.md").write_text("shipped\n", encoding="utf-8")
    monkeypatch.setattr(cli, "TASKS_TEMPLATE", template)
    monkeypatch.setattr(settings, "root", tmp_path / "root")

    cli.seed()
    mine = settings.tasks_dir / "271_fixture" / "task.yaml"
    mine.write_text("kind: Deployment\n", encoding="utf-8")
    cli.seed()

    assert mine.read_text(encoding="utf-8") == "kind: Deployment\n"
    assert (settings.tasks_dir / "271_fixture" / "README.md").read_text(encoding="utf-8") == "shipped\n"


def test_seeding_keeps_an_intentionally_empty_manifest(tmp_path, monkeypatch):
    """An empty file is the start state and also a legal learner state. Either way it is
    theirs, and seeding must not treat 'empty' as 'absent'."""
    from drillion import cli
    from drillion.settings import settings

    template = tmp_path / "template"
    (template / "271_fixture").mkdir(parents=True)
    (template / "271_fixture" / "task.yaml").write_text("", encoding="utf-8")
    monkeypatch.setattr(cli, "TASKS_TEMPLATE", template)
    monkeypatch.setattr(settings, "root", tmp_path / "root")

    cli.seed()
    mine = settings.tasks_dir / "271_fixture" / "task.yaml"
    mine.write_text("", encoding="utf-8")
    before = mine.stat().st_mtime_ns
    cli.seed()
    assert mine.stat().st_mtime_ns == before
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_seed.py -v -k manifest`
Expected: FAIL. The learner's `kind: Deployment` is replaced by the packaged empty file.

- [ ] **Step 3: Write the implementation**

In `src/drillion/cli.py`, add the constant and branch on it in `seed()`:

```python
from . import kinds

# the files that belong to the learner once they exist. Everything else under tasks/ is
# drillion's and follows the installed version.
LEARNER_FILES = {kind.filename for kind in kinds.KINDS.values()}
```

```python
        if out.name == "task.py" and out.is_file():
            _merge(src, out)
        elif out.name in LEARNER_FILES and out.exists():
            continue  # theirs now, in whatever state they left it, empty included
        else:
            shutil.copy2(src, out)
```

`out.exists()` rather than `out.is_file()`, so a directory sitting where a learner file belongs is not silently overwritten either.

- [ ] **Step 4: Run the tests**

Run: `uv run pytest tests/test_seed.py -q`
Expected: PASS.

- [ ] **Step 5: Run the full suite and lint**

Run: `uv run pytest tests/ -q && uv run ruff check && uv run ruff format --check`

- [ ] **Step 6: Commit**

```bash
git add src/drillion/cli.py tests/test_seed.py
git commit -m "fix(cli): keep a learner's manifest when seeding brings tasks up to date"
```

---

### Task 7: The pin table and tool verification

Acquisition comes next; this task is only "given a file on disk, is it the grader we pinned". Verification runs before every grading run, not only after a download.

**Files:**
- Create: `src/drillion/tools.py`
- Test: `tests/test_tools.py`

**Interfaces:**
- Consumes: `settings.root`.
- Produces: `tools.PINS: dict[str, dict[tuple[str, str], Pin]]` keyed by tool name then `(platform, machine)`. `Pin` is a NamedTuple `(version, url, archive_sha256, member, binary_sha256)`. `tools.pin_for(name) -> Pin` raises `tools.Unsupported` on an unknown platform. `tools.installed(name) -> Path | None` returns the verified binary or None. `tools.digest(path) -> str`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_tools.py`:

```python
"""Pinned external graders: verified on every use, never trusted because they exist."""

import hashlib

import pytest

from drillion import tools
from drillion.settings import settings


def test_a_binary_that_does_not_match_its_pin_is_not_installed(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "root", tmp_path)
    binary = tmp_path / "tools" / "kubeconform"
    binary.parent.mkdir(parents=True)
    binary.write_bytes(b"not kubeconform")
    assert tools.installed("kubeconform") is None


def test_a_matching_binary_is_installed(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "root", tmp_path)
    binary = tmp_path / "tools" / "kubeconform"
    binary.parent.mkdir(parents=True)
    binary.write_bytes(b"pretend")
    pin = tools.pin_for("kubeconform")
    monkeypatch.setitem(
        tools.PINS["kubeconform"],
        tools.host(),
        pin._replace(binary_sha256=hashlib.sha256(b"pretend").hexdigest()),
    )
    assert tools.installed("kubeconform") == binary


def test_an_unsupported_platform_says_so(monkeypatch):
    monkeypatch.setattr(tools, "host", lambda: ("plan9", "vax"))
    with pytest.raises(tools.Unsupported):
        tools.pin_for("kubeconform")


def test_every_pin_is_filled_in():
    """A placeholder pin is a release blocker, not a TODO."""
    for name, by_host in tools.PINS.items():
        for host, pin in by_host.items():
            assert pin.version and pin.url.startswith("https://"), (name, host)
            assert len(pin.archive_sha256) == 64 and len(pin.binary_sha256) == 64, (name, host)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_tools.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'drillion.tools'`.

- [ ] **Step 3: Write the implementation**

Create `src/drillion/tools.py`:

```python
"""Pinned external graders, fetched once and verified every time.

A grader that decides whether a learner passed is part of the verdict, so its identity is
pinned by checksum rather than by version string, and checked before every run rather than
only after a download."""

import hashlib
import platform
import sys
from typing import NamedTuple

from .settings import settings

KUBECONFORM = "kubeconform"


class Unsupported(Exception):
    """No pin for this operating system and architecture."""


class Pin(NamedTuple):
    version: str
    url: str
    archive_sha256: str
    member: str  # the one file inside the archive that is the executable
    binary_sha256: str


def host():
    """(platform, machine), normalised to the names the pins are keyed by."""
    machine = platform.machine().lower()
    return sys.platform, {"x86_64": "amd64", "aarch64": "arm64"}.get(machine, machine)


PINS: dict[str, dict[tuple[str, str], Pin]] = {
    KUBECONFORM: {
        # Filled in by the release gate. Upstream publishes .tar.gz per platform, a .zip
        # for Windows, and a separate CHECKSUMS file:
        # https://github.com/yannh/kubeconform/blob/v0.8.0/.goreleaser.yml
        ("linux", "amd64"): Pin("", "", "", "kubeconform", ""),
        ("linux", "arm64"): Pin("", "", "", "kubeconform", ""),
        ("darwin", "amd64"): Pin("", "", "", "kubeconform", ""),
        ("darwin", "arm64"): Pin("", "", "", "kubeconform", ""),
        ("win32", "amd64"): Pin("", "", "", "kubeconform.exe", ""),
    }
}


def pin_for(name):
    try:
        return PINS[name][host()]
    except KeyError:
        raise Unsupported(f"no pinned {name} for {host()[0]}/{host()[1]}") from None


def tools_dir():
    return settings.root / "tools"


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def installed(name):
    """The verified binary, or None. Never returns a path it has not just checked."""
    pin = pin_for(name)
    path = tools_dir() / pin.member
    if not path.is_file() or digest(path) != pin.binary_sha256:
        return None
    return path
```

The empty pin strings are filled in at the phase 2 release gate. `test_every_pin_is_filled_in` fails until they are, which is the point: it is the gate, not a reminder.

- [ ] **Step 4: Run the tests**

Run: `uv run pytest tests/test_tools.py -v`
Expected: PASS except `test_every_pin_is_filled_in`, which FAILS by design until the pins are real. Mark it now with `@pytest.mark.xfail(reason="pins are filled at the phase 2 release gate", strict=True)` and delete the marker in phase 2.

- [ ] **Step 5: Run the full suite and lint**

Run: `uv run pytest tests/ -q && uv run ruff check && uv run ruff format --check`

- [ ] **Step 6: Commit**

```bash
git add src/drillion/tools.py tests/test_tools.py
git commit -m "feat(tools): pin external graders by checksum and verify before every use"
```

---

### Task 8: Acquiring a pinned tool safely

**Files:**
- Modify: `src/drillion/tools.py`
- Modify: `src/drillion/doctor.py`
- Test: `tests/test_tools.py`, `tests/test_doctor.py`

**Interfaces:**
- Consumes: `tools.Pin`, `tools.pin_for`, `tools.digest`, `tools.installed` from Task 7.
- Produces: `tools.acquire(name) -> Path` raises `tools.Rejected` on any checksum or archive-shape failure. `tools.report() -> list[tuple[str, str]]` returns `(tool name, one line of status)` for doctor.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_tools.py`. `responses` is already a dependency, so the download is faked without a network:

```python
import io
import tarfile

import responses


def _archive(member, payload):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        info = tarfile.TarInfo(member)
        info.size = len(payload)
        info.mode = 0o755
        tar.addfile(info, io.BytesIO(payload))
    return buf.getvalue()


@responses.activate
def test_acquire_verifies_the_archive_then_the_binary(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "root", tmp_path)
    payload = b"pretend kubeconform"
    blob = _archive("kubeconform", payload)
    responses.add(responses.GET, "https://example.invalid/k.tar.gz", body=blob)
    monkeypatch.setitem(
        tools.PINS["kubeconform"],
        tools.host(),
        tools.Pin("0.8.0", "https://example.invalid/k.tar.gz",
                  hashlib.sha256(blob).hexdigest(), "kubeconform",
                  hashlib.sha256(payload).hexdigest()),
    )
    path = tools.acquire("kubeconform")
    assert path.read_bytes() == payload and tools.installed("kubeconform") == path


@responses.activate
def test_a_tampered_archive_is_rejected_and_the_old_tool_survives(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "root", tmp_path)
    good = tmp_path / "tools" / "kubeconform"
    good.parent.mkdir(parents=True)
    good.write_bytes(b"the one that already worked")
    responses.add(responses.GET, "https://example.invalid/k.tar.gz", body=b"wrong bytes")
    monkeypatch.setitem(
        tools.PINS["kubeconform"],
        tools.host(),
        tools.Pin("0.8.0", "https://example.invalid/k.tar.gz", "00" * 32, "kubeconform", "11" * 32),
    )
    with pytest.raises(tools.Rejected):
        tools.acquire("kubeconform")
    assert good.read_bytes() == b"the one that already worked"


@responses.activate
def test_an_archive_member_that_escapes_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "root", tmp_path)
    blob = _archive("../../escape", b"nope")
    responses.add(responses.GET, "https://example.invalid/k.tar.gz", body=blob)
    monkeypatch.setitem(
        tools.PINS["kubeconform"],
        tools.host(),
        tools.Pin("0.8.0", "https://example.invalid/k.tar.gz",
                  hashlib.sha256(blob).hexdigest(), "kubeconform", "11" * 32),
    )
    with pytest.raises(tools.Rejected):
        tools.acquire("kubeconform")
    assert not (tmp_path / "escape").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_tools.py -v -k "acquire or escape or tampered"`
Expected: FAIL with `AttributeError: module 'drillion.tools' has no attribute 'acquire'`.

- [ ] **Step 3: Write the implementation**

Add to `src/drillion/tools.py`:

```python
import os
import tarfile
import tempfile
import zipfile

import requests

TIMEOUT = (10, 60)  # connect, read
MAX_ARCHIVE = 64 << 20


class Rejected(Exception):
    """An acquisition that did not match its pin. Nothing was installed."""


def _download(url, into):
    """The archive, or Rejected. Bounded: a grader is a few megabytes, never a stream."""
    with requests.get(url, stream=True, timeout=TIMEOUT) as r:
        r.raise_for_status()
        size = 0
        with into.open("wb") as out:
            for block in r.iter_content(1 << 20):
                size += len(block)
                if size > MAX_ARCHIVE:
                    raise Rejected(f"{url} is larger than {MAX_ARCHIVE} bytes")
                out.write(block)
    return into


def _extract(archive, member, into):
    """Exactly one named regular file. Not a directory, not a link, not a path."""
    if archive.name.endswith(".zip"):
        with zipfile.ZipFile(archive) as zf:
            info = zf.getinfo(member)  # KeyError if absent
            if info.is_dir():
                raise Rejected(f"{member} is a directory")
            data = zf.read(member)
    else:
        with tarfile.open(archive) as tf:
            info = tf.getmember(member)  # KeyError if absent
            if not info.isfile():
                raise Rejected(f"{member} is not a regular file")
            data = tf.extractfile(info).read()
    into.write_bytes(data)
    into.chmod(0o755)
    return into


def acquire(name):
    """Fetch, verify and install a pinned tool. On any failure nothing is replaced."""
    pin = pin_for(name)
    if not pin.url:
        raise Rejected(f"{name} has no pin for {host()[0]}/{host()[1]} yet")
    target = tools_dir()
    target.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=target) as scratch:
        scratch = Path(scratch)
        suffix = ".zip" if pin.url.endswith(".zip") else ".tar.gz"
        archive = _download(pin.url, scratch / f"{name}{suffix}")
        if digest(archive) != pin.archive_sha256:
            raise Rejected(f"{pin.url} does not match its pinned archive checksum")
        try:
            binary = _extract(archive, pin.member, scratch / pin.member)
        except KeyError:
            raise Rejected(f"{pin.url} has no member {pin.member!r}") from None
        if digest(binary) != pin.binary_sha256:
            raise Rejected(f"{pin.member} does not match its pinned checksum")
        os.replace(binary, target / pin.member)
    return target / pin.member
```

`_extract` reads the named member by name rather than unpacking the archive, so a `../../escape` member is simply never found and nothing is written outside the scratch directory.

Add `report()` and call it from `doctor`:

```python
def report():
    """(tool, status) for every pinned tool, for `drillion doctor`."""
    out = []
    for name in PINS:
        try:
            pin = pin_for(name)
        except Unsupported as exc:
            out.append((name, str(exc)))
            continue
        if not pin.url:
            out.append((name, f"no pin for this platform yet ({pin.version or 'unset'})"))
        elif installed(name):
            out.append((name, f"{pin.version}, verified"))
        else:
            out.append((name, f"missing or altered: run `drillion doctor --fetch`"))
    return out
```

Wire `report()` into `doctor`'s output and add a `--fetch` flag to the CLI that calls `acquire` for every tool that `installed()` returns None for.

- [ ] **Step 4: Run the tests**

Run: `uv run pytest tests/test_tools.py tests/test_doctor.py -q`
Expected: PASS.

- [ ] **Step 5: Run the full suite and lint**

Run: `uv run pytest tests/ -q && uv run ruff check && uv run ruff format --check`

- [ ] **Step 6: Commit**

```bash
git add src/drillion/tools.py src/drillion/doctor.py src/drillion/cli.py tests/test_tools.py tests/test_doctor.py
git commit -m "feat(tools): fetch a pinned grader, verifying the archive and the binary"
```

---

### Task 9: Packaged Kubernetes schemas

**Files:**
- Create: `src/drillion/_schemas/manifest.json`, `src/drillion/_schemas/<version>-standalone-strict/*.json`
- Modify: `pyproject.toml:65` (wheel force-include and sdist artifacts)
- Modify: `src/drillion/tools.py`
- Test: `tests/test_tools.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `tools.SCHEMAS: Path` pointing at the packaged directory, `tools.KUBERNETES_VERSION: str`, `tools.schema_digest() -> str` over the packaged set, and `tools.schema_location() -> str`, the `-schema-location` template kubeconform expects.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_tools.py`:

```python
def test_packaged_schemas_are_present_and_pinned():
    assert tools.SCHEMAS.is_dir(), "schemas must ship with the package, not be downloaded"
    assert tools.KUBERNETES_VERSION.count(".") == 2, "pin a concrete X.Y.Z"
    assert (tools.SCHEMAS / "deployment-apps-v1.json").is_file()
    assert len(tools.schema_digest()) == 64


def test_schema_location_is_a_local_template_with_no_remote_fallback():
    location = tools.schema_location()
    assert location.startswith(str(tools.SCHEMAS))
    assert "{{.ResourceKind}}" in location and "http" not in location
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_tools.py -v -k schema`
Expected: FAIL with `AttributeError: module 'drillion.tools' has no attribute 'SCHEMAS'`.

- [ ] **Step 3: Write the implementation**

Download one `standalone-strict` schema set from `yannh/kubernetes-json-schema` for a concrete version and commit it under `src/drillion/_schemas/<version>-standalone-strict/`. For this phase only the kinds the fixture needs must be present; phase 3 widens the set. Write `src/drillion/_schemas/manifest.json`:

```json
{"kubernetes_version": "1.31.0", "source": "https://github.com/yannh/kubernetes-json-schema", "digest": "<sha256 over the sorted file list and contents>"}
```

Add to `src/drillion/tools.py`:

```python
import json

from .settings import PKG

_MANIFEST = json.loads((PKG / "_schemas" / "manifest.json").read_text(encoding="utf-8"))
KUBERNETES_VERSION = _MANIFEST["kubernetes_version"]
SCHEMAS = PKG / "_schemas" / f"{KUBERNETES_VERSION}-standalone-strict"


def schema_digest():
    """One digest over the whole packaged set: part of a manifest verdict's identity."""
    h = hashlib.sha256()
    for path in sorted(SCHEMAS.rglob("*.json")):
        h.update(path.name.encode())
        h.update(path.read_bytes())
    return h.hexdigest()


def schema_location():
    """kubeconform's local template. No remote location is ever passed, so a schema that
    is not packaged is an error rather than a silent download."""
    return str(SCHEMAS / "{{.ResourceKind}}{{.KindSuffix}}.json")
```

In `pyproject.toml`, add the schemas to both build targets:

```toml
[tool.hatch.build.targets.wheel.force-include]
"tasks" = "drillion/_tasks"
"web/dist" = "drillion/_web"
```

`src/drillion/_schemas` is already inside `packages = ["src/drillion"]`, so the wheel picks it up; confirm with `uv build` and add an sdist `artifacts` entry only if the check below shows it missing.

- [ ] **Step 4: Run the tests and check the built artifacts**

Run: `uv run pytest tests/test_tools.py -q`
Then: `uv build && python -c "import zipfile,glob;z=zipfile.ZipFile(glob.glob('dist/*.whl')[0]);print([n for n in z.namelist() if '_schemas' in n][:5])"`
Expected: PASS, and the schema files are listed in the wheel.

- [ ] **Step 5: Run the full suite and lint**

Run: `uv run pytest tests/ -q && uv run ruff check && uv run ruff format --check`

- [ ] **Step 6: Commit**

```bash
git add src/drillion/_schemas src/drillion/tools.py pyproject.toml tests/test_tools.py
git commit -m "feat(tools): package kubernetes schemas so grading never needs the network"
```

---

### Task 10: Sandbox reaches the tools and the schemas

**Files:**
- Modify: `src/drillion/sandbox.py:229` (`_roots`), `src/drillion/sandbox.py:340` (`_sbpl`)
- Test: `tests/test_sandbox.py`

**Interfaces:**
- Consumes: `tools.tools_dir()`, `tools.SCHEMAS` from Tasks 7 and 9.
- Produces: no new names.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_sandbox.py`:

```python
def test_the_tools_directory_is_executable_and_schemas_are_readable(tmp_path, monkeypatch):
    from drillion import sandbox, tools
    from drillion.settings import settings

    monkeypatch.setattr(settings, "root", tmp_path)
    (tmp_path / "tools").mkdir()
    roots = dict(sandbox._roots(str(tmp_path / "scratch"), []))
    tools_key = os.fsencode(str((tmp_path / "tools").resolve()))
    assert "execute" in roots.get(tools_key, set())
    schema_key = os.fsencode(str(tools.SCHEMAS.resolve()))
    assert "read_file" in roots.get(schema_key, set())


def test_the_network_stays_denied():
    """Grading is offline. Adding an exec root must not have opened anything else."""
    from drillion import sandbox

    assert "connect_tcp" not in {r for _, rights in sandbox._roots("/tmp", []) for r in rights}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_sandbox.py -v -k tools_directory`
Expected: FAIL with `KeyError` or an empty rights set.

- [ ] **Step 3: Write the implementation**

In `src/drillion/sandbox.py`, import `tools` lazily inside `_roots` to avoid an import cycle, and add two roots:

```python
        # the pinned graders, executable for the same reason /usr/bin is: a manifest is
        # graded by running kubeconform, and whatever it starts inherits this sandbox
        (tools.tools_dir(), _EXEC),
        (tools.SCHEMAS, _READ),
```

Both go through the existing `merged` loop, which already drops paths that do not exist, so a machine with no tools installed is unchanged.

In `_sbpl`, add the same two paths to the readable set, and `tools_dir()` to the `process-exec*` set.

- [ ] **Step 4: Run the tests**

Run: `uv run pytest tests/test_sandbox.py -q`
Expected: PASS.

- [ ] **Step 5: Run the full suite and lint**

Run: `uv run pytest tests/ -q && uv run ruff check && uv run ruff format --check`

- [ ] **Step 6: Commit**

```bash
git add src/drillion/sandbox.py tests/test_sandbox.py
git commit -m "feat(sandbox): let a graded run execute the pinned tools and read the schemas"
```

---

### Task 11: Generating a brief in a sandboxed child

The load-bearing correction from the audit. `brief()` is task-authored Python and must never be imported by the server. It runs in the same sandboxed child every graded run already uses, and its result crosses back as validated JSON.

**Files:**
- Create: `src/drillion/manifest.py`
- Test: `tests/test_manifest.py`, `tests/fixtures_manifest.py`

**Interfaces:**
- Consumes: `sandbox.run`, `settings.root`, `kinds.of`.
- Produces: `manifest.generate_brief(meta, seed) -> dict` runs in a child and returns a validated mapping. `manifest.Rejected` is raised when the child fails or returns something unusable. `manifest.MAX_BRIEF_BYTES = 8192`. `manifest.render(template, brief) -> str` for plain text.

- [ ] **Step 1: Write the failing test**

Create `tests/fixtures_manifest.py`:

```python
"""The fixture manifest task every phase-1 test grades against. It never enters tasks/."""

README = """\
---
title: A fixture deployment
kind: manifest
difficulty: easy
minutes: 10
track: kubernetes
tags: [deployment]
---
# A fixture deployment

## Why
Because a Deployment is the first shape anyone has to type from nothing.

## You get
Nothing but the requirements below.

## You return
a Deployment named `{name}` with {replicas} replicas.

## Rules
One document, one Deployment.

## Hints
### Hint 1
one
### Hint 2
two
### Hint 3
three
"""

GRADE = '''\
SERVICES = ["checkout", "billing"]


def brief(r):
    return {"name": r.choice(SERVICES), "replicas": r.randint(2, 5)}


def check(doc, b):
    assert doc["kind"] == "Deployment", "kind"
    assert doc["metadata"]["name"] == b["name"], "name"
    assert doc["spec"]["replicas"] == b["replicas"], "replicas"
'''

SOLUTION = """\
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {name}
spec:
  replicas: {replicas}
"""


def fixture_task():
    """{filename: text} for `tests.fixtures.tasks_root`."""
    return {"README.md": README, "task.yaml": "", "grade.py": GRADE, "solution.yaml": SOLUTION}
```

Create `tests/test_manifest.py`:

```python
"""Briefs are generated by task code, so they are generated where task code is confined."""

import shutil

import pytest

from drillion import catalogue, manifest
from drillion.settings import settings
from tests.fixtures import tasks_root
from tests.fixtures_manifest import fixture_task


@pytest.fixture
def fixture_root():
    tmp = tasks_root(**{"271_fixture": fixture_task()})
    keep = settings.root
    settings.root = tmp
    yield tmp
    settings.root = keep
    shutil.rmtree(tmp, ignore_errors=True)


def test_a_brief_is_generated_and_is_deterministic(fixture_root):
    meta = catalogue.tasks()["271_fixture"]
    first = manifest.generate_brief(meta, 4242)
    assert first == manifest.generate_brief(meta, 4242)
    assert first["name"] in ("checkout", "billing") and 2 <= first["replicas"] <= 5


def test_different_seeds_can_give_different_briefs(fixture_root):
    meta = catalogue.tasks()["271_fixture"]
    seen = {tuple(sorted(manifest.generate_brief(meta, s).items())) for s in range(1000, 1040)}
    assert len(seen) > 1, "the brief must actually vary with the seed"


def test_the_server_never_imports_the_grader(fixture_root):
    import sys

    meta = catalogue.tasks()["271_fixture"]
    manifest.generate_brief(meta, 7)
    assert not any("271_fixture" in name or name == "grade" for name in sys.modules)


def test_a_grader_that_returns_junk_is_rejected(fixture_root):
    (settings.tasks_dir / "271_fixture" / "grade.py").write_text(
        "def brief(r):\n    return object()\n\n\ndef check(doc, b):\n    pass\n",
        encoding="utf-8",
    )
    meta = catalogue.tasks()["271_fixture"]
    with pytest.raises(manifest.Rejected):
        manifest.generate_brief(meta, 7)


def test_a_grader_that_explodes_is_rejected_not_crashed(fixture_root):
    (settings.tasks_dir / "271_fixture" / "grade.py").write_text(
        "def brief(r):\n    raise ValueError('boom')\n\n\ndef check(doc, b):\n    pass\n",
        encoding="utf-8",
    )
    meta = catalogue.tasks()["271_fixture"]
    with pytest.raises(manifest.Rejected):
        manifest.generate_brief(meta, 7)


def test_render_fills_placeholders_and_survives_doubled_braces():
    assert manifest.render("a {name} b", {"name": "x"}) == "a x b"
    assert manifest.render("a {{literal}} b", {}) == "a {literal} b"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_manifest.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'drillion.manifest'`.

- [ ] **Step 3: Write the implementation**

Create `src/drillion/manifest.py`:

```python
"""Grading a manifest: the brief a sitting is graded against, and how it is produced.

`grade.py` is task-authored Python. It is loaded and run only inside the sandboxed child
that `sandbox.run` starts, and it talks back in JSON. The server never imports it."""

import json
import subprocess
import tempfile
from pathlib import Path

from . import sandbox
from .settings import settings

MAX_BRIEF_BYTES = 8192
SCALARS = (str, int, float, bool)

# runs inside the sandbox, with the grader path and seed passed as argv
_BRIEF_SOURCE = '''
import importlib.util, json, random, sys

path, seed, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
spec = importlib.util.spec_from_file_location(sys.argv[4], path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
with open(out, "w", encoding="utf-8") as stream:
    json.dump(module.brief(random.Random(seed)), stream)
'''


class Rejected(Exception):
    """A grader that did not produce a usable brief. Nothing was graded."""


def _validated(raw):
    """A brief is a flat mapping of string keys to finite scalars. Anything else is a
    task-authoring bug, and one that would otherwise reach a template or an assert."""
    if not isinstance(raw, dict):
        raise Rejected("brief() must return a mapping")
    for key, value in raw.items():
        if not isinstance(key, str) or not key.isidentifier():
            raise Rejected(f"brief key {key!r} is not a plain name")
        if isinstance(value, bool) or not isinstance(value, SCALARS):
            if not isinstance(value, SCALARS):
                raise Rejected(f"brief value for {key!r} is not a scalar")
        if isinstance(value, float) and value != value:
            raise Rejected(f"brief value for {key!r} is not a finite number")
    return raw


def module_name(slug):
    """A unique module name per task, so two graders cannot share state in selfcheck."""
    return f"drillion_grade_{slug}"


def generate_brief(meta, seed):
    """The requirements for one sitting, produced by the task's own code, in the sandbox."""
    grader = meta["dir"] / "grade.py"
    with tempfile.TemporaryDirectory(dir=settings.root) as scratch:
        scratch = Path(scratch)
        script = scratch / "_brief.py"
        script.write_text(_BRIEF_SOURCE, encoding="utf-8")
        out = scratch / "brief.json"
        try:
            result = sandbox.run_script(
                [str(script), str(grader), str(seed), str(out), module_name(meta["dir"].name)],
                scratch,
                30,
            )
        except subprocess.TimeoutExpired:
            raise Rejected("brief() did not finish") from None
        if result.returncode != 0:
            raise Rejected(f"brief() failed: {result.stderr.strip()[-500:]}")
        if not out.exists() or out.stat().st_size > MAX_BRIEF_BYTES:
            raise Rejected("brief() wrote nothing, or wrote too much")
        try:
            return _validated(json.loads(out.read_text(encoding="utf-8")))
        except ValueError as exc:
            raise Rejected(f"brief() is not valid JSON: {exc}") from None


def render(template, brief):
    """Plain-text substitution for a README. Doubled braces stay literal, as in str.format."""
    try:
        return template.format(**brief)
    except (KeyError, IndexError, ValueError) as exc:
        raise Rejected(f"the spec template does not match the brief: {exc}") from None
```

`sandbox.run` builds a pytest command. Add a sibling in `src/drillion/sandbox.py` that runs a plain script under the same confinement:

```python
def run_script(args, scratch, cpu, **env):
    """A bare interpreter under the same tier as a graded run: `confine` without pytest."""
    plan = confine([], scratch, cpu, **env)
    plan["args"] = [sys.executable, *args]
    if status()[0] == "restricted-token":
        from . import winsandbox

        return winsandbox.run(plan["args"], scratch, timeout=cpu, **env)
    return subprocess.run(
        **plan, capture_output=True, text=True, encoding="utf-8", check=False, timeout=cpu
    )
```

`confine([])` builds an empty pytest command whose `args` is then replaced, so the environment, cwd, and `preexec_fn` are identical to a graded run.

- [ ] **Step 4: Run the tests**

Run: `uv run pytest tests/test_manifest.py -v`
Expected: PASS.

- [ ] **Step 5: Run the full suite and lint**

Run: `uv run pytest tests/ -q && uv run ruff check && uv run ruff format --check`

- [ ] **Step 6: Commit**

```bash
git add src/drillion/manifest.py src/drillion/sandbox.py tests/test_manifest.py tests/fixtures_manifest.py
git commit -m "feat(manifest): generate a sitting's brief inside the sandbox, never in the server"
```

---

### Task 12: The brief persists on the attempt

An open sitting must keep the requirements it was given. Regenerating from the seed on every render means an upgraded grader silently changes the question mid-attempt.

**Files:**
- Modify: `src/drillion/attempts.py:68` (`open_attempt`), `src/drillion/state.py:78` (`_fields`)
- Modify: `src/drillion/api.py:241` (`_payload`), `src/drillion/api.py:413` (`get_task`), `src/drillion/api.py:420` (`open_task`)
- Test: `tests/test_attempts.py`, `tests/test_manifest.py`

**Interfaces:**
- Consumes: `manifest.generate_brief`, `manifest.render` from Task 11.
- Produces: an open manifest attempt carries `o["brief"]: dict`, `o["spec_md"]: str` and `o["brief_revision"]: str`. `attempts.open_attempt(st, slug, meta)` takes `meta`. `api._payload` serves `o["spec_md"]` when one is stored.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_manifest.py`:

```python
def test_opening_persists_the_brief_and_the_rendered_spec(fixture_root):
    from drillion import attempts, state

    meta = catalogue.tasks()["271_fixture"]
    with state.writing() as st:
        o = attempts.open_attempt(st, "271_fixture", meta)
        assert o["brief"]["name"] in ("checkout", "billing")
        assert f"named `{o['brief']['name']}`" in o["spec_md"]
        assert "{name}" not in o["spec_md"]


def test_an_edited_readme_does_not_change_an_open_sitting(fixture_root):
    from drillion import attempts, state

    meta = catalogue.tasks()["271_fixture"]
    with state.writing() as st:
        first = attempts.open_attempt(st, "271_fixture", meta)["spec_md"]
    readme = settings.tasks_dir / "271_fixture" / "README.md"
    readme.write_text(readme.read_text(encoding="utf-8").replace("Because", "CHANGED"), encoding="utf-8")
    with state.writing() as st:
        again = attempts.open_attempt(st, "271_fixture", catalogue.tasks()["271_fixture"])
    assert again["spec_md"] == first


def test_a_python_attempt_gains_no_manifest_fields(fixture_root):
    from drillion import attempts, state

    meta = {"kind": "python", "dir": settings.tasks_dir / "271_fixture", "hints": []}
    with state.writing() as st:
        o = attempts.open_attempt(st, "009_like", meta)
    assert "brief" not in o and "spec_md" not in o
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_manifest.py -v -k persists`
Expected: FAIL. `open_attempt` takes two arguments and stores no brief.

- [ ] **Step 3: Write the implementation**

In `src/drillion/attempts.py`:

```python
def open_attempt(st, slug, meta):
    """The attempt is the timer, and for a manifest it is also the question.

    A manifest's requirements are generated once, here, and never again: regenerating them
    from the seed would let an upgraded grader change the question inside a live sitting."""
    o = st["open"].get(slug)
    if o:
        touch(o)
        return o
    now = datetime.now()
    seed = random.randint(1000, 9999)
    st["open"][slug] = {"seed": seed, ..., **kinds.of(meta).opening(meta, seed)}
    return st["open"][slug]
```

`attempts` never names a kind. The manifest kind's `opening` is what produces the brief:

```python
class _Manifest:
    def opening(self, meta, seed):
        from . import manifest

        brief = manifest.generate_brief(meta, seed)
        return {
            "brief": brief,
            "spec_md": manifest.render(meta["spec_md"], brief),
            "brief_revision": manifest.grader_revision(meta),
        }

    def spec(self, meta, o):
        """A rendered brief belongs to the sitting that was given it. With no attempt open
        the README is served as written, placeholders and all, which is why `doctor` rejects
        a manifest whose Why or You get sections contain one."""
        return o["spec_md"] if o and "spec_md" in o else meta["spec_md"]
```

Add `manifest.grader_revision(meta)`, a sha256 prefix over `grade.py` and `solution.yaml`, so a later run can say which generator produced the stored brief.

In `state._fields`, allow the new keys: `brief` must be a dict, `spec_md` and `brief_revision` must be text. Follow the existing style, raising `Unreadable` with a sentence.

In `api._payload`, prefer the stored spec:

```python
        "spec_md": kind.spec(meta, o),
```

An unopened manifest task therefore shows the README with its placeholders still in it, which is why the spec requires `## Why` and `## You get` to contain none. Add that rule to `doctor._value_rules`: for `kind: manifest`, a `{` in the `Why` or `You get` sections is a reported reason.

Update both callers of `open_attempt` in `api.py` to pass `meta`.

- [ ] **Step 4: Run the tests**

Run: `uv run pytest tests/test_manifest.py tests/test_attempts.py tests/test_api.py -q`
Expected: PASS.

- [ ] **Step 5: Run the full suite and lint**

Run: `uv run pytest tests/ -q && uv run ruff check && uv run ruff format --check`

- [ ] **Step 6: Commit**

```bash
git add src/drillion/attempts.py src/drillion/state.py src/drillion/api.py src/drillion/manifest.py src/drillion/doctor.py tests/
git commit -m "feat(attempts): persist a manifest sitting's brief and its rendered spec"
```

---

### Task 13: Grading a manifest

**Files:**
- Modify: `src/drillion/manifest.py`, `src/drillion/runner.py:71` (`run_tests`)
- Test: `tests/test_manifest.py`

**Interfaces:**
- Consumes: `tools.installed`, `tools.schema_location`, `tools.KUBERNETES_VERSION`, `manifest.module_name`, the persisted `o["brief"]`.
- Produces: `manifest.harness(meta, brief) -> str`, the generated test source. `manifest.ToolMissing` is raised when the grader is not installed. `runner.run_tests` splits into `runner.run_python(meta, seed)` and `runner.run_manifest(meta, brief)`, both returning `(passed, output, case)`, with `case` None for a manifest. `manifest.fingerprint(meta) -> str`.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_manifest.py`:

```python
def test_a_correct_manifest_passes(fixture_root, installed_kubeconform):
    from drillion import runner

    meta = catalogue.tasks()["271_fixture"]
    brief = {"name": "checkout", "replicas": 3}
    (settings.tasks_dir / "271_fixture" / "task.yaml").write_text(
        manifest.render_solution(meta, brief), encoding="utf-8"
    )
    passed, out, case = runner.run_tests(meta, 7, brief=brief)
    assert passed, out
    assert case is None, "a manifest run has no generated-arguments case"


def test_a_manifest_that_misses_the_brief_says_which_requirement(fixture_root, installed_kubeconform):
    from drillion import runner

    meta = catalogue.tasks()["271_fixture"]
    (settings.tasks_dir / "271_fixture" / "task.yaml").write_text(
        "apiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: checkout\nspec:\n  replicas: 9\n",
        encoding="utf-8",
    )
    passed, out, _ = runner.run_tests(meta, 7, brief={"name": "checkout", "replicas": 3})
    assert not passed and "replicas" in out


def test_an_empty_submission_is_rejected_before_the_schema(fixture_root, installed_kubeconform):
    from drillion import runner

    meta = catalogue.tasks()["271_fixture"]
    passed, out, _ = runner.run_tests(meta, 7, brief={"name": "checkout", "replicas": 3})
    assert not passed and "empty" in out.lower()


def test_a_multi_document_submission_is_rejected(fixture_root, installed_kubeconform):
    from drillion import runner

    meta = catalogue.tasks()["271_fixture"]
    (settings.tasks_dir / "271_fixture" / "task.yaml").write_text(
        "kind: Deployment\n---\nkind: Service\n", encoding="utf-8"
    )
    passed, out, _ = runner.run_tests(meta, 7, brief={"name": "checkout", "replicas": 3})
    assert not passed and "one document" in out.lower()


def test_a_missing_tool_is_not_a_wrong_answer(fixture_root, monkeypatch):
    from drillion import tools

    monkeypatch.setattr(tools, "installed", lambda name: None)
    meta = catalogue.tasks()["271_fixture"]
    with pytest.raises(manifest.ToolMissing):
        manifest.harness(meta, {"name": "checkout", "replicas": 3})


def test_the_fingerprint_changes_when_any_grading_input_changes(fixture_root, monkeypatch):
    from drillion import tools

    meta = catalogue.tasks()["271_fixture"]
    before = manifest.fingerprint(meta)
    monkeypatch.setattr(tools, "KUBERNETES_VERSION", "9.9.9")
    assert manifest.fingerprint(meta) != before
```

Write an `installed_kubeconform` fixture in the same module that skips when `tools.installed("kubeconform")` is None, so the suite stays runnable before the pins are filled:

```python
@pytest.fixture
def installed_kubeconform():
    if tools.installed(tools.KUBECONFORM) is None:
        pytest.skip("kubeconform is not installed: run `drillion doctor --fetch`")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_manifest.py -v -k "missing_tool or fingerprint"`
Expected: FAIL with `AttributeError: module 'drillion.manifest' has no attribute 'harness'`.

- [ ] **Step 3: Write the implementation**

Add to `src/drillion/manifest.py`:

```python
from . import tools


class ToolMissing(Exception):
    """The grader is not installed. This is infrastructure, never a learner's mistake."""


_HARNESS = '''
import importlib.util, json, subprocess, sys
from pathlib import Path

import yaml

BRIEF = json.loads({brief!r})


def _one_mapping(text):
    if not text.strip():
        raise AssertionError("task.yaml is empty: write the manifest before submitting")
    docs = list(yaml.safe_load_all(text))
    if len(docs) != 1:
        raise AssertionError(f"expected one document, found {{len(docs)}}")
    if not isinstance(docs[0], dict):
        raise AssertionError("the document must be a mapping, not a list or a scalar")
    return docs[0]


def _readable(out):
    try:
        report = json.loads(out.stdout)
    except ValueError:
        return (out.stderr or out.stdout).strip()[-1000:]
    lines = []
    for entry in report.get("resources", []):
        if entry.get("status") not in ("statusValid", "statusSkipped"):
            lines.append(f"{{entry.get('path', 'task.yaml')}}: {{entry.get('msg', 'invalid')}}")
    return "\\n".join(lines) or "the manifest is not valid against the schema"


def test_manifest():
    text = Path({learner!r}).read_text(encoding="utf-8")
    doc = _one_mapping(text)
    out = subprocess.run(
        [{tool!r}, "-strict", "-kubernetes-version", {kube!r},
         "-schema-location", {schemas!r}, "-output", "json", {learner!r}],
        capture_output=True, text=True, timeout=30,
    )
    assert out.returncode == 0, _readable(out)
    spec = importlib.util.spec_from_file_location({module!r}, {grader!r})
    grade = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(grade)
    grade.check(doc, BRIEF)
'''


def harness(meta, brief):
    """The generated test for one manifest sitting. Never regenerates the brief."""
    tool = tools.installed(tools.KUBECONFORM)
    if tool is None:
        raise ToolMissing("kubeconform is not installed: run `drillion doctor --fetch`")
    kind = kinds.of(meta)
    return _HARNESS.format(
        brief=json.dumps(brief),
        learner=str(kind.path(meta)),
        tool=str(tool),
        kube=tools.KUBERNETES_VERSION,
        schemas=tools.schema_location(),
        module=module_name(meta["dir"].name),
        grader=str(meta["dir"] / "grade.py"),
    )


def fingerprint(meta):
    """What decided this verdict: the grader, the validator and the schemas alike.

    The etag says what the learner wrote. This says what judged it, which is why the
    validator version and the schema digest are in here and not only `grade.py`."""
    pin = tools.pin_for(tools.KUBECONFORM)
    h = hashlib.sha256()
    for part in (
        grader_revision(meta),
        pin.version,
        pin.binary_sha256,
        tools.KUBERNETES_VERSION,
        tools.schema_digest(),
    ):
        h.update(part.encode())
        h.update(b"\0")
    return "m1:" + h.hexdigest()[:12]
```

Note the doubled braces inside `_HARNESS`: the template goes through `str.format`, so every literal brace in the generated code is written `{{`/`}}`.

In `src/drillion/runner.py`, dispatch:

`runner` gains a second entry point and loses nothing. There is no dispatch here: the caller
already holds a kind, and `kind.grade` picks the path.

```python
def run_python(meta, seed):
    """The existing run_tests body, renamed. Unchanged otherwise."""
    ...


def run_manifest(meta, brief):
    """Write the generated harness into the scratch dir and grade it like any other test."""
    from . import manifest

    with tempfile.TemporaryDirectory(dir=settings.root) as box:
        test = Path(box, "test_manifest.py")
        test.write_text(manifest.harness(meta, brief), encoding="utf-8")
        try:
            r = _run_pytest([str(test), "-l", "--verbosity=2", "--timeout=45"], timeout=60)
        except subprocess.TimeoutExpired:
            return False, "timed out after 60s", None
    return r.returncode == 0, r.stdout, None
```

The manifest kind wires it up, and `api.run_task` calls `kind.grade(meta, o)` for both kinds:

```python
class _Manifest:
    def grade(self, meta, o):
        from . import runner

        return runner.run_manifest(meta, o["brief"])
```

Update `api.run_task` to pass `meta` and `o.get("brief")`, to catch `manifest.ToolMissing` and return a 503 naming the fix rather than a failing test, and to record `manifest.fingerprint(meta)` as the pass's `revision` for a manifest.

- [ ] **Step 4: Run the tests**

Run: `uv run pytest tests/test_manifest.py -v`
Expected: PASS, with the kubeconform-dependent tests skipped until the pins land.

- [ ] **Step 5: Run the full suite and lint**

Run: `uv run pytest tests/ -q && uv run ruff check && uv run ruff format --check`

- [ ] **Step 6: Commit**

```bash
git add src/drillion/manifest.py src/drillion/runner.py src/drillion/api.py tests/test_manifest.py
git commit -m "feat(manifest): grade a submission with kubeconform and the stored brief"
```

---

### Task 14: Rendering the solution safely

`str.format` on a YAML template can change a value's type or break its quoting: a name of `y` becomes a boolean, a value with a colon splits a mapping. The solution is rendered for the gated reveal and for the fixture check, so it has to be right in both.

**Files:**
- Modify: `src/drillion/manifest.py`
- Test: `tests/test_manifest.py`

**Interfaces:**
- Consumes: `manifest.render` from Task 11.
- Produces: `manifest.render_solution(meta, brief) -> str`, which serialises each placeholder as a YAML scalar of its intended type and parses the result before returning it.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_manifest.py`:

```python
import yaml


def test_a_solution_placeholder_keeps_its_type(fixture_root):
    meta = catalogue.tasks()["271_fixture"]
    doc = yaml.safe_load(manifest.render_solution(meta, {"name": "checkout", "replicas": 3}))
    assert doc["spec"]["replicas"] == 3 and doc["metadata"]["name"] == "checkout"


def test_a_yaml_looking_string_stays_a_string(fixture_root):
    """`y`, `no` and `1.0` are all YAML traps. A name is a name."""
    for value in ("y", "no", "1.0", "on"):
        doc = yaml.safe_load(manifest.render_solution(meta_for(), {"name": value, "replicas": 2}))
        assert doc["metadata"]["name"] == value, value


def test_a_value_with_a_colon_does_not_break_the_document(fixture_root):
    doc = yaml.safe_load(manifest.render_solution(meta_for(), {"name": "a: b", "replicas": 2}))
    assert doc["metadata"]["name"] == "a: b"


def test_a_placeholder_that_is_not_a_whole_scalar_is_rejected(fixture_root):
    solution = settings.tasks_dir / "271_fixture" / "solution.yaml"
    solution.write_text("metadata:\n  name: prefix-{name}\n", encoding="utf-8")
    with pytest.raises(manifest.Rejected):
        manifest.render_solution(catalogue.tasks()["271_fixture"], {"name": "checkout"})
```

Add a `meta_for()` helper in the module returning `catalogue.tasks()["271_fixture"]`.

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_manifest.py -v -k solution`
Expected: FAIL with `AttributeError: module 'drillion.manifest' has no attribute 'render_solution'`.

- [ ] **Step 3: Write the implementation**

Add to `src/drillion/manifest.py`:

```python
import re

# a placeholder must be the entire value of its line: `name: {name}`, never `name: a-{name}`.
# Anything else would splice an unquoted fragment into YAML, which is where the quoting
# and type traps live. Compose such values in brief() instead.
_WHOLE_SCALAR = re.compile(r"^(?P<lead>[^\S\n]*(?:- )?(?:[\w.-]+:[^\S\n]+)?)\{(\w+)\}[^\S\n]*$")
_ANY_PLACEHOLDER = re.compile(r"(?<!\{)\{(\w+)\}")


def render_solution(meta, brief):
    """The reference manifest for this sitting, with each placeholder serialised as the
    YAML scalar its value actually is."""
    template = (meta["dir"] / "solution.yaml").read_text(encoding="utf-8")
    out = []
    for number, line in enumerate(template.split("\n"), 1):
        match = _WHOLE_SCALAR.match(line)
        if match:
            key = match.group(2)
            if key not in brief:
                raise Rejected(f"solution.yaml line {number}: no brief value for {key!r}")
            out.append(match.group("lead") + _scalar(brief[key]))
        elif _ANY_PLACEHOLDER.search(line):
            raise Rejected(
                f"solution.yaml line {number}: a placeholder must be a whole value; "
                "build the combined value in brief() instead"
            )
        else:
            out.append(line)
    rendered = "\n".join(out)
    try:
        yaml.safe_load(rendered)
    except yaml.YAMLError as exc:
        raise Rejected(f"the rendered solution is not valid YAML: {exc}") from None
    return rendered


def _scalar(value):
    """One value as YAML, with its type and quoting intact. `yaml.safe_dump` of a bare
    scalar is exactly this question, so ask it rather than reimplementing the quoting rules."""
    return yaml.safe_dump(value, default_flow_style=True, width=1 << 30).strip().removesuffix("\n...")
```

Serve `render_solution(meta, o["brief"])` from `api.solution_task` when the kind is a manifest, keeping the existing gate untouched.

- [ ] **Step 4: Run the tests**

Run: `uv run pytest tests/test_manifest.py -v -k solution`
Expected: PASS.

- [ ] **Step 5: Run the full suite and lint**

Run: `uv run pytest tests/ -q && uv run ruff check && uv run ruff format --check`

- [ ] **Step 6: Commit**

```bash
git add src/drillion/manifest.py src/drillion/api.py tests/test_manifest.py
git commit -m "feat(manifest): render the reference solution as typed YAML scalars"
```

---

### Task 15: The editor speaks YAML

**Files:**
- Modify: `web/src/api.ts:10`, `web/src/Editor.tsx:5,27,60,63,280`, `web/src/Task.tsx:295`
- Test: `web/tests/` via `pnpm --dir web screens`

**Interfaces:**
- Consumes: `kind` in the task payload's `meta` from Task 1.
- Produces: `Meta.kind: "python" | "manifest"`, `Meta.tier?: ...` optional.

- [ ] **Step 1: Make the types honest**

In `web/src/api.ts`, `tier` becomes optional and `kind` arrives:

```ts
difficulty: "easy" | "medium" | "hard"; tier?: "core" | "advanced" | "packages"; track?: string;
kind: "python" | "manifest"; filename: string;
```

In `web/src/Catalogue.tsx:28`, `facets` must tolerate a missing tier:

```ts
const facets = (row: Row) => [row.tier, row.track, ...row.tags].filter(Boolean) as string[];
```

and `TaskPath` renders the track when there is no tier.

- [ ] **Step 2: Register YAML and pick the language per task**

In `web/src/Editor.tsx`, beside the existing Python registration:

```ts
import "@codingame/monaco-vscode-standalone-languages/languages/definitions/yaml/register.js";
```

Replace the module-level `FILE` constant with one derived from the task, and gate the language client so a manifest never gets the Python LSP:

```ts
const fileFor = (kind: Meta["kind"]) =>
  kind === "manifest" ? `${WORKSPACE}/task.yaml` : `${WORKSPACE}/solve.py`;
const languageFor = (kind: Meta["kind"]) => (kind === "manifest" ? "yaml" : "python");
```

Diff models at `Editor.tsx:280` take the same extension. Dispose the old model and, when switching away from Python, stop the language client before creating the new one.

- [ ] **Step 3: Hide the case panel for a manifest**

In `web/src/Task.tsx`, render the generated-arguments panel only when `meta.kind === "python"`. The run response already returns `case: null` for a manifest from Task 13, so this is about not showing an empty panel that reads as a bug.

- [ ] **Step 4: Build and check the screens**

Run: `pnpm --dir web build && pnpm --dir web screens`
Expected: the build passes and the Playwright screens are green. Restart the server before looking at it by hand; a rebuild alone leaves an open tab on the old bundle.

- [ ] **Step 5: Lint**

Run: `pnpm --dir web lint && uv run pytest tests/ -q`

- [ ] **Step 6: Commit**

```bash
git add web/src
git commit -m "feat(web): edit manifests as YAML and keep the python LSP off them"
```

---

### Task 16: The fixture passes end to end

The phase gate. This is the same vertical slice that becomes `271_first_deployment` in phase 2, exercised through the application rather than through unit seams.

**Files:**
- Create: `tests/test_manifest_e2e.py`
- Test: itself

**Interfaces:**
- Consumes: everything above.
- Produces: nothing.

- [ ] **Step 1: Write the failing test**

Create `tests/test_manifest_e2e.py`:

```python
"""One manifest sitting, through the API, from an empty file to a reset one."""

import shutil

import pytest

from drillion import manifest, tools
from drillion.settings import settings
from tests.fixtures import tasks_root
from tests.fixtures_manifest import fixture_task


@pytest.fixture
def fixture_app():
    if tools.installed(tools.KUBECONFORM) is None:
        pytest.skip("kubeconform is not installed: run `drillion doctor --fetch`")
    tmp = tasks_root(**{"271_fixture": fixture_task()})
    keep = settings.root
    settings.root = tmp
    yield tmp
    settings.root = keep
    shutil.rmtree(tmp, ignore_errors=True)


def test_a_sitting_goes_from_empty_to_passed_to_reset(fixture_app, client):
    opened = client.post("/api/task/271_fixture/open").json()
    assert opened["code"] == "", "a manifest task opens empty"
    assert "{name}" not in opened["spec_md"], "the brief is rendered, not templated"

    wrong = client.post(
        "/api/task/271_fixture/run",
        json={"code": "kind: Deployment\n", "etag": opened["etag"], "submit": False},
    ).json()
    assert not wrong["passed"]

    meta = __import__("drillion.catalogue", fromlist=["tasks"]).tasks()["271_fixture"]
    brief = client.get("/api/task/271_fixture").json()
    correct = manifest.render_solution(meta, _stored_brief())
    done = client.post(
        "/api/task/271_fixture/run",
        json={"code": correct, "etag": wrong["etag"], "submit": True},
    ).json()
    assert done["passed"] and done["graded"] and done["grade"]

    assert (settings.tasks_dir / "271_fixture" / "task.yaml").read_text(encoding="utf-8") == ""
    after = client.get("/api/task/271_fixture").json()
    assert after["code"] == "" and after["archive"][-1]["revision"].startswith("m1:")


def test_two_sittings_ask_for_different_things(fixture_app, client):
    """The whole point: the answer cannot be pasted back."""
    seen = set()
    for _ in range(12):
        opened = client.post("/api/task/271_fixture/open").json()
        seen.add(opened["spec_md"])
        client.post("/api/task/271_fixture/abandon", json={"etag": opened["etag"]})
    assert len(seen) > 1
```

Write `_stored_brief()` to read the open attempt's brief through `state.reading()`, and reuse the existing client fixture from `tests/test_api.py` by importing it or moving it into a shared `tests/conftest.py`.

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_manifest_e2e.py -v`
Expected: FAIL, or SKIP if the pins are not yet filled in. If it skips, fill the pins from the chosen kubeconform release first: this test is the phase gate and a skipped gate proves nothing.

- [ ] **Step 3: Fix whatever it finds**

No new implementation is planned here. Anything this test catches is a defect in Tasks 1 to 15, and the fix belongs in the module that owns it.

- [ ] **Step 4: Run the whole suite on a clean checkout**

Run: `uv run pytest tests/ -q && uv run ruff check && uv run ruff format --check`
Then confirm the real catalogue is untouched: `uv run drillion doctor` reports no new reasons, and `uv run python -c "from drillion.runner import selfcheck; raise SystemExit(selfcheck())"` still reports every Python task passing.

- [ ] **Step 5: Commit**

```bash
git add tests/test_manifest_e2e.py
git commit -m "test(manifest): grade one fixture sitting end to end through the api"
```

---

## What phase 1 deliberately does not do

Carried to the phase 2 plan, per the spec:

- `runner.selfcheck()` still assumes Python. No manifest may enter `tasks/` until it does not.
- Backup stays at `FORMAT = 1` and stores `.py` regions only. Mixed-kind bundles, format 2 and legacy reading are phase 2.
- The pins are filled and the wheel, sdist and Docker image are proved to grade offline in phase 2.
- `271_first_deployment` is promoted from the fixture in phase 2, after those gates pass.

## Self-review notes

- **Spec coverage.** Tasks 1 to 16 cover the spec's Vocabulary, A task on disk, grade.py contract, The seeded spec, Grading, The region, Pending reset and recovery, Grading fingerprint, Acquiring the tools, Sandbox and Editor sections. selfcheck and Backup are intentionally out of this plan and named above.
- **Known type consistency risk.** `runner.run_tests(path, seed)` becomes `runner.run_python(meta, seed)` in Task 13, and every caller goes through `kinds.of(meta).grade(meta, o)` instead. Task 3 touches the caller and Task 13 renames the callee; whichever runs second updates `tests/test_runner.py` alongside. Task 2 defines `grade()` against the old name, so Task 13 must update `_Python.grade` in the same commit that renames it.
- **`has_given`** becomes a kind method rather than a branch in `_payload`. `_Python.has_given` is the existing function; `_Manifest.has_given` returns False, because a manifest has no code above `solve()` to keep. Add it to the class in Task 2 alongside `opening`, `spec` and `grade`.
- **One per-kind table is left outside `kinds.py` on purpose.** `doctor._value_rules` decides which frontmatter fields each kind may carry, and `catalogue.CHECKS` decides which files it must have. Both are data keyed by kind name, one entry per kind, and both live in modules that `kinds` imports from. A third kind adds a row to each; neither grows a branch.
