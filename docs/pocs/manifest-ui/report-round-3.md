# Round 3

Removed `ManifestHelp`, its file bar, YAML outline, buttons, render site and obsolete test assertions. Removed `ManifestBrief`, its filename row, blue rule and dead CSS. Both kinds now use exactly the same `Spec · ${slug}/README.md` card and `SpecText` body. Dropped the wrapper's Run/Submit sentence without adding another wrapper; the existing shared run-result explanation and button hints remain.

Kept `ManifestWorkspace.tsx` as a one-component module. Moving its sole remaining component into the already large Task module would add churn without helping this deletion. `ManifestFailure` is byte-for-byte unchanged. Its `.aside` rule remains because the failure component still uses it; every other rule in that module was deleted. The diagnostic hover and splitter files are unchanged.

## Review findings

1. **Fixed: stale diagnostics after replacing the rejected draft.** In `web/src/useDraft.ts`, `reset()` (called after abandon by `Task.tsx`) and `takeDisk()` replaced the buffer without clearing `syntax`. The status row and editor could consequently describe an error in the previous buffer. Added `setSyntax(null)` to both paths. This omission existed in the earlier boolean lifecycle too; `54a9e12` made the stale state carry a message and line. New React server-rendered hook tests reproduce both paths without a browser. Both failed before the fix and pass afterward.

2. **Reported only, not fixed: kind-change editor readiness and retained collection.** In `web/src/Editor.tsx`, the construction effect disposes the old app but never resets `marks.current` or `ready`. On a kind change the decorations effect runs before asynchronous construction finishes and can return without an editor. The later `setReady(true)` repeats an already-true value, so it cannot reliably rerun the diagnostic, preference, read-only or keybinding effects. The old collection can retain a reference to the disposed editor until another diagnostic/value update or unmount. Installed Monaco source shows editor disposal detaches the model and removes its owned decorations, so this is not evidence that visible decorations survive disposal. Normal task navigation is protected by `<Task key={slug}>` in `App.tsx`; the finding concerns rebuilding the same mounted Editor. Left the coordinated readiness/binding lifecycle repair for a separate change, keeping the approved editor experience untouched.

3. **Reported only, not fixed: diagnostics can describe an older draft during overlapping saves.** `useDraft.save(sent)` unconditionally absorbs a 400 or clears syntax on success, without checking which buffer revision produced the response. A slow response can therefore set or clear a diagnostic after newer typing or another save. `inflight.current` records the newest promise rather than serializing all autosaves. This predates the object-state conversion and needs request-ordering work beyond the two replacement-state fixes. Run/Submit normally waits through `settle()` and then `landed()` clears syntax; an older overlapping request is the remaining caveat.

4. **Reviewed, no fix needed: diagnostic conversion, dependencies and bounds.** `54a9e12` preserves both old explicit clear sites, successful save and `landed()`, as `setSyntax(null)`. `syntaxBad` is derived directly from `syntax`; Task reads the object. Current decoration dependencies include problem, value, ready and kind. Installed `EditorApp.updateCode()` calls `setValue()` on the existing editor/model, so ordinary buffer replacement is covered by value changes. Clamping an obsolete line to the last current line avoids invalid ranges after shrinking the buffer, but is only a placement fallback, not fresh validation. No line uses the same documented fallback. Apart from finding 2, there is no current call site replacing the model independently of those inputs.

5. **Reviewed, no fix needed; historical comparison limited: plain global CSS.** `Editor.tsx` imports `Editor.css` for side effects, matching the plain `ds/styles.css` entrypoint pattern. Current selectors explicitly target Monaco and do not rely on module-local names. The production build contains the panel, row and attribution selectors and token-based shadow. Audited all 34 CSS modules and CSS imports under `web/src`: no other side-effect-only module or global-only module remains. Only `SpecText.module.css` uses `:global`, underneath its consumed local `.root`. However, the actual `bcdcb99` diff adds Editor.css and changes Editor.tsx; its parent contains no Editor.module.css, and path history has no committed version of that file. Therefore I cannot honestly certify a rule-for-rule comparison against the reported uncommitted predecessor. The current plain selectors have the intended global scope, but historical declaration/selector equivalence remains unverified. The round 2 report still names Editor.module.css and is retained as historical documentation.

## Verification

All commands ran in `/tmp/drillion-ui-poc`. No app, browser, local HTTP server or Playwright run was attempted. Node tests use Vite middleware mode with sockets disabled.

| Check | Result |
| --- | --- |
| `pnpm_config_verify_deps_before_run=false corepack pnpm --dir web build` | PASS, exit 0; 3150 modules, built in 3.81s |
| `pnpm_config_verify_deps_before_run=false corepack pnpm --dir web lint` | PASS, exit 0; `$ oxlint` |
| `node web/tests/css-modules.test.mjs` | PASS: 1, fail: 0 |
| `node web/tests/manifest-feedback.test.mjs` | PASS: 1, fail: 0 |
| `node web/tests/task-panes.test.mjs` | PASS: 1, fail: 0 |
| `node web/tests/draft-diagnostics.test.mjs` | PASS: 2, fail: 0 |
| Production CSS inspection | Hover panel, row and attribution rules present |
| Protected-component comparison | ManifestFailure unchanged; Editor and TaskPanes have no diff |

Each test file ran in its own invocation. Mutation verification: removing only reset's new clear failed only the reset case; removing only takeDisk's clear failed only the takeDisk case. Temporarily replacing parsed field paths with `/wrong` failed the adjusted manifest-feedback test. Restored all mutations before the final passing runs. No mutation touched ManifestFailure, the hover or splitter.

The default pnpm shim exited before running the scripts. Cached Corepack pnpm 11.24.0 initially attempted an automatic install and failed opening its global SQLite store. The environment override above runs the installed dependencies without modifying project configuration or adding packages. Build warnings remain for PostCSS's missing `from`, externalized `node:fs/promises` and large chunks. Visual behavior awaits the maintainer's browser pass.

Surface check: the shared web Task page is the affected entry point for both kinds. Abandon and disk-conflict acceptance are the replacement paths tested. Run/Submit buttons and keybindings use the same existing handlers. No new reverse action or connection-mode behavior was added; remote/tunnel runtime behavior was not exercised.

Build deleted the tracked `web/dist/.gitkeep`; it was restored from HEAD before the commit attempt. No changes to tasks, dependencies, Python, other branches, push or merge. The pre-existing untracked `UI-POC-BRIEF-3.md` is left unchanged and excluded from staging.

Commit status: **uncommitted**. `git add` failed with `fatal: Unable to create '/home/daniel/github/drillion/.git/worktrees/drillion-ui-poc/index.lock': Read-only file system`. Per instructions, no workaround or further Git mutation was attempted. Intended commit: `git commit --no-gpg-sign -m "fix(web): unify task specs and clear replaced draft diagnostics"`.
