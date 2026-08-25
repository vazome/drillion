# Task 10 report — content format: one folder per drill, guidance in Markdown

Branch `main`, three commits on top of `6198cda`. Tree clean, 104 drills, everything green.

| commit | subject |
|---|---|
| `904b528` | Core: marker region, Markdown guidance, folder per drill |
| `a0af83d` | Migrate drills to folders |
| `b146bdb` | Remove the migration script |

---

## Step 1 — Core (`src/study/`)

**`region.py`** — rewritten around one marker line.

```python
MARKER = "# ══ machinery — everything below is the grader's, not yours ══"
```

- `bounds(src)` → the 1-based line of the marker; `cut(src)` → `Region(body, tail)` (a
  `NamedTuple`, so `cut(src).body` still reads); `splice(src, body)` = `body.strip("\n") +
  "\n\n\n" + tail`; `etag` = sha256 of the body, 12 hex chars.
- `stub(body)` = everything before `solve`'s first statement (imports, given code, decorators, the
  signature) + `raise NotImplementedError`. It refuses a one-line body (`def solve(x): return x`)
  because a pass has to be able to rewrite the file to a stub.
- `has_given(body)` moved here from `catalogue.py` (per the brief).
- `validate(edited, disk_src)` — non-empty, parses, exactly one top-level `def solve`, no
  `_reference`/`_gen`/`test_*` definitions, no `Name("_reference")`, the marker is not in the
  edited text, `stub(edited)` is possible, the spliced file parses.
- **Deleted**: `strip_spec`, `merge_spec`, `Spec`, `doc_offset`, the docstring gate in
  `write_region`, and the `_docstring`/`_str_expr`/`_assign` helpers. A learner may now write a
  docstring; it is just code.

**`catalogue.py`** — reads folders, not files. `frontmatter(md)` splits the YAML header
(`yaml.safe_load`) from the body; `guidance(md)` splits the spec (everything above `## Hints`)
from the `### Hint N` sections. `exercises()` walks `exercises/*/`, takes `topic` from the
folder's leading number, requires `title` / `minutes` / `tags` and exactly 3 hints, and skips a
folder that fails any of it. Entry keys: frontmatter + `topic`, `path`, `dir`, `hints`,
`spec_md`, `marker_line`.

**`runner.py`** — `summarise(out, marker_line)`; the region starts at line 1 so the map is the
identity, and the regex was tightened from any `*.py:NN` to `*drill.py:NN` so a frame in `_lib`
or in pytest itself is never rewritten. `selfcheck` writes `exercises/<slug>/_selfcheck.py` and
deletes it in `finally`. Both subprocesses now pass `--import-mode=importlib` and
`PYTHONPATH=<exercises dir>` explicitly, so they work from a temp root with no `pyproject.toml`.

**`api.py`** — payload per the spec: `spec_md`, `region_start` (always 1), `marker_line`; `spec`,
`read_first`, `doc_offset` and `hints_line` are gone; `meta` gains `source` (and `practices`).
New `GET /api/ex/{slug}/assets/{name}` → `FileResponse` from `<dir>/assets/<name>`, 404 unless
`name` is a plain filename that exists. `_coords()` collapsed into `bounds()`.

**`attempts.py`** — `abandon` archives the region as-is (there is no spec to strip).

**`pyproject.toml`** — `pyyaml>=6.0.3` in `[project.dependencies]`; pytest
`python_files = ["drill.py", "test_*.py"]`, `testpaths = ["tests", "exercises"]`,
`pythonpath = ["exercises"]`, `addopts = "--import-mode=importlib"`; ruff per-file ignores moved
from `"exercises/*"` to `"exercises/*/drill.py"`.

`settings.py`, `state.py`, `scheduler.py`, `cli.py` unchanged.

## Step 2 — Tests

`tests/test_region.py` and `tests/test_catalogue.py` rewritten; `test_api.py` rewritten around a
copied drill *folder* plus an `assets/` fixture; `test_runner.py` for the new `summarise`
signature; `test_attempts.py` and `test_scheduler.py` moved to new-form slugs (`001_a`, `002_b`,
`003_c`). 37 tests (was 43 — the eight `merge_spec`/`strip_spec` tests describe code that no
longer exists; four new tests were added: marker-on-every-drill, learner-docstring accepted,
broken-folder-skipped, assets endpoint).

### TDD evidence

**RED** — the new tests, written before any implementation:

```
$ uv run pytest tests/test_region.py tests/test_catalogue.py -q
tests/test_region.py:18: in <module>
    SRC = (settings.exercises_dir / "001_fstrings" / "drill.py").read_text()
E   FileNotFoundError: [Errno 2] No such file or directory:
    '/home/daniel/study/exercises/001_fstrings/drill.py'
tests/test_catalogue.py:33: in <module>
    f"{region.MARKER}\nfrom _lib import rng  # noqa: E402\n"
E   AttributeError: module 'study.region' has no attribute 'MARKER'
=========================== short test summary info ============================
ERROR tests/test_region.py - FileNotFoundError: [Errno 2] No such file or dir...
ERROR tests/test_catalogue.py - AttributeError: module 'study.region' has no ...
!!!!!!!!!!!!!!!!!!! Interrupted: 2 errors during collection !!!!!!!!!!!!!!!!!!!!
2 errors in 0.19s
```

**GREEN (logic, before any content was migrated)** — the two catalogue tests that build their own
throwaway `exercises/` root, so they do not need migrated drills:

```
$ uv run pytest tests/test_catalogue.py -q -k "topic_comes or broken_folder"
..                                                                       [100%]
2 passed, 2 deselected in 0.05s
```

**GREEN (everything, after the migration)** — see step 5. The content-sweeping tests
(round-trip on all 104 drills, stub identity, every README's contract) cannot go green before the
drills exist; that is why commit `904b528` is red on its own and commit `a0af83d` is green. It is
the unavoidable seam in the mandated two-commit split of one change.

## Step 3 — Migration

`migrate.py` at the root, run once, deleted in `b146bdb`. Per drill it:

1. `git mv exercises/ex_<NNN>_<name>.py exercises/<NNN>_<name>/drill.py`, then rewrites the file:
   the learner's region (old META…HINTS block minus `solve`'s docstring) on top, the marker, the
   machinery imports, the machinery.
2. Writes `README.md`: META → frontmatter; the docstring's `WHY:` / `YOU GET:` / `YOU RETURN:` /
   `─── exact rules ───` labels → `## Why` / `## You get` / `## You return` / `## Rules`; indented
   example runs → fenced blocks (```` ```python ```` when a line looks like code, a plain fence
   otherwise); the `# READ FIRST:` block → `## Read first` bullets; `TAKE-HOME:` → a `> [!NOTE]`
   callout; `# SOURCE:` → frontmatter `source` plus a closing attribution line; HINTS →
   `### Hint 1..3`.
3. `progress.json`: `ex_` dropped from the keys of `cards`, `open` and `archive` and from
   `log[].slug`.

### Decisions the spec left open

| decision | why |
|---|---|
| Imports above the old `META` that the region never names move **below** the marker (`from _lib import rng` and 103 others); only the 2 that the region uses stay above (`098_fixtures`: `asyncio`, `pytest`; `099_asgi_test`: `FastAPI`). | The spec puts `_lib` below the marker because "only machinery needs it". Same rule, applied by name analysis. Keeps the stub the learner sees free of seven imports they never touch. |
| A blank line between the marker and the machinery imports (the spec's example has them adjacent). | Ruff's isort attaches a comment directly above an import to that import and moves it when sorting. A blank line keeps the marker out of the import block. `bounds`/`cut`/`splice` do not care. |
| No `# noqa: E402` on the moved imports (the spec's example line has one). | E402 is **not** in this repo's enabled ruff rule set, so the directive would itself be an error (RUF100, which *is* enabled). The `["E402", "F841"]` per-file ignore is still in `pyproject.toml` as the brief asks. What ruff actually flags here is I001, fixed by `ruff check --fix` after the migration. |
| The old module docstring becomes the lede under `# title`: italic when it is one line, plain when it is two paragraphs (16 drills). | Emphasis cannot span a blank line. Nothing else in the layout holds it, and dropping it would lose content. |
| The Exercism attribution line sits just above `## Hints`, i.e. at the end of the spec. | The spec says "a last line"; the spec pane is what the learner reads, and `## Hints` is not part of it. |
| `─── the questions ───` (101 only) becomes `## Rules` with `**The questions**` as its first line. | Keeps the block's own name. Reported below. |
| `YOU GET:` appearing twice (4 drills, one label per argument) concatenates into one `## You get`. | First pass overwrote the first paragraph; caught by the word-for-word check and fixed. |

### Drills the converter could not classify cleanly

- **`101_explain_takehome`** — the only one. Its rules block is titled `─── the questions ───`
  rather than `─── exact rules ───`, and its body is a 10-question quiz whose lettered options
  (`a)`…`d)`) are not Markdown list markers, so a renderer folds each question's options into the
  question's paragraph. Every word is present and correctly placed under `## Rules`; the layout
  needs Task 11.
- Not a classification failure but worth listing for Task 11: **31 drills** have a
  ```` ```python ```` fence whose content is the repo's `call  ->  result` example notation
  (`solve([4, 1, 3, 2], 50)          ->  2`), which is not valid Python. It highlights fine; the
  spec's own example writes the same thing as a `# ->` comment.

### Hand-edits to drills (the only two)

1. **`059_mock`** — its `_reference`, rules and hint 2 taught
   `patch(f"{__name__}.send_alert")`. Under the new module names
   (`exercises.059_mock.drill`) `unittest.mock` cannot resolve that target:
   `pkgutil.resolve_name` rejects a dotted name whose parts start with a digit
   (`ValueError: invalid format: 'exercises.059_mock._selfcheck'`), and every drill folder starts
   with a digit. The drill now teaches `patch.object(sys.modules[__name__], "send_alert")` — the
   same lesson ("patch the name in the module that uses it"), in the spelling `098_fixtures`
   already used — with `import sys` given at the top of the region and the "no imports beyond
   unittest.mock" constraint updated. Without this the selfcheck is 103/104.
2. **`098_fixtures`** — one prose reference to "ex_096", a slug that no longer exists → "drill 096".

Both are in commit `a0af83d`'s message.

## Step 4 — Docs

`README.md`: the intro sentence, the session walkthrough, the Layout tree, the Development
commands, and "The exercises" rewritten — the `README.md` frontmatter/heading contract, the
`drill.py` marker sketch, the region contract in marker terms, the Exercism-verbatim rule, and the
Track/tags wording (`source:` frontmatter, Take-home callout). Status line updated to 104 drills.

`DESIGN.md`: `GET /api/ex/{slug}` now documents `spec_md` as GitHub-flavoured Markdown with the
exact feature list the renderer must support (headings, lists, tables, fenced code with language,
`> [!NOTE]`/`[!TIP]`/`[!WARNING]`, ```` ```mermaid ````, images from
`GET /api/ex/{slug}/assets/{name}`, `![…](assets/x.webm)` as a muted looping video, no raw HTML),
notes the pane scrolls and must not truncate, and says hints are Markdown rendered the same way.
`read_first` and `doc_offset` are gone from the brief.

## Step 5 — Verification (pasted)

```
$ uv run pytest tests -q -W error
.....................................                                    [100%]
37 passed in 2.59s

$ uv run ruff check .
All checks passed!

$ uv run study selfcheck
104/104 ok

$ ls -d exercises/*/ | wc -l
104

$ uv run python verify_readmes.py
104/104 READMEs: frontmatter, headings and 3 hints ok

$ git status --short  →  (empty: clean)
```

`verify_readmes.py` (a throwaway, not committed) asserts per folder: the frontmatter parses and
holds only `title`/`minutes`/`prereqs`/`tags`/`practices`/`source`, `title`+`minutes`+`tags` are
present and typed, `topic` is *not* in the frontmatter, the spec starts with `# <title>` and
contains `## Why`, `## You get`, `## You return`, `## Rules`, there are exactly 3 non-empty hints,
`## Hints` is not in the spec, and `catalogue.exercises()` returns the folder with
`topic == int(folder.split("_")[0])`.

**Boot smoke — the real server, not ASGI:**

```
$ STUDY_OPEN_BROWSER=0 STUDY_PORT=8811 uv run study &
$ curl -s -w "\nHTTP %{http_code}\n" http://127.0.0.1:8811/api/health
{"status":"ok","exercises":104,"root":"/home/daniel/study"}
HTTP 200

$ curl -s http://127.0.0.1:8811/api/ex/019_counter | ...
spec_md starts with "# ": True
'# Counter — top N by frequency\n\n*Top-N counting — the single'
region_start 1 marker_line 5

$ curl -s -w "\nHTTP %{http_code}\n" \
    "http://127.0.0.1:8811/api/ex/019_counter/assets/..%2Fdrill.py"
{"error":"Not Found"}
HTTP 404
```

Over ASGI the same endpoint reports the removed fields are gone and `meta` carries the new shape:

```
GET /api/ex/019_counter -> 200
  keys present of (spec, spec_md, read_first, doc_offset, region_start, marker_line):
      ['marker_line', 'region_start', 'spec_md']
  meta: {"prereqs": [18], "practices": [], "title": "Counter — top N by frequency",
         "minutes": 12, "tags": ["data-structures"], "topic": 19}
  hints total/shown: 3 []
GET /api/ex/019_counter/assets/..%2Fdrill.py -> 404
catalogue: total 104, first slug 001_fstrings, 30 tags
```

**`progress.json` — key renames only:**

```
$ diff <(sed 's/"ex_/"/g' progress.before.json) <(git show HEAD:progress.json)
  (no output) — identical after dropping the ex_ prefix
```

**`016_typehints` — the open draft is byte-identical:**

```
$ git show HEAD:exercises/016_typehints/drill.py | head -9
def solve(fn):
    from typing import get_type_hints
    modifications = get_type_hints(fn)
    zone = modifications["zone"]
    returnal = modifications["return"]

    print(get_type_hints(fn))

    raise NotImplementedError
```

A script comparing that region against the old file's region-minus-docstring, computed from
`/tmp/exercises.before/ex_016_typehints.py`, prints `identical: True`.

**`git status` on the old→new mapping.** Git reports 104 deletions + 208 additions rather than 104
renames: the docstring, META, HINTS and READ FIRST block were the bulk of each old file, so
`drill.py` falls under the default 50% similarity threshold. At `-M25%` git pairs 77 of them:

```
$ git diff --cached -M25% --summary | grep -c "^ rename"
77
```

## Self-review of the diff

**Word-for-word content check.** A script reconstructs the old guidance (module docstring +
`inspect.cleandoc(solve.__doc__)` + the READ FIRST comment lines + the three HINTS strings) and the
new one (README body minus frontmatter, heading lines, fence delimiters, the `> [!NOTE]` line, the
attribution line, and the `- ` added to Read-first bullets; `**Take-home:**` mapped back to
`TAKE-HOME:`, `**The questions**` back to `─── the questions ───`), normalises both to token lists
and diffs them. Structural label tokens (`WHY:`, `YOU GET:`, `YOU RETURN:`, `─── exact rules ───`,
`READ FIRST`) and bare `-` are excluded.

All 104 drills:

```
101/104 drills: every word of the old docstring, READ FIRST and HINTS is present
in the new README, in order
059_mock              -file, -and -f"{__name__}.send_alert"  →  +file. +This +module +is …
098_fixtures          -ex_096  →  +drill +096
101_explain_takehome  -memory):  →  +memory)
```

The three differences are all accounted for: the two deliberate hand-edits above, and one dropped
`:` — `101`'s READ FIRST heading reads `READ FIRST (…these come from — re-read…):`, and stripping
the `READ FIRST` label takes its trailing colon with it. Nothing else changed.

The 10-drill sample the brief asked for (`001_fstrings`, `016_typehints`, `019_counter`,
`023_itertools`, `035_subprocess`, `044_customexc`, `073_p95`, `098_fixtures`, `300_two_fer`,
`309_rna_transcription`) — chosen to cover a plain drill, the open draft, a multi-`YOU GET:` drill,
a bullet-heavy drill, a given-code drill, a whole-task drill with a two-paragraph module docstring,
a decorated/`sys.modules` drill and two Exercism drills:

```
9/10 drills: every word of the old docstring, READ FIRST and HINTS is present in
the new README, in order
098_fixtures ['-ex_096', '+drill', '+096']
```

**Markdown sanity sweep, all 104 READMEs:** fences balanced, no `WHY:` / `YOU GET:` /
`─── exact rules ───` left anywhere, no malformed headings, no triple blank lines outside fences,
every file ends in a newline. Clean.

**Invariants re-checked on the committed tree:** every `drill.py` round-trips
(`splice(src, cut(src).body) == src`), the marker is the first line of every tail, `stub(body) ==
body` for all 103 drills without an open attempt, no `_reference`/`test_` text leaks into any
region, `from _lib import rng` is below the marker in all 104, and `validate` accepts every
pristine region.

**Leftovers:** `grep` for `read_first`, `doc_offset`, `hints_line`, `strip_spec`, `merge_spec`,
`HINTS = [`, `META = {` across `*.py`/`*.md`/`*.ts`/`*.tsx` (excluding `.superpowers/`) returns
nothing. `web/README.md`, `Dockerfile`, `compose.yaml`, `.github/workflows/ci.yml` needed no
change (CI runs exactly the three verified commands).

## Concerns

1. **`--import-mode=importlib` is load-bearing, and it is not in the spec.** Every drill file is
   called `drill.py`, so pytest's default prepend mode aborts collection with
   `import file mismatch`. importlib mode names modules by path instead. Consequence: a drill's
   `__name__` is `exercises.059_mock.drill`, which is not a valid dotted identifier — that is what
   broke `059_mock`, and it will break any future drill that patches or imports *itself* by name.
   Worth a line in the drill-authoring section if another such drill appears.
2. **Commit `904b528` does not pass its own tests in isolation** (the content-sweeping tests need
   the migrated drills, which arrive in `a0af83d`). Inherent to the mandated commit split; HEAD is
   green.
3. **31 drills carry ```` ```python ```` fences that are the `call -> result` notation, not
   Python**, and `101_explain_takehome`'s quiz options do not render as a list. Both are content
   polish, explicitly Task 11's job; nothing is lost.
4. **Rename detection.** `git log --follow` on a drill will need `-M25%` or lower to walk past this
   commit. Unavoidable: the file genuinely lost two thirds of its bytes to `README.md`.
5. **The global constraint "an exercise file is never written without `solve`'s docstring" is
   gone**, deliberately: the content-format spec (2026-08-25) supersedes it — the spec is the
   README now, and `validate` guards the marker, the machinery names and the splice instead.
