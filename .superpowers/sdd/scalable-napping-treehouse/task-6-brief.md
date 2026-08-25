### Task 6: Frontend

Implement `web/index.html`, `web/app.js`, `web/style.css` per the "Frontend" section of the plan
file `/home/daniel/.claude/plans/scalable-napping-treehouse.md` (read everything above "## Tasks"
for the API contract) and the design brief at
`.superpowers/sdd/scalable-napping-treehouse/design-brief.md` (binding for colours/typography/
layout). CodeMirror import lines: use the ones recorded in the ledger under "Task 1". No build
step, no framework, no bundler; ES modules loaded by the browser. Keep `app.js` under ~450 lines;
if it grows past that, report it as a concern rather than splitting into new files.

Must-haves checklist (the reviewer checks each): hash router with the 3 views; catalogue search +
tag chips (AND) + status filter + Today panel + focus dropdown; exercise page layout per the
brief with spec `<pre>`, READ FIRST links, given-code note, CodeMirror with `indentUnit` 4 +
`Mod-Enter` + `indentWithTab`, toolbar (Run, timer with amber/red thresholds, attempts, seed,
hints with countdown, solution button states, abandon, archive), results panel (headline +
collapsible output; pass state with grade line and read-only passing code); in-order request
chain per exercise (Run cancels debounce, awaits in-flight PUT, reuses its etag); autosave 800 ms
with silent 400 + amber dot; localStorage draft mirror offered on open when newer; `beforeunload`
when dirty; 409 banner with reload/overwrite; heartbeat every 60 s while visible; textarea
fallback when the dynamic import fails; progress view with boxes, due count, per-tag table, last
30 log lines. Accessibility basics: buttons are `<button>`, focus visible, colour contrast per
the brief.

Verify by starting `uv run study.py` and exercising the UI with a real browser if one is available
to you (`explorer.exe` opens the Windows browser on this WSL box); otherwise verify with `curl`
that the static files serve and that `node --check`-equivalent syntax validity holds
(`uv run python -c "import subprocess"` is not enough — at minimum load each JS file through
`new Function` in `node` if node exists, else state clearly that browser verification is left to
the controller). Commit: `web UI: catalogue, exercise page, progress`.

