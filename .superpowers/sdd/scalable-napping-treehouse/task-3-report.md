# Task 3 report — Migration to one tagged catalogue

Branch `study-ui`. Commits on top of `9a98eed`:

- `6a94fd9` Merge rsample drills into one tagged catalogue
- `3ce7507` Remove the one-off migration script

Final tree is clean and contains no `migrate.py` and no `rsample_drill/`.

## What was done

`migrate.py` (written at the repo root, run once, committed in `6a94fd9`, deleted in `3ce7507`)
asserted a clean `git status` — ignoring only its own untracked self — and then, using `study.cut`,
`strip_spec`, `stub`, `splice`, `merge_spec`, `validate`, `write_region`, `save`:

1. **Root `progress.json`** rebuilt from `rsample_drill/progress.json`:
   `focus: null`; cards `ex_009_sortkey` and `ex_022_sets` (`{box, due, seen}` only, the two with
   `seen > 0`); both log entries with the slugs remapped; `archive` for those two slugs holding
   `strip_spec(cut(copy_src).body).editor` of the rsample copy verbatim (stray `print(...)` calls
   included) with the matching log `date`/`grade`; `open["ex_016_typehints"]` =
   `{seed: 4357, attempts: 0, hints: 0, new: true, started/last: <now>, active: 0,
   solution_shown: false}`.
2. **ex_016's draft.** ex_04's five solve-body statements after the docstring, with
   `from typing import get_type_hints` prepended as the first body line, on the general file's
   `def solve(fn):` signature and docstring. No `Callable`, no module-level typing import. Written
   through `validate()` + `write_region()`, so it went past the same gate the server uses.
3. **The 10 copies.** Each copy's `# READ FIRST` block (the `#` lines after the module docstring,
   `copy of` line dropped) plus a new `#   TAKE-HOME: <text>` line from `rsample_drill/README.md`
   was inserted directly after the general file's module docstring, followed by exactly one blank
   line. No general file already had a block, so nothing had to be merged.
4. **The 8 originals** `git mv`-ed into `exercises/` as `ex_094…ex_101`, `META["topic"]` set to
   94–101, `prereqs` set to `[56] [56] [13,56] [56,95] [59] [98] [9,22,29] [94,100]`, and the
   TAKE-HOME line appended to their existing READ FIRST block.
5. `git mv exercises/ex_070_ebscleanup.py exercises/ex_072_ebscleanup.py` (topic stays 72; the
   docstring explaining the number is untouched).
6. **Tags** written into every one of the 87 `META` dicts as the last key, by AST: the insertion
   point is the end of the dict's last value, so the entry lands inline
   (`"prereqs": [], "tags": ["core"]}`) unless the closing `}` is on its own line or the line would
   pass 100 chars, in which case it goes on its own indented line. Each result is re-parsed and
   `ast.literal_eval`-ed, asserting `tags` is last and correct. Section tag from the topic number
   per the brief's ranges; library tags from the file's own top-level `Import`/`ImportFrom` roots
   (`boto3`/`moto`→`boto3`, `requests`/`responses`→`requests`, `langchain_core`→`langchain`,
   `fastapi`/`httpx`→`fastapi`, `asyncio`→`asyncio`); `rsample` on the 18. `tier` untouched.
   Distribution: core 16, files-text 9, data-structures 7, stdlib-ops 7, concurrency 7, http 6,
   errors 6, llm 6, testing 5, cloud 4, whole-task 14 (= 87); asyncio 8, langchain 5, boto3 4,
   requests 4, fastapi 1; rsample 18.
7. `git rm -r rsample_drill` plus an `rmtree` (the untracked `__pycache__` would otherwise keep the
   directory alive).
8. `pyproject.toml`: `testpaths = ["exercises", "test_study.py"]`, per-file-ignore
   `"exercises/*" = ["E402", "F841"]`, `[tool.ruff] extend-exclude = ["drafts"]`,
   `uv add --dev uvicorn` (uvicorn 0.52.4 + click; `uv.lock` committed).
   `.gitignore`: `*.tmp`, `.pytest_cache/` added; `progress.json` is **not** ignored
   (`git check-ignore progress.json` → rc 1).
9. `STUDY.md`: "Take-home track" section deleted; a "Tags" section added (section / library / track
   vocabulary + what `focus` does); `tags` added to the META bullet in "Adding exercises" and the
   region contract written out there.

## Verification

```
$ uv run study.py selfcheck
87/87 ok

$ uv run pytest --collect-only -q exercises | tail -1
88 tests collected in 0.64s

$ ls exercises/ex_*.py | wc -l
87

$ ls -d rsample_drill
ls: cannot access 'rsample_drill': No such file or directory

$ uv run pytest test_study.py -q | tail -2
........................................                                 [100%]
40 passed in 0.46s

$ uv run ruff check .
All checks passed!

$ git status --porcelain (empty = clean)
[end]
```

```
$ every META has a non-empty tags list; filename number == topic; stub identity
tags 87/87  filename==topic 87/87  stub-identity 86/87 (ex_016 holds the draft)
ex_016 body has get_type_hints: True
ex_016 module-level typing import: False
catalogue size: 87  rsample-tagged: 18

$ uv run pytest -q | tail -1  (exercise stubs are expected to fail)
86 failed, 41 passed, 1 error in 3.88s
```

The 86 failures + 1 error are the 87 exercise stubs raising `NotImplementedError`, as expected
(`ex_098_fixtures` contributes the "error" because its `@pytest.fixture`-decorated `solve` is
requested by its second test; the second test passes, which is the 41st pass alongside
test_study.py's 40).

Scheduler smoke test on the migrated state:

```
$ uv run python -c "... study.load() / study.exercises() ..."
due: ['ex_009_sortkey', 'ex_022_sets']
unseen head: ['ex_001_fstrings', 'ex_002_slicing', 'ex_004_ordefault', ...] ... 40
unseen under rsample focus: ['ex_012_decorators', 'ex_016_typehints', 'ex_029_regex',
                            'ex_055_concurrency', 'ex_059_mock', 'ex_061_whattotest']
```

`focus="rsample"` correctly offers only the six rsample drills whose rsample-tagged prereqs are
cleared (ex_013 waits on ex_012, ex_094–101 wait on ex_056) — the track still runs top-to-bottom.

## Files changed

`106 files changed, 275 insertions(+), 1593 deletions(-)` across the two commits.

- 79 `exercises/ex_*.py` — `"tags"` added to META; 10 of them also gained a READ FIRST block;
  `ex_016_typehints.py` also gained the draft body; `ex_070` → `ex_072` (rename only).
- 8 new `exercises/ex_09*_*.py` / `ex_10*_*.py` moved out of `rsample_drill/` (topic, prereqs,
  TAKE-HOME line).
- `rsample_drill/` deleted (18 drills, `_lib.py`, `README.md`, `progress.json`).
- `progress.json` (new, tracked), `pyproject.toml`, `.gitignore`, `STUDY.md`, `uv.lock`,
  `test_study.py`.

## Deviations from the brief (both forced by the brief's own verification list)

1. **`"exercises/*" = ["E402", "F841"]`** — the brief specifies `["E402"]`, but ex_016's draft (whose
   exact statements the brief pins) leaves `zone` and `returnal` unused, and this ruff's default
   rule set has F841 on, so `ruff check .` could not be clean with `["E402"]` alone. F841 is the
   same category as E402 here: the region between META and HINTS is the learner's half-written
   code. (For the record, E402 is *not* in this ruff's enabled set today, so that half of the entry
   is currently a no-op kept for the future browser-written code.)
2. **`test_study.py::test_stub_is_identity_on_pristine_files`** now skips files with an open
   attempt (`study.load()["open"]`). It sweeps every file in `exercises/`, so ex_016's draft made it
   fail; the brief simultaneously requires the draft on disk and a green `test_study.py`. Skipping
   by open attempt states the actual invariant ("a file with no open attempt is a stub") instead of
   naming ex_016.

Also added `[tool.ruff] extend-exclude = ["drafts"]`, which the task description explicitly
authorised for `drafts/flow3.py`'s pre-existing C413.

## Self-review findings

- `ast` column offsets are UTF-8 **byte** offsets, and META titles are full of em dashes. The first
  draft of the META surgery sliced strings by those offsets; fixed with a `_cut()` helper that
  slices the encoded line and decodes. Every rewritten META is re-parsed and `literal_eval`-ed as a
  check, and all 87 files still parse.
- `git rm -r rsample_drill` alone leaves the directory on disk because of untracked `__pycache__`;
  the script rmtree's it afterwards, which is why `ls -d rsample_drill` fails.
- The grafted READ FIRST blocks inherit some >100-char URL lines from the rsample files. E501 is not
  enabled here and the same lines existed before, so nothing was reflowed — rewrapping a URL line
  breaks the link.
- The 10 grafts each land as `docstring / block / one blank line / code`; the script normalises
  whatever blank lines were there rather than assuming exactly one.
- `ex_070 → ex_072` shows as `RM` (rename + modify) only because of the tags entry; content is
  otherwise byte-identical.

## Concerns

- `test_stub_is_identity_on_pristine_files` now reads the real `progress.json`. That couples a unit
  test to live state (it already read the real `exercises/`, so the coupling is not new, but it is
  now state and not just files). If Task 4/5 wants tests fully hermetic, hardcode the exception
  instead.
- `STUDY.md`'s command block at the top still advertises the deleted CLI (`study.py check/hint/
  status`) and "Current coverage" still says "8 of 87 topics". Both are out of Task 3's scope —
  flagging them for whoever owns the docs pass.
- `python-checklist.md` has no entries for topics 94–101; the new topic numbers exist only in the
  files. Nothing reads that file, but the STUDY.md instruction "topic number from
  `python-checklist.md`" is now slightly ahead of the checklist.
