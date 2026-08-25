# SDD ledger — plan: /home/daniel/.claude/plans/scalable-napping-treehouse.md
Branch: study-ui (in the main working tree; Ruling: no separate worktree — Daniel's editor and
runner live in ~/study and the migration renames the files he works in; merge to master at the
end — costs nothing if wrong beyond a branch switch).
BASE for Task 2: 67d64f5 (checkpoint commit on main, branched to study-ui).
Spec: none separate; the plan's design sections (above "## Tasks") are the authority.

## Pre-flight scan (2026-08-25)
| pair / task | produces vs consumes | finding |
|---|---|---|
| T2 core ↔ T3 migration | T3 imports `cut/strip_spec/stub/splice/bounds` from study.py; T3 writes the progress.json shape T2 defines | consistent; T2 must tolerate META without `tags` pre-migration — Ruling: `tags = META.get("tags", [])` (in plan) |
| T2 core ↔ T4 web | T4 calls the lifecycle functions by the names T2's brief fixes (`open_attempt/record_pass/abandon/next_hint/unlock_solution/validate/write_region/etag/summarise/run_tests/queue/exercises`) | names fixed in T2 brief; T4 brief says "use study's functions" |
| T3 migration ↔ T4 web | T4 tests copy `ex_001` (unchanged by T3 except tags) | consistent |
| T4 web ↔ T6 frontend | API table is the shared contract; T6 consumes it verbatim | consistent |
| T5 design ↔ T6 frontend | design-brief.md path fixed in both | consistent |
| T1 spike ↔ T6 | import lines recorded in this ledger under "Task 1" | consistent |
| T2 self | tests over `exercises/` = 79 files pre-migration, all pristine → stub identity holds for all | consistent |
| T3 self | "all files stub-identical except ex_016" vs archiving ex_009/ex_022 bodies and leaving them stubs | consistent |
| T3 self | migrate.py deleted after run → no permanent test of the migration | Ruling: acceptable for a one-off; the verification list + selfcheck are the test — costs a re-run from the checkpoint commit if wrong |
| T4 self | brief's smoke-test narrative has one self-correction (stub run → not 400) | reads as intended: stub parses, run returns passed=False |
| Global ↔ rubric | reviewers may flag `# ponytail:` shortcuts as defects | Ruling: a ponytail comment marks a deliberate ceiling; reviewers judge whether the ceiling is acceptable, not the comment |
| Model selection | skill says cheapest model per task; Daniel's standing instruction says Opus 5 for all subagents | Ruling: Daniel's instruction wins — all implementers/reviewers on `opus`; final review also `opus` (Fable subagent was allowed "only this single time" for the plan review); Fable (this session) is the gate |


## Task 1: complete (spike, nothing committed)
Working esm.sh imports (verified in the t3 preview browser, one shared @codemirror/state instance):
  import("https://esm.sh/codemirror@6.0.2")           → { basicSetup }      # bare "codemirror@6" resolves to 6.65.7 with only a default export — DO NOT use it
  import("https://esm.sh/@codemirror/view@6")         → { EditorView, keymap }
  import("https://esm.sh/@codemirror/state@6")        → { EditorState }
  import("https://esm.sh/@codemirror/lang-python@6")  → { python }
  import("https://esm.sh/@codemirror/language@6")     → { indentUnit, HighlightStyle, syntaxHighlighting }
  import("https://esm.sh/@codemirror/commands@6")     → { indentWithTab }
Construct: EditorState.create({doc, extensions:[basicSetup, python(), indentUnit.of("    "), keymap.of([indentWithTab, {key:"Mod-Enter", run}])]}); new EditorView({state, parent}).
Note for E2E: the preview browser reaches WSL via its LAN IP (172.31.x.x), not 127.0.0.1 — Task 7 needs the app bound to 0.0.0.0 for the test session only (env override), never by default.

## Task 5: complete (design brief, controller-run with frontend-design skill; nothing committed)
Brief: .superpowers/sdd/scalable-napping-treehouse/design-brief.md — "index cards on a desk": cool
mineral-grey desk + white cards, Bahnschrift labels / Segoe UI body / Cascadia Mono code, one plum
accent #5A3E9C, muted pass/fail/warn, signature = the Leitner ladder meter. Light editor theme
specified. Ruling: light UI (not soft-dark) — avoids the near-black+accent default and any
"terminal" reading; costs a theme swap if Daniel prefers dark.

## Task 2: implementer DONE_WITH_CONCERNS (commit 9a98eed; 40 tests, selfcheck 79/79)
Rulings on its deviations (accepted, carried into Task 4's dispatch):
- `open_attempt(st, slug)` takes no `meta` — fine; the attempt doesn't need it.
- `region_start` = first line of the region body (not META end + 1) so summarise's remap is exact.
- `summarise(out, region_start, doc_offset, hints_line)` derives doc_end itself (no 5th arg).
- `abandon(st, slug, disk_src)` returns the stubbed source; web.py does the etag check + write.
- 522 lines (prose-heavy) accepted; no cut. `pick()` unused → deferred minor: delete after Task 4 if still unused.
- ruff: 5 pre-existing errors only in drafts/ and rsample_drill/ (Task 3 removes the folder; drafts/ is Daniel's scratch — leave).
Task 2: review clean (Approved, spec ✅). Deferred minors (for the final review to triage):
- queue()/due_today/unseen materialise zero-cards via card() setdefault → GET handlers must never save() (carried to Task 4 dispatch).
- summarise remaps any *.py:NN in the region range regardless of file (library frames could get a bogus "line N") — known ceiling; needs filename arg to tighten.
- run_tests has no unit test; TimeoutExpired branch discards partial stdout.
- exercises() "skips broken files" branch untested; catalogue parses each file 5× (172 ms/79 files) — fine for localhost.
- Gated(0) = hints exhausted vs Gated(n>0) = wait (carried to Task 4); record_pass/next_hint/unlock_solution KeyError without an open attempt → web.py must 4xx (carried to Task 4).
- validate's top-level ban misses AnnAssign/import forms (the _reference Name walk covers what matters); "could not put the spec back" message blames machinery for learner trailing content.
- stub keeps the learner's indentation for the docstring after a non-4-space save (git noise, cosmetic); helpers above solve survive a reset (name in README.md, Task 8).
Task 2: complete (commits 67d64f5..9a98eed, review clean)
BASE for Task 3: 9a98eed

## Task 3: implementer DONE_WITH_CONCERNS (commits 6a94fd9, 3ce7507; selfcheck 87/87, 88 tests, ruff clean)
Rulings: F841 added to the exercises/* ruff ignore (learner code legitimately has unused names; ruff is
not the grader) — accepted. test_stub_is_identity skips slugs with an open attempt (reads progress.json)
— accepted: that IS the invariant (files without an attempt are stubs). `[tool.ruff] extend-exclude =
["drafts"]` accepted. Noted for Task 8: README.md command block still lists deleted CLI commands;
python-checklist.md lacks 94–101 (Daniel's checklist — leave).

## Phase B (Exercism) started 2026-08-25 — worktree /home/daniel/study-exercism, branch exercism-drills from 3ce7507
Plan: .superpowers/sdd/scalable-napping-treehouse/phase-b-exercism.md. Batches A–I; agents write files only
(no git); controller commits per wave and runs the global selfcheck. Wave 1 = A (concept 200–214),
B (concept 215–229), E (practice 300–309), F (practice 310–319).

## RESUME POINT (written 2026-08-25 before context compaction; session limit killed all agents)
State of the world:
- Branch `study-ui` in /home/daniel/study, HEAD 3ce7507, tree clean. Commits: 67d64f5 checkpoint → 9a98eed Task 2 (core) → 6a94fd9 + 3ce7507 Task 3 (migration).
- Task 1 (spike): complete — CodeMirror import lines recorded above under "Task 1".
- Task 2: complete, review clean (see above).
- Task 3: implementer DONE_WITH_CONCERNS, rulings recorded above; **task review NOT done** — the reviewer
  agent was killed mid-review (it had verified user-work migration for ex_01/02/04 and was checking uv.lock).
  NEXT: re-dispatch the Task 3 reviewer (opus) with brief task-3-brief.md, report task-3-report.md,
  diff review-9a98eed..3ce7507.diff (already generated), BASE 9a98eed HEAD 3ce7507.
- Task 4 (web.py): NOT started. Brief extracted at task-4-brief.md. Dispatch after Task 3 review clears.
  Carry into its dispatch: Task 2 rulings (open_attempt(st, slug); region_start = first body line;
  summarise(out, region_start, doc_offset, hints_line); abandon(st, slug, disk_src) returns stubbed src),
  Task 2 deferred minors (GET handlers never save() — queue() materialises zero-cards; Gated(0) = hints
  exhausted; record_pass/next_hint/unlock_solution KeyError without an open attempt → 4xx).
- Task 5 (design brief): complete — design-brief.md.
- Task 6 (frontend), 7 (E2E), 8 (docs + final review): NOT started.
- Phase B (Exercism): worktree /home/daniel/study-exercism on branch `exercism-drills` from 3ce7507.
  Wave 1 agents (batches A, B, E, F) were ALL killed early. Partial files left: exercises/ex_200_lasagna.py
  (batch A) and exercises/ex_300_two_fer.py (batch E) — unverified; delete them before re-dispatch.
  No phaseb-*-report.md files exist. NEXT: re-dispatch batches A, B, E, F (prompts: contract file
  phase-b-exercism.md + per-batch assignment tables in this ledger's Phase B section / the original
  dispatches — batch A = concept k 0–4 → topics 200–214; B = k 5–9 → 215–229; E = practice 300–309
  (two-fer, leap, raindrops, bob, reverse-string, isogram, pangram, anagram, hamming, rna-transcription);
  F = 310–319 (word-count, acronym, run-length-encoding, roman-numerals, luhn, isbn-verifier,
  phone-number, matching-brackets, series, sum-of-multiples)). Remaining batches C (k 10–14 → 230–244),
  D (k 15–19 → 245–259), G (320–329), H (330–339), I (340–349) per phase-b-exercism.md.
  Agents write files only (no git); controller commits per wave and runs `uv run study.py selfcheck`.
- Run at most ~3 agents concurrently from now on (5 in parallel hit the session limit).
- Spike static server on :8799 and the Exercism clone at /tmp/exercism-python may need re-creating
  after a reboot (clone: `git clone --depth 1 https://github.com/exercism/python /tmp/exercism-python`).

### Artifacts on disk (complete, single-version — git holds the code versions)
task-2-brief.md, task-2-report.md (168 lines, full TDD evidence), review-67d64f5..9a98eed.diff;
task-3-brief.md, task-3-report.md (169 lines, full verification output), review-9a98eed..3ce7507.diff;
task-4-brief.md; design-brief.md; phase-b-exercism.md; spike/index.html (working CodeMirror page).
Killed agents wrote NO reports; only the two partial drill files in the worktree.

### Killed agent IDs (try SendMessage to resume with context intact before re-dispatching fresh):
- Task 3 reviewer: a39006e85d42f297e — had read brief/report/diff and finished the user-work checks
- Exercism batch A: ac5fc46c8435b69f4 — had read sources, started writing ex_200_lasagna.py
- Exercism batch B: a510b1c8e82f7c728 — only started reading
- Exercism batch E: a3ad8e9d32e7f356e — had read all 10 sources, started writing ex_300_two_fer.py
- Exercism batch F: a34a2678abb049240 — only started reading
If a resume fails (agent gone), dispatch fresh with the same prompts; delete the partial files first.

## Resumed 2026-08-25 after compaction
Killed agents were unreachable (ListAgents empty) → fresh dispatches. Deleted partial ex_200/ex_300 in worktree.
Phase B prompt files: /tmp/phaseb-common.md (contract + concept→topic map), /tmp/phaseb-<BATCH>.md (assignment).
Wave 1' (3 concurrent): Task 3 reviewer (opus) + batch A + batch E. Next: batch B, F, then C, D, G, H, I; Task 4 after Task 3 clears.
Task 3: review Approved (spec ✅ all 8 steps; archive byte-faithful; tags 87/87 by AST). Rulings on minors:
F841 ignore ratified (ceiling: unused locals in machinery go unlinted); drafts/ exclude kept (Daniel's scratch);
ex_098 docstring ex_11→ex_096 fixed by controller (commit after 3ce7507); test_stub_is_identity reading
progress.json accepted; README.md command block + "8 of 87" line → Task 8.
Task 3: complete. BASE for Task 4 = HEAD after the ex_098 fix.
Phase B batch E: DONE_WITH_CONCERNS → read_first() skipped # SOURCE: line — fixed on study-ui (3e85082; unit
test to add after Task 4 lands, test_study.py is being edited by the Task 4 agent). Rulings: `solve(name="you")`
default in signature OK (selfcheck rebuilds the call from the signature); multi-practice section tag = first
listed practice; TODO links.json placeholders replaced by docs.python.org links OK. Committed in worktree.
Phase B batch A: DONE_WITH_CONCERNS (same read_first issue, fixed). 7 files (200,203,206,207,209,212,213).
Rulings: ex_200 returns EXPECTED_BAKE_TIME constant in the dict OK; docstring task dropped OK; ex_209/206 follow
instructions over buggy exemplar OK; given value_of_card in ex_213 OK. Committed in worktree. Reviewer dispatched.
Phase B batch E: review Needs fixes (1 Important: ex_309 hint 2 leaked maketrans table) → fixed by controller
(+ hamming match regex escaped, two-fer assert message). Deferred minors: two-fer _gen never hits default path;
pangram module-level ascii_lowercase import; anagram exact-order assert (docstring states it) — accepted.
Ruling for all batches: hand-picked docs.python.org anchors instead of links.json entries are fine if they resolve.
Batch E: complete.

## Task 4: implementer DONE_WITH_CONCERNS (commit 89f4d57 on top of 3e85082; 42 tests in test_study.py, selfcheck 87/87)
Rulings: PUT does not touch the timer (heartbeat every 60 s < 120 s cap keeps `active` exact) — accepted;
no open attempt → 409 {error} without `etag` (etag-409 carries `etag`) — accepted, Task 6 must branch on it;
global lock held for the whole pytest subprocess, all handlers sync def — accepted ceiling (single user);
abandon tolerates a missing attempt (= reset to stub) OK; touch on unknown slug → 409 not 404 — minor, accepted.
Whole-suite `uv run pytest -q` is red by design (exercise stubs); only test_study.py is the green gate.
Phase B batch A: review Approved (1 Important: lowercase constants in ex_200 _reference → fixed by controller;
+ ex_206 third canonical row, comment attribution). Deferred minors: ex_207 spec lacks "int type" clause;
ex_212 generated cases score card_one only; hint-3 structural transcriptions accepted (within contract).
Batch A: complete.
Task 4: review Approved (spec ✅ all endpoints). Important (PUT without attempt un-stubs a closed file) → fixed by
controller (+ test). Deferred minors: chunked-body 413 ceiling (ponytail'd); gated hint/solution 423 raise before
save (touch lost, harmless under heartbeat); catalogue indexes m["minutes"] directly; RequestValidationError
uses FastAPI's {detail} shape (Task 6 must tolerate both); explorer.exe Popen never reaped.
Task 4: complete. BASE for Task 6 = HEAD.

## 2026-08-25 direction change (Daniel): modern rich framework + light/dark + research-first
Plan file updated: Research section; Frontend = React 19 + Vite + TS + Tailwind v4 + shadcn/ui,
@uiw/react-codemirror, TanStack Query, react-router hash; build-if-stale in serve(); web.py mounts web/dist.
Task 6 rewritten. Task 1 esm.sh import lines superseded. Daniel will run `/design` himself — WAIT for its
output before dispatching Task 6; record its path here under "Task 6 design input".
Phase B batches B and F were stopped by Daniel mid-write. Batch B left UNVERIFIED partial files in the worktree: ex_215, ex_218, ex_221 (delete before re-dispatch); batch F left nothing. Re-dispatch when he says go.
stack-notes.md written (Context7-verified Tailwind v4 / shadcn Vite / react-codemirror setup); referenced from plan Task 6.

## 2026-08-25 Daniel: reshape to production-grade backend NOW (Task 9), UI later, Phase B paused
Plan: Task 9 = src/study package (cli/settings/state/catalogue/region/scheduler/attempts/runner/api),
console script `study`, runtime deps in [project.dependencies], tests/ split, /api/health, stdlib logging,
Dockerfile + compose + .dockerignore (Docker NOT installed here → unverified), CI workflow. BASE 3c06497.
Correction: Docker IS installed (daemon just not started). Docker optional for now; controller runs `docker compose build` as a smoke test once Daniel starts it.
Task 9: implementer DONE_WITH_CONCERNS (dfebde2, 67a89a0; 43 tests, selfcheck 87/87). Rulings: compose single-file
bind mount → controller switched to `./:/data`; web_dist = repo-root web/dist (correct reading); `/` 404 until
Task 6 accepted. Docker build + CI unverified here (daemon off).
Task 9: review Approved (AST-verified move, 42→42 tests + health). Minors fixed by controller: dead region.has_given,
CI `uv sync --frozen`. Deferred: static mount decided at import (Task 6 note), STUDY_PORT non-int traceback,
serve() prints 0.0.0.0 URL in container. Task 9: complete.
Repo housekeeping (Daniel): plan now lives at .superpowers/sdd/scalable-napping-treehouse/plan.md (old
~/.claude/plans path is a symlink); .superpowers tracked; drafts/, README.md, platform-checklist.md,
python-checklist.{md,html}, ruff_plan.md, ruff_report.txt, unrelated-devops-1.html purged from ALL history
(git-filter-repo, backup bundle in /tmp), gitignored, kept locally; all branches force-pushed to origin.
NOTE for Task 8: README.md is local-only now → user docs go to README.md.
README.md is the single user doc (STUDY.md deleted per Daniel; review-*.diff gitignored).
README rewritten as a project README (Task 8 docs pulled forward; re-check after Task 6 lands: frontend dev loop, screenshots).
DESIGN.md is the design handoff (screens, data, states, constraints); design-brief.md marked superseded; spike/ and web/index.html removed (web/README.md keeps web/ non-empty for the Dockerfile COPY).

## 2026-08-25 Daniel: content format change (folder per drill, README.md guidance in GFM)
Spec: content-format-spec.md. Plan: Task 10 (core + migration), Task 11 (Exercism verbatim + native polish).
exercism-drills merged into main (ff9220a, 104 drills, selfcheck 104/104); worktree and branch deleted;
batch-B partial files discarded. Phase B continues on main in the folder format after Task 10.
