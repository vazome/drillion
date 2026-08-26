# Content format — one folder per drill, guidance in Markdown

Decided with Daniel 2026-08-25. Replaces "the spec is `solve`'s docstring, HINTS is a Python list".

## Why

Python docstrings cannot carry headings, code blocks, callouts, diagrams or images, so the spec
pane can only style text. Guidance moves to GitHub-flavoured Markdown; the Python file becomes code
only. Side effects, all good: the docstring hide/restore layer (`strip_spec`/`merge_spec`, the
"never write without a docstring" gate) is deleted; Exercism content (already Markdown) is kept
verbatim instead of paraphrased; assets (SVG, Mermaid, Manim-rendered video) sit next to the drill.

## Layout

```
exercises/
  _lib.py                         seeded Random (unchanged)
  019_counter/                    slug = folder name = "<topic>_<name>"; topic = leading integer
    README.md                     guidance (frontmatter = META) — see "README.md"
    drill.py                      learner region + machinery — see "drill.py"
    assets/                       optional: images, .webm, mermaid sources, manim scenes
  300_two_fer/
    ...
```

Slugs change from `ex_019_counter` to `019_counter` everywhere (`progress.json` keys, API paths,
URLs). Topic numbers keep their meaning (section tag ranges, prereqs, `200 + 3k + i`, `300+`).

## drill.py

```python
from collections import Counter          # ← learner region starts at line 1: the learner's imports,

TRUTHY = {"1", "true", "yes"}            #   given code (# given — do not edit), and solve()

def solve(lines, n):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══   ← MARKER, verbatim
from _lib import rng                     # noqa: E402

def _gen(r): ...
def _reference(lines, n): ...
def test_solve(): ...
```

- No module docstring, no META, no HINTS, no READ FIRST/SOURCE comments in the `.py`.
- **Region** = every line above the MARKER line (`# ══ machinery` … first line that starts with
  `# ══ machinery`). `bounds(src)` returns the marker line index; `cut` → `body, tail`;
  `splice(src, body)` = body + "\n\n\n" + tail (blank-line normalised); `etag` = sha256 of body.
- `stub(body)`: everything before `solve` (imports, given code, decorators) + `solve`'s signature +
  `    raise NotImplementedError`. `has_given(body)`: any non-import statement before `solve`.
- `validate(edited, disk_src)`: parses; exactly one top-level `def solve`; no `_reference/_gen/
  test_*` defs and no `Name("_reference")`; non-empty; the marker is not in the edited text; the
  spliced file parses. No docstring rule any more (a learner may write one; it is just code).
- `solve` may have a one-line docstring in authored files? **No** — keep the stub minimal; the spec
  is the README.
- `_lib` is imported below the marker (only machinery needs it). pytest `pythonpath = ["exercises"]`.
- `python_files = ["drill.py", "test_*.py"]`; `testpaths = ["tests", "exercises"]`; ruff per-file
  ignores `"exercises/*/drill.py" = ["E402", "F841"]`.
- `selfcheck` writes `exercises/<slug>/_selfcheck.py` (explicit paths are always collected) and
  deletes it in `finally`.

## README.md

```markdown
---
title: Top-N crashing services
difficulty: medium       # easy | medium | hard
tier: core               # core | advanced | packages
track: rsample            # optional, a themed run through the corpus
minutes: 12
prereqs: [18]
tags: [collections]
practices: []            # optional, whole-task drills
source: exercism/python practice/two-fer (MIT, adapted)   # optional, Exercism drills
---
# Top-N crashing services

## Why
A team lead asks "which services are crashing the most?" …

## You get
`lines` — a list of strings like

```python
"2026-08-25 ERROR api timeout"
```

and `n` — how many services to report.

## You return
A list of `(service, count)` tuples, most frequent first; ties broken alphabetically.

## Rules
- count only lines whose level is `ERROR`
- service is the third whitespace-separated field

```python
solve(["..ERROR api..", "..ERROR api..", "..ERROR db.."], n=2)  # -> [("api", 2), ("db", 1)]
```

## Read first
- [collections.Counter](https://docs.python.org/3/library/collections.html#collections.Counter) — `most_common()` does the sorting for you
- [sorting with key=](https://realpython.com/...) — refresher on tie-breaking with tuples

> [!NOTE]
> **Take-home:** `sorted(rows, key=score)` is the same move on the RAG scores.

## Hints
### Hint 1
…
### Hint 2
…
### Hint 3
…
```

- Frontmatter is YAML (PyYAML `safe_load`, runtime dependency), written in this key order:
  `title`, `difficulty`, `tier`, `track?`, `minutes`, `prereqs`, `tags`, `practices?`, `source?`.
  Required: `title`, `difficulty`, `tier`, `minutes`, `tags`. Optional: `track`, `prereqs`
  (default `[]`), `practices`, `source` — an optional key is omitted, never written empty.
  `topic` is **not** in the frontmatter: it is the folder's leading number.
- `difficulty` is `easy` | `medium` | `hard` — how hard the task is to *get right*, judged from
  its rules, not from `minutes`. `minutes` is par time for grading and the learner never sees it.
- `tier` is `core` | `advanced` | `packages` — stdlib fundamentals, harder stdlib work, and
  third-party libraries. `track` names an optional themed run (`rsample`) and is usually absent.
- `tags` are concepts, 1-3 of them, and nothing else. Four tags that used to do other jobs are
  gone: `exercism` → `source:`, `core` and `data-structures` → `tier:`, `whole-task` →
  `difficulty: hard`, `rsample` → `track:`.
- `focus` in `progress.json` matches one string against a task's `tier`, `track` and `tags`
  alike, so all three are filters.
- Headings are the contract: `# <title>` then `## Why`, `## You get`, `## You return`, `## Rules`,
  `## Read first`, `## Hints` with `### Hint 1..3`. Extra sections are allowed anywhere before
  `## Hints` (Exercism drills add `## Introduction` and `## Instructions`).
- **Spec** = the body from `# title` up to `## Hints`. **Hints** = the `### Hint N` sections, in
  order; exactly 3. The server never sends a hint the learner has not unlocked.
- GFM features the renderer supports: headings, lists, tables, fenced code with language,
  images (`assets/...`, resolved to `/api/ex/{slug}/assets/...`), GitHub alerts (`> [!NOTE]`,
  `[!TIP]`, `[!WARNING]`), ```mermaid diagrams, and `![…](assets/x.webm)` rendered as a muted
  looping video. No raw HTML.

### Exercism drills — keep their content, add ours

For a drill adapted from Exercism the README **contains Exercism's Markdown verbatim** and our
material around it:

```
# <title>
## Why                       ours: the business framing (who needs this, why)
## Introduction              Exercism .docs/introduction.md verbatim (concept drills; practice if present)
## Instructions              Exercism .docs/instructions.md verbatim (+ instructions.append.md)
## You get / ## You return   ours: the exact signature of `solve` in this repo (dict of functions,
                             class returned, defaults), literal examples
## Rules                     ours: only what Exercism's text leaves open and the tests need
                             (error messages verbatim, ordering, types)
## Read first                concepts/<slug>/links.json → list; or hand-picked docs anchors
## Hints                     Exercism .docs/hints.md content folded into Hint 1–2 where it fits;
                             Hint 3 = ours, the same idea on different data
```
Attribution: frontmatter `source:` plus `*Adapted from [exercism/python](…) — MIT.*` placed after
`## Read first` and **before `## Hints`** — not at the end of the file. `guidance()` partitions the
README at `\n## Hints\n` and splits the remainder on `### Hint N`, so a line below the hints is
swallowed into hint 3 and never renders in the spec pane. `303_bob`, `335_nth_prime` and `338_clock`
are the models.
Never trim Exercism's wording to make room; the spec pane scrolls.

## API changes

- `GET /api/catalogue` rows: `slug` (`019_counter`), `topic`, `title`, `minutes`, `tags`, `prereqs`,
  `practices`, status fields — unchanged shape, new slug form.
- `GET /api/ex/{slug}`: `spec` becomes **Markdown** (`spec_md`), `read_first` and `doc_offset` are
  removed (links live in the Markdown; no docstring offset), `hints.shown` are Markdown strings,
  `code`/`etag`/`has_given`/`region_start` (= 1)/`marker_line` stay. `meta` gains `source`.
- `GET /api/ex/{slug}/assets/{name}` → `FileResponse` from `<dir>/assets/<name>`; `name` must be a
  plain filename (no `/`, no `..`), 404 otherwise.
- Everything else (PUT/run/touch/hint/solution/abandon/focus/progress/health) unchanged.

## Migration (one-off script, deleted after)

For each `exercises/ex_<NNN>_<name>.py` (104 files):
1. Create `exercises/<NNN>_<name>/`; move machinery (`_gen`, `_reference`, `test_solve`, helpers,
   `from _lib import rng`) below the MARKER into `drill.py`; keep the learner region as-is minus the
   docstring (preserves ex_016's open draft; every other file stays a stub).
2. README.md from: META → frontmatter; docstring → sections by its `WHY:` / `YOU GET:` /
   `YOU RETURN:` / `─── exact rules ───` labels; lines that look like `solve(...) -> ...` or
   `name(...)  ->` examples become a ```python fence; READ FIRST comment block → `## Read first`
   list (`url — note`), `TAKE-HOME:` → `> [!NOTE]` callout; `# SOURCE:` → frontmatter `source`;
   HINTS → `### Hint 1..3`.
3. `progress.json`: rename keys in `cards`, `open`, `log[].slug`, `archive` (`ex_` prefix dropped).
4. Verify: 104 folders; `uv run study selfcheck` 104/104; every README parses with the required
   headings and exactly 3 hints; `git status` shows only renames + README adds; the ex_016 draft
   body is byte-identical in `drill.py`.

The 17 Exercism drills then get a content pass (Task 11): README rebuilt per "Exercism drills —
keep their content, add ours" from `/tmp/exercism-python` sources. Native drills get a light pass:
examples fenced, callouts, tables where a rule list is really a table.

## Out of scope now

MDX/interactive content (per-file upgrade later), folder-per-drill assets tooling, Manim in the
build (render offline, commit the `.webm`).
