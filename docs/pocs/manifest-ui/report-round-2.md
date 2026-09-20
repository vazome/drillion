# UI proof of concept: Round 2

Work stayed on `poc/manifest-ui` in `/tmp/drillion-ui-poc`. Both briefs were read directly before implementation. No dependencies were added or installed successfully, no Python files were changed, and nothing was written into `tasks/`.

## 1. Centre splitter

Replaced native `resize: horizontal` with `TaskPanes`, a two-pane layout with a full-height 10px hit target, a 1px seam, and token-based hover, focus and drag highlights. Pointer capture keeps a drag attached when the pointer leaves the target; pointer-up, cancellation and lost capture end the interaction. Moving into the narrow layout clears an interrupted drag.

The separator is named, focusable, vertical, and exposes its controlled pane and live ARIA minimum, maximum and current values. Left/right arrows move by two percentage points; Home/End select the allowed extremes. The brief keeps its 340px minimum and 70% ceiling. The upper limit also preserves room for the existing 420px editor and 20px seam, avoiding horizontal overflow. The existing 999px narrow-screen breakpoint still stacks the panes and removes the separator.

Position is saved through `prefs.ts` after a drag or keyboard adjustment, with the previous 42% default. Window resizing clamps the displayed position without overwriting the saved preference. No Settings control was added.

Research:

- [VS Code sash source](https://github.com/microsoft/vscode/blob/main/src/vs/base/browser/ui/sash/sash.ts) and its CSS: inspected the installed VS Code implementation in `web/node_modules/.pnpm/@codingame+monaco-vscode-api@36.2.2/node_modules/@codingame/monaco-vscode-api/vscode/src/vs/base/browser/ui/sash/`. Borrowed the separate hit target/visual seam and hover/active treatment. That installed implementation uses mouse and gesture event factories; this POC uses the pointer capture required by the brief.
- [react-resizable-panels separator](https://github.com/bvaughn/react-resizable-panels/blob/main/_autodocs/api-reference/separator.md), configuration and accessibility documentation via Context7: borrowed named separator semantics, keyboard sizing, generous hit targets and persistence after user interaction. Nothing was installed.
- [ARIA window splitter pattern](https://www.w3.org/WAI/ARIA/apg/patterns/windowsplitter/), retrieved via Context7: used separator range properties, arrow keys and optional Home/End. No collapsing feature was added because the brief requires a minimum width.

Direct HTTP research failed because the sandbox could not resolve external hosts. Context7 and the installed VS Code source supplied the evidence above.

Monaco's installed `editorConfiguration.js` starts its container observer when `automaticLayout` is true. `elementSizeObserver.js` uses `DisposableResizeObserver` and animation-frame scheduling. The existing `automaticLayout: true` therefore covers this container resize; no duplicate manual layout listener was added. This conclusion is source-verified, not browser-verified.

## 2. Diagnostic hover

The save-time diagnostic now displays escaped prose and a separate, muted source line: `YAML · server parser` for manifests and `Python · server parser` for Python. Explicit `isTrusted: false` and `supportHtml: false` keep diagnostic content from becoming executable commands or HTML. No Quick Fix, View Problem, code action, schema URL or other unavailable control was fabricated.

Inspected the installed `IMarkdownString` definition and markdown renderer. `supportHtml` allows sanitized HTML; trusted markdown additionally permits command links. Neither is needed for the message plus markdown source line. Context7's Monaco lookup returned no matching documentation for these specific flags, so the installed version was the authority.

Hover theme colours are added to the existing `applyTheme` integration. There was no existing custom editor CSS file. The sibling `Editor.module.css` provides the required global Monaco selectors for padded rows, separators between rows, readable wrapping, bounded width, border and token-based shadow. Both the resizable outer widget and `.monaco-hover` use the design tokens, including dark-mode tokens.

The API currently provides a single save-time parser diagnostic. Existing Monaco hover rows can stack with separators; this change does not invent additional diagnostics or infer kubeconform line locations. Kubeconform field errors remain in the result panel and are labelled there.

## 3. Manifest failure panel

`ManifestFailure` now uses `ResultBanner` for the same tinted failure background and mono headline as Python failures. `FailedCase` accepts labelled diagnostic values and uses its existing wrapping, line-numbered wrong-value renderer. Paths retain their case, and messages use the existing failure colours. The Python input/actual/expected rendering remains available and is covered by the updated render test.

Kept the integer-without-quotes hint, raw validator details and generic fallback. Removed the duplicated failure CSS and the unreachable ParserError/ScannerError branch from `manifestFeedback.ts`. Field-level schema feedback identifies kubeconform as its source.

## Verification

Final results:

| Command | Result |
| --- | --- |
| `pnpm_config_verify_deps_before_run=false pnpm --dir web build` | PASS, exit 0; TypeScript and Vite, 3150 modules, built in 3.46s |
| `pnpm_config_verify_deps_before_run=false pnpm --dir web lint` | PASS, exit 0; `oxlint` |
| `node --test web/tests/css-modules.test.mjs` | PASS, 1 test, 0 failures |
| `node --test web/tests/manifest-feedback.test.mjs` | PASS, 1 test, 0 failures |
| `node --test web/tests/task-panes.test.mjs` | PASS, 1 test, 0 failures |
| `git diff --check` | PASS |

Node tests were run one file per invocation. They use Vite's middleware-only loader without listening on a socket; no app server or Playwright process was started.

The first plain pnpm invocation tried an automatic dependency refresh and failed opening the global pnpm SQLite store. Setting `pnpm_config_verify_deps_before_run=false` for the commands used the already-installed dependencies without changing project configuration or installing packages. Build warnings remain for PostCSS's missing `from`, an externalized `node:fs/promises` dependency and large chunks.

A final lint run caught synchronous state setting in an effect during narrow-screen drag cleanup. Cleanup was moved into the resize observer callback, then lint and build passed again.

Mutation verification was performed for both changed/new Node tests. Reducing the brief minimum from 340 to 300 failed the bounds assertion; restoring a parser-specific branch failed the fallback assertion; changing manifest `data-wrong` rendering to `data-right` failed the failure-render assertion. All mutations were restored and the tests passed afterward.

Build deleted `web/dist/.gitkeep`. The prescribed checkout command did not complete and was interrupted. The file was restored from `git show HEAD:web/dist/.gitkeep`; its diff against HEAD is empty.

## Scope and remaining verification

The applicable surface is the web task page for both Python and manifest tasks. Both Run and Submit share the updated failure rendering. The splitter works in both directions and has minimum/maximum keyboard controls; the narrow layout has no resize affordance. Preferences remain browser-local, including the existing storage-event mechanism. No transport, API, remote/relay or tunnel logic was changed, and there is no new Settings entry point.

No browser or Playwright validation was performed. Still unverified: visual fidelity and text wrapping in the actual hover, light/dark appearance, pointer capture across Monaco, touch behavior, keyboard focus and screen-reader announcements, persistence across a real reload, narrow/wide transitions during dragging, live Monaco relayout and axe checks. These need the maintainer's browser pass.

All edited files, test changes, generated build outputs and this report are within `/tmp/drillion-ui-poc`. Nothing was written into `tasks/`. No push, merge, extra branch or unrelated refactor was performed. `UI-POC-BRIEF-2.md` was already untracked on arrival and was left unchanged.

The feedback is consistent with the existing code. The only qualification is that multiple schema diagnostics in the editor cannot honestly be supplied by the current single parser-error API without additional mapping; the result panel remains their existing home.

## Commit status

No Round 2 commits were made. Staging failed with:

```text
fatal: Unable to create '/home/daniel/github/drillion/.git/worktrees/drillion-ui-poc/index.lock': Read-only file system
```

No attempt was made to bypass the read-only metadata. The implementation and report remain uncommitted for the maintainer. The intended commit title is `fix(web): improve task resizing and manifest feedback`, using `git commit --no-gpg-sign` with no co-author trailer or generated footer.
