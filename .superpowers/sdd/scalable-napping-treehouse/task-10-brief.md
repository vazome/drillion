### Task 10: Content format — one folder per drill, guidance in Markdown (runs NOW, before Task 6)

Spec: `.superpowers/sdd/scalable-napping-treehouse/content-format-spec.md` — binding, read it
fully first. Implement the core change and the migration in one task, in this order:

1. **Core** (`src/study/`): `region.py` → marker-based region (`bounds/cut/splice/stub/has_given/
   validate/etag/write_region`; delete `strip_spec`, `merge_spec`, `Spec`, `doc_offset`, the
   docstring gate). `catalogue.py` → folders `exercises/<NNN>_<name>/` with `README.md` (PyYAML
   frontmatter; `topic` from the folder name; spec Markdown = body up to `## Hints`; hints = the
   `### Hint N` sections) + `drill.py` (marker present). `runner.py` → `_selfcheck.py` inside the
   folder; `summarise` keeps mapping `drill.py:NN` to editor lines (region starts at line 1, so
   the map is identity up to the marker). `api.py` → payload per the spec's "API changes"
   (`spec_md`, no `read_first`/`doc_offset`, `meta.source`, assets endpoint). `settings.py`
   unchanged. `pyproject.toml`: `pyyaml` runtime dep; pytest `pythonpath = ["exercises"]`,
   `python_files = ["drill.py", "test_*.py"]`; ruff ignores for `exercises/*/drill.py`.
2. **Tests** (`tests/`): rewrite `test_region.py` for the marker region (round-trip on all drills,
   stub identity on all drills except open attempts, validate rejections incl. "marker in edited
   text"), `test_catalogue.py` (frontmatter, headings, exactly 3 hints, topic from folder name,
   broken folder skipped), `test_api.py` (temp copy of one drill folder; spec_md present; hint
   texts are Markdown; assets endpoint 200/404 incl. traversal), scheduler/attempts/runner tests
   adjusted to the new slugs. TDD: red first for the new region and catalogue behaviour.
3. **Migration** — `migrate.py` at the root per the spec's "Migration" section; run once; verify
   the list in the spec; delete the script in the final commit. Do not hand-edit drills except
   where the converter cannot classify a docstring line (report those).
4. `README.md` (repo): update "The exercises" (layout, README.md contract, drill.py marker,
   Exercism verbatim rule) and the Layout tree. `DESIGN.md`: the spec pane renders Markdown
   (headings, lists, tables, fenced code, GitHub alerts, Mermaid, images, muted looping video),
   hints are Markdown; `read_first` is part of the Markdown.
5. Verification (paste): `uv run pytest tests -q` green, no warnings; `uv run ruff check .`;
   `uv run study selfcheck` → 104/104; `ls -d exercises/*/ | wc -l` → 104; a script that loads
   every README and asserts required frontmatter keys + headings + 3 hints; boot smoke:
   `GET /api/ex/019_counter` shows `spec_md` starting with `# ` and `GET /api/ex/019_counter/
   assets/..%2Fdrill.py` → 404; `git status` clean; `progress.json` keys renamed, values intact
   (diff shows only key renames); `exercises/016_typehints/drill.py` region == the old file's
   region minus the docstring.
Commits: `Core: marker region, Markdown guidance, folder per drill` · `Migrate drills to folders` ·
`Remove the migration script`.

