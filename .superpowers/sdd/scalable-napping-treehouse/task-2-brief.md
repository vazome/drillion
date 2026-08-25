### Task 2: `study.py` core + `test_study.py` (TDD)

Rewrite `study.py` per the design sections above ("Catalogue", "Region + splice", "State",
"Scheduler", "Attempt lifecycle", "selfcheck", and the `summarise`/`run_tests` notes under "API").
Read those sections in the plan file `/home/daniel/.claude/plans/scalable-napping-treehouse.md`
(everything above "## Tasks") — they are the spec. Deliverables:

- Keep: `ROOT`, `LADDER`, `INTERVIEW`, `NEW_PER_DAY`, `GRADES`, `load/save/today/card/due_today/
  pick/grade_of/reschedule/_solution`. Change `EXDIR = ROOT/"exercises"`, `STATE = ROOT/
  "progress.json"`; `load()` returns `{"focus": None, "cards": {}, "open": {}, "log": [], "archive": {}}`
  when missing and fills missing keys on old files. Delete `cmd_next/cmd_check/cmd_hint/cmd_status`.
- New pure functions with these exact names: `bounds`, `cut` (returns a small dataclass or tuple
  `head, lead, body, trail, tail`), `splice`, `strip_spec` (returns `editor, spec_src, spec_text,
  doc_offset`), `merge_spec`, `stub`, `validate` (raises `Invalid(msg, line, col)`), `etag`,
  `read_first(src)`, `has_given(body)`, `summarise`, `touch`, `queue`, `exercises` (ast-based, no exec).
- Attempt lifecycle functions: `open_attempt(st, slug, meta)`, `record_pass(st, slug, meta, code)`
  (does reschedule/log/archive and returns `(grade, gap, box)` — the **caller** writes the stub;
  provide `write_region(path, new_src)` for the atomic write), `abandon(...)`, `next_hint(st, slug,
  hints)` → `(level, text)` or raises `Gated(wait_secs)`, `unlock_solution(st, slug)` → bool.
  `grade_of(attempts, secs, par, solution_shown)` unchanged; callers pass `active`.
- `run_tests(path, seed)` with `cwd=ROOT`, `timeout=60`, `-p no:cacheprovider`; returns `(ok, out)`.
- `selfcheck()` exactly as defined; CLI: `uv run study.py` → `serve` (lazy `from web import serve`),
  `uv run study.py selfcheck`. Module docstring updated.
- `test_study.py` (plain pytest functions, no fixtures), each test globbing `exercises/ex_*.py`
  where it says "all files": splice round-trip on all files; stub identity on all files (they are
  all pristine now); spec round-trip (`merge_spec(strip_spec(body).editor, spec_src)` equals body
  after normalising blank lines); merge edge cases (one-liner `def solve(x): return x` rejected;
  `def solve(\n    x,\n): return x` rejected; 2-space body ok; tab body ok; pasted docstring
  dropped; comment-first body ok; decorated solve keeps decorator); validate rejects: syntax error
  (with line), no solve, two solves, top-level `_reference`, `test_x`, `Name` `_reference` inside
  solve, empty; stub keeps given code (ex_036 `TRUTHY`, ex_044 `ConfigError`); summarise: headline
  = `E   ` lines, a `file.py:NN` inside the region maps to the editor line, a test-frame line
  does not; `grade_of`/`reschedule` pinned with 3 cases each; `queue`/`unseen` with focus ignores
  out-of-focus prereqs (build a tiny fake `exs` dict); `touch` caps a gap at 120 s.
- TDD: write the tests first (RED), then implement (GREEN). Run `uv run pytest test_study.py -q`
  and `uv run ruff check .`; both clean. `uv run study.py selfcheck` → `79/79 ok`.
- Commit: `study.py core: ast catalogue, region splice, attempt lifecycle, selfcheck`.

