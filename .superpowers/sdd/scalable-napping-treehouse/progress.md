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
Task 10: implementer DONE_WITH_CONCERNS (904b528, a0af83d, b146bdb). Rulings: --import-mode=importlib + 059_mock
patch.object(sys.modules[__name__]) accepted; core commit red in isolation accepted; delete+add not rename accepted.
Review Approved (all 104 round-trip/stub-identity verified; progress.json values intact; 8-drill fidelity zero loss).
Minors: _selfcheck.py gitignored by controller; deferred: guidance() splits on first "## Hints" (contract says
last section), meta denylist vs allowlist, PYTHONPATH overwritten in runner, validate is a gate not a sandbox,
META["tier"] dropped (dead). Task 10: complete.
Task 11 dispatched: batch X (17 Exercism verbatim), N1/N2/N3 (native polish, 29 each). Prompts /tmp/task11-*.md.
Task 11 status (session limit hit again, resets 21:10 Madrid): N1 ✓ af800dd · N2 ✓ 568eca6 · X ✓ 81a5881 + d684d4c
(controller folded hints.md verbatim as "## Exercism hints" before Read first; mechanical check: every
introduction/instructions line present in order for 17/17; `~~~~exercism/note` → [!NOTE] callouts, <br> dropped) ·
N3 part 1 ✓ (20 files, agent died; parse-checked) — REMAINING N3: 093_message_dig 094_await_under_lock 095_semaphore
096_async_cm 097_lazy_init_lock 098_fixtures 099_asgi_test 100_rerank 101_explain_takehome (special case: ### Q1 headings).
Still to do for Task 11: dispatch N3 remainder (9 files); one sampling reviewer over N1–N3 (native polish) and an
accuracy check of You get/You return/split coverage for 206/207/212/213 (X reviewer died before that step).
Model policy (Daniel, 2026-08-25): controller picks sonnet/opus per task, never fable. N3b → sonnet; native/X reviewer → opus.
N3b ✓ d8760f1 (sonnet). Task 11 authoring complete; content reviewer (opus) pending. Phase B batch B (opus) running; batch F dispatched (opus).
Task 11: content review Approved (95 native+X checked: Why unchanged 95/95, frontmatter identical 95/95, 130 fenced
solve() calls match signatures, 17 Exercism splits/signatures correct, hints.md verbatim 7/7). Minors applied by
controller: 059 fence → text, 043 WARNING → TIP, 203/213 bool wording. Deferred: adjacent TIP callouts (078/083/085),
084 table duplicates fence comments. Task 11: complete.
Batch F ✓ committed; ruling: multi-practice section tag = first listed practice (consistent with batch E).
Batch C ✓ committed (pretty-leaflet is Exercism 'wip': instructions say class, tests say functions — followed tests, README flags it).
Batch B: review Approved; minor fixed (chaitanas ### General). Deferred: 218 Hint 2 names all four methods; 228 _HIGHEST narrow.
Batch F: review Needs fixes → fixed by controller (### inside fences → #, 319 Hint 2 rewritten). Deferred: canonical counts >6 (more coverage), 318 Hint 2 borderline, 319 [3,0] canonical case order. Batch F: complete. Batch G dispatched (opus).
Batch C: review Approved; Important fixed (230 contradiction stated), 236 rule softened. Deferred: canonical counts <3 in 234/239/240/243 (copy more variations later), 230 format_date generated count, 243 overlap rule untested. Batch H dispatched (opus).
Batch G ✓ committed; ruling: 329 scrabble-score section tag core (map override); keep Exercism's (_[concept:...]()_) fragments (precedent 209).

## RESUME POINT 2026-08-26 (session limit hit again on batch H + batch G review)
State found on resume: HEAD 66572d8 on `main`. 159 drills pass `uv run study selfcheck`, ruff clean.
Untracked in the working tree: batch D (10 folders, 245–259) and batch H PARTIAL (330–337; 338_clock
and 339_high_scores never written, no phaseb-H-report.md). phaseb-D-report.md and phaseb-G-report.md
on disk, untracked. Batch G is COMMITTED (6e59f33) but its review never ran.
Outstanding when resumed: (1) batch H remainder + audit of the inherited 8, (2) batch G review,
(3) batch D review + commit. Batch I (340–349) is the only batch never started.
Reviewer prompt files written this session: /tmp/phaseb-review-common.md (binding reviewer contract,
carries the standing rulings so reviewers stop re-raising them), /tmp/phaseb-review-{D,G}.md,
/tmp/phaseb-H2.md (batch H remainder + audit-the-inherited-8).
Dispatched 3 concurrent (opus, per model policy — never fable): batch H remainder, batch G review,
batch D review.
Batch G: review Needs fixes → 1 Important (325 secret-handshake Rules table gave the 4th-from-right
char of "10011" as `1`, contradicting its own `solve("10011") # -> ["double blink", "wink"]` example
and the canonical case) → fixed by controller, commit ee804ac. Reviewer independently re-ran ruff /
stub / reference(seeds 1,2,42) / selfcheck, scripted a verbatim diff (0 differing lines across all 20
Introduction+Instructions sections), and added a NEW check worth keeping: execute every
`expr # -> value` example in our own sections against `_reference` (53 examples, 0 mismatches) — the
325 error survived only because it lived in a prose table, not a fence. Concerns closed: 326 float
rounding (1.6M cases, three association orders never diverge), 323 `//` vs exemplar `/` (README pins
it). Report table's stale `files-text` for 329 left as-written with a controller note (the pasted
catalogue output is evidence of what was run; the file itself carries the settled `core`).
Batch G: complete.
Batch D: review Needs fixes → 1 Important + 5 minors, all resolved; commit 110388a. All three of the
implementer's concerns ruled in its favour (247 categorize_dish signature trade; 251 and 257 exemplar
bugs are real — instructions implemented, and 257 deliberately does not port one canonical test
expectation). Important: Hint 2 gave the literal solution in 249/258/259 (249's was a fence holding
the whole of its only function, in the drill's own parameter name, leaving nothing for Hint 3) and
more mildly in 247/251/254 — all six rewritten by the controller to name the routing/operator/builtin
without the working expression. Minors fixed: two enum anchors → howto/enum.html (verified 200 + id
present), 245's towardsdatascience link 404 → dropped, 254 now states WARNING must be declared before
the WARN alias (the get_members assertion is messageless, so the failure was cryptic).
NEW STANDING RULING (m-3, for later batches): when an upstream Exercism heading level is itself
anomalous (cater-waiter introduction.md:342 is `# Set Symmetric Difference` among `##` siblings),
demote it to the level its SIBLINGS land on, not by the fixed one level — one level would produce a
top-level `##` section and break the section contract.
Known ceiling (m-4, accepted): runs of two blank lines in Exercism sources render as one in our
READMEs (41 places in batch D). Rendering-neutral in GFM; "line for line" is the stated bar and this
is the only systematic departure. Trailing whitespace inside fences IS preserved.
Batch D: complete.
Batch H: authored (338_clock + 339_high_scores written; inherited 330–337 audited, nothing changed).
Reviewer dispatched (opus) with a provenance warning — the eight inherited drills were written by a
killed agent that never self-verified, so "it all passed as written" is a claim to check, not a given.
Controller measured concern (b) for the reviewer: 335_nth_prime asserts solve(10001); naive trial
division reaches 104743 in 26.9 s but src/study/runner.py:30 caps a run at --timeout=10, so a CORRECT
but naive solution gets an opaque timeout kill. _gen caps at 1500 and the small canonical cases run
first, so a WRONG solution still fails fast — the defect is scoped to correct-but-slow. Controller's
leaning: keep the case, add a Rules WARNING naming the √n requirement. Concern (c) already closed by
the controller: 336_sieve's primes literal is at drill.py:57, below the marker at drill.py:5.
NEW CHECK worth keeping (from the batch G review): execute every `expr # -> value` example in our own
sections against _reference, AND read prose tables that state per-character/per-position facts —
batch G's only defect was a wrong character in a prose table that passed every scripted check.
Batch H: review Needs fixes → 2 Important + the 335 ruling, all applied; commit b68c629.
Provenance verdict: the second implementer's "changed nothing, all passed" HELD UP — reviewer
independently re-derived all 10 frontmatters from config.json, re-ran a fence-aware fidelity diff
(0 changed lines), ran all 183 upstream canonical tests against the ten _references, executed 72
README examples plus every hint block (0 mismatches), and re-measured _gen variety.
I-1 (330 pig-latin): the Rules WARNING said a rule-2-before-rule-3 mistake turns `square` into
`quaresay`; it actually yields `uaresqay` (`quaresay` is a DIFFERENT bug — moving only the first
consonant). Script-invisible, caught by reading — the second prose-table/prose-claim defect in two
batches. The new "read the prose claims" check is earning its place; keep it in every review prompt.
I-2 (338 clock): the non-mutation assert sat AFTER the subtraction check, so a mutating `+` failed on
the `-` line and was blamed on subtraction while the explanatory message never ran. Fixed by checking
each operator immediately after it runs. Controller verified empirically with a correct-arithmetic
mutating Clock: before → "Clock(25, 2117) - 868"; after → "+ must not change Clock(25, 2117) itself".
335 nth-prime: reviewer ruled option (b) — keep Exercism's canonical solve(10001), announce the wall.
Reviewer measured naive at 32.6 s (controller measured 26.9 s) against --timeout=10 with
pytest-timeout 2.4.0 installed, so the kill is hard and opaque. Decisive argument was internal
consistency: 334_prime_factors/README.md:86 already does exactly this for the same failure mode —
two sibling drills, same trap, one warned and one not. Added as a second paragraph inside the
existing callout rather than a second adjacent callout (adjacent-callout style was a deferred minor).
336 sieve: concern closed — primes-below-1000 literal exists only in drill.py:44–57, below the
marker at line 5; grep confirms it appears in no README or hint.
Batch H: complete. Catalogue now 161 drills, selfcheck 161/161, ruff clean.

## Phase B status after 2026-08-26 session
Complete: A, B, C, D, E, F, G, H (+ Task 11 native/X content). NOT STARTED: batch I (340–349) — the
only remaining batch. Prompt at /tmp/phaseb-I.md; dispatch with /tmp/phaseb-common.md, then review
with /tmp/phaseb-review-common.md + a per-batch file like /tmp/phaseb-review-{D,G,H}.md.
Reviewer prompt improvements to carry into batch I's review: (1) execute every `expr # -> value`
example in our own sections against _reference; (2) READ prose tables and prose claims that state
per-character/per-position facts — both Important findings in G and H were of that class and passed
every scripted check; (3) if a batch was written by more than one agent, tell the reviewer which
files are inherited and unverified.

## Phase B COMPLETE 2026-08-26
Batch I (340–349) authored and committed as c7b453e. Catalogue 171 drills, selfcheck 171/171,
ruff clean, tests 40 passed. **All Phase B batches A–I are done. Phase B is finished.**

Batch I ran as 2 implementers (opus, 5 drills each) → 2 reviewers (opus, cross-assigned) → 1 fix
agent. Both reviewers ruled Needs fixes, one Important each, and both Importants were prose no test
could catch: 341's Hint 3 was `allergic_to`/`lst` with the nouns renamed; 349's Rules claimed
`values.index(target)` "passes every test" when `list.index` raises ValueError with Python's own
wording. That is four batches running (C, G, H, I). The three reviewer-contract additions recorded
after H did their job — keep them for any future content batch.

Two brief errors the implementers caught and diverged from, independently of each other, before
the controller's correction arrived:
- The attribution line is NOT the last line of the file. `guidance()` partitions at `\n## Hints\n`,
  so a line below the hints is swallowed into Hint 3 and never renders. It goes after
  `## Read first`, before `## Hints`. content-format-spec.md said "a last line" and has been fixed.
- Exercism drills carry NO `practices:` frontmatter key. That field holds int topic numbers for
  native drills (`069_s3audit` → `[30, 43, 68]`); all 33 pre-existing Exercism drills omit it.
  Open question, deliberately not settled inside a batch: whether 300–349 should carry it at all.
  If ever yes, it is a type decision across all 50, not a per-batch fix.

Controller decision during the batch: dropped the `with-statement` tag from 344_grep. It was the
slug's only config practice, but the drill has no `with` and no `open()` because the controller
told the implementer not to touch the filesystem. A tag promising a concept the drill does not
practise is worse than deviating from "copy config.json verbatim".

Prompts live in this session's scratchpad, not /tmp: phaseb-common.md, phaseb-I{1,2}.md,
phaseb-review-common.md, phaseb-review-I{1,2}.md. Copy them forward if another content batch runs.

## Task 6 (frontend) 2026-08-26 — built from the Claude Design system
Design input: Claude Design project `drillion design system`
(e20cf404-9878-452c-9bf7-b013f4cdd8da, "Mineral Blue"). Pulled to `web/src/ds/`: 5 token CSS files,
17 components (`.jsx`, verbatim) and their prop contracts (assembled into `src/ds/index.d.ts` from
the project's per-component `.d.ts`). NOT synced back — that project was authored in Claude Design,
has no `_ds_sync.json` anchor, and `/design-sync` would overwrite hand-made work.

STACK DEVIATION from the plan, under Daniel's "hard rule: use ponytail". The plan mandated
Tailwind v4 + shadcn/ui + TanStack Query + react-router; all four were dropped:
- the 17 design components use zero Tailwind classes (inline styles over CSS variables), so
  Tailwind's only job would have been layout glue the design's own screens also do inline;
- shadcn would be a second component library re-themed to match tokens already implemented —
  the design's primitives are already accessible (native `<select>`, `role="switch"`,
  `aria-expanded`, Enter/Space rows, `:focus-visible` rings);
- 3 screens / 6 endpoints and no cache-invalidation web; the exercise page's in-order request
  chain is hand-written either way, which is what TanStack Query would not have solved;
- hash routing for 3 routes is 12 lines (`App.tsx: useHash`).
Kept/added: `@uiw/react-codemirror` + `@codemirror/lang-python` + `@uiw/codemirror-themes`
(the editor, themed from the tokens), `react-markdown` + `remark-gfm` +
`remark-github-blockquote-alert`. Net: 4 mandated deps out, 3 in. Reviewer should check against
this entry, not the plan's stack line. Say so if you want the mandated stack instead — it is a
rewrite of the styling layer, not of the screens.

SpecText replaced. The design shipped a hand-rolled regex Markdown parser; measured against the
real corpus it mis-renders 143/171 READMEs (plain blockquotes), 113 (`_emphasis_`), 17 (ordered
lists), 16 (h4+), 5 (nested lists). Same visual decisions, `react-markdown` underneath. Its
Mermaid CDN loader and `assets/` video path were dropped: 0 of 171 drills use either, and a CDN
in a local-first app is a bug (noted in the file).

Two backend changes inside Task 6's scope:
- `api.py` mounts `StaticFiles(..., check_dir=False)` unconditionally. This closes the Task 9
  deferred minor ("static mount decided at import") and is what lets `serve()` build `web/dist`
  after the module is imported.
- `serve()` calls new `build_web()`: builds `web/dist` when missing or older than `web/src`,
  via pnpm; warns and carries on if pnpm is absent (API still serves, `/` 404s). In the container
  no `web/package.json` is copied, so it returns early and leaves the baked dist alone.
Dockerfile: `node:24-slim AS web` stage added, `COPY --from=web /build/dist ./web/dist`.

Off-by-one found by driving the real API, not by reading: `card["box"]` is a 0-based index into
LADDER (0-4), while `LadderMeter` fills `box` cells 1-5. Catalogue rows now pass
`ex.seen ? ex.box + 1 : 0` and the grade line reads `box ${result.box + 1} of 5`.

`web/pnpm-workspace.yaml` is load-bearing on this machine: `/home/daniel/pnpm-workspace.yaml`
makes $HOME one workspace, and without a local one `pnpm install` in `web/` silently installs
the home package instead (exit 0, no node_modules).

Verified: `pnpm build` clean (tsc + vite); `uv run drillion` serves `/` 200 with the Vite
index.html and `/assets/*.{js,css}` 200; unmatched `/api/*` still 404s as JSON; deleting
`web/dist` and starting the server rebuilds and serves it; `tests/` 40 passed; `selfcheck`
171/171; `ruff check .` clean. The whole attempt flow was driven over HTTP against a scratch
root (never Daniel's progress.json): payload keys, PUT-before-open 409, stale-etag 409 with
`{error,etag,code}`, syntax 400 with `{error,line,col}`, failing run, passing run
(grade/box/due_in/code, file back to stub, archive + log written), hint 200, solution 423 with
`need_attempts`/`need_secs`, touch.
New check `web/check.mjs` (`pnpm --dir web check <port>`): renders all 171 specs through SpecText
and asserts no literal `[!NOTE]`-class marker, `## ` heading count == `<h2>` count, lists stay
lists. 171/171 pass; verified it FAILS when `remarkAlert` is removed.
NOT verified: a real browser. Left to Task 7 per AGENTS.md.
Not committed — Daniel asked for the build, not a commit.
