# Round 2: a real splitter, VS Code grade diagnostics, and errors that look like drillion

Same worktree, branch `poc/manifest-ui`. Round 1 is committed (`345a93d`, `54a9e12`). The
maintainer has now used it in a browser and has three pieces of feedback. He is the person
whose taste decides this, so treat his words as the spec.

Read `UI-POC-BRIEF.md` for the project background and the hard constraints. They all still
apply, especially: **no new dependencies**, React 19 + Vite + CSS Modules + the local design
system in `web/src/ds/`, no Tailwind, no component library.

---

## 1. A centre splitter between the two panes

His words: *"that slider on in the center you know like in modern systems basically."*

Today the left pane is a plain `<div>` with `resize: horizontal` (`web/src/Task.tsx`, the
element with `width: "42%", minWidth: 340, maxWidth: "70%", ... resize: "horizontal"`). It
does work - dragging takes it 610px to 834px and the editor shrinks to match - but the only
grab target is the native corner grip at the bottom-right of a very tall pane, with
`cursor: auto`. He drew a red box around that whole empty seam between the panes and
circled the grip: he expects to drag **anywhere along the divider**, as in VS Code, Figma,
or any modern split pane.

Build a real splitter. Research current practice first rather than inventing it: look at how
VS Code's sash, `react-resizable-panels`, and the ARIA `separator` pattern handle this, then
write the minimal version for this codebase. **Do not install any of them**; read them and
implement it yourself.

What a good one does, and what the review will look for:
- A full-height drag handle sitting between the panes, with `cursor: col-resize`, a hit area
  wider than the line you actually draw (roughly 8-10px of target for a 1px visual seam), and
  a hover/drag highlight using existing tokens.
- Pointer events, not mouse events, and `setPointerCapture` so a fast drag that leaves the
  handle keeps tracking. Release on `pointerup`/`pointercancel`.
- Keyboard accessible: `role="separator"`, `tabindex="0"`, `aria-orientation="vertical"`,
  `aria-valuenow/valuemin/valuemax`, and left/right arrows moving it in steps. Home/End to
  the extremes is a nice touch. **The repo runs axe accessibility checks in Playwright, so a
  handle with no name or no role will fail the build.**
- Respect the existing bounds (`minWidth: 340`, `maxWidth: "70%"`), and collapse to a single
  column on a narrow screen exactly where the current `narrow` branch does.
- Remember the position across reloads if that costs you almost nothing. `web/src/prefs.ts`
  is where per-user client settings already live; follow whatever it does rather than
  inventing a second mechanism. Do not add a preference to the Settings screen for this.
- Monaco needs to relayout when the pane resizes. The editor is constructed with
  `automaticLayout: true`, so confirm whether that is enough and say what you found.

Take the `resize: horizontal` off the pane once the splitter works. Two mechanisms for one
job is worse than either.

---

## 2. Diagnostics that look like VS Code's

His words: *"I need vscode like errors that I can see in vscode they lok proper and cool!!"*

Round 1 got the behaviour right and the presentation plain. The squiggle and hover work: an
invalid save is marked on its line and the message shows on hover (`web/src/Editor.tsx`, the
decorations effect). What lands is a bare grey box with one line of unstyled text.

VS Code's, which is what he pasted as the target, is a panel with clear structure:
- the message in readable prose at the top,
- the **source** of the diagnostic set apart from the message, dimmer and smaller - in his
  screenshot, the word `YAML` after the message text, and on the second entry a
  `yaml-schema:` label with the schema URL underneath,
- multiple diagnostics on the same spot stacked in one panel with separators between them,
- a row of actions at the bottom, and
- generous padding, a border, a real shadow, and a max width so long text wraps instead of
  stretching across the screen.

Get as close to that as is honest here. Notes:
- Monaco's `hoverMessage` takes an `IMarkdownString`, so markdown formatting, code spans and
  dimmed source labels are available without any new dependency. Check what `supportHtml`
  and `isTrusted` allow in this version before relying on either.
- The hover widget is `.monaco-hover`. It can be styled from a stylesheet using the existing
  design tokens, including the dark-mode ones. Find where the app's global editor styling
  already lives and put it with that rather than starting a new pattern.
- Do not fabricate the parts drillion cannot honestly provide. There is no quick fix, no
  code action, and no problems panel, so **do not draw "Quick Fix..." or "View Problem"
  links that do nothing.** A convincing imitation with dead controls is worse than an honest
  panel. If an action genuinely works, add it; otherwise leave the row out.
- A truthful source label is available and worth showing: the YAML parse error comes from
  the server's YAML parser, and the schema errors come from kubeconform. Say which.

---

## 3. The manifest failure panel should look like drillion's own

His words: *"I dont like the way errors are stylilized, python errors in drilion lokoked
better much better, idk tink about it."*

He is right, and the cause is concrete. A failed python run renders through
`web/src/ds/ResultBanner.jsx`, whose failed state is a tinted panel:

```css
.root[data-state="failed"]{background:var(--fail-bg);border-left:3px solid var(--fail);color:var(--text)}
.headline{font-family:var(--font-mono);font-size:13.5px;white-space:pre-wrap;color:var(--fail);font-weight:600}
```

and the detail below it renders through `ds/FailedCase.jsx`, which lays out labelled mono
values on `--surface-2` with `--fail-bg`/`--pass-bg` for the wrong and right ones.

`ManifestFailure` in `web/src/ManifestWorkspace.tsx` bypasses all of that. It has the left
rule but no tinted background, and its headline is a sans `<h3>` at `--fs-h` where the whole
rest of the app uses a mono headline for a failure. That is the entire reason it reads as
belonging to a different application.

Rework it so a failed manifest and a failed python run are visibly the same product. Reuse
`ResultBanner` and `FailedCase` where they fit rather than restyling copies of them - a
field path and its message are close to the labelled-value pair `FailedCase` already draws.
Deleting `ManifestWorkspace.module.css` rules that exist only because they duplicate
something in `ds/` is a good outcome, not a loss.

While you are in there: `manifestFeedback.ts` has a dead branch. The `ParserError`/
`ScannerError` case can never fire, because a YAML parse failure is rejected at save time as
a 400 with `output: ""`, and the call site requires `result.output` to be truthy. That path
now shows as an editor squiggle instead. Remove the dead branch.

---

## Constraints and verification

- `pnpm --dir web build` and `pnpm --dir web lint` must pass. Run both.
- `node --test web/tests/css-modules.test.mjs` and
  `node --test web/tests/manifest-feedback.test.mjs` must pass. Run them **one file per
  invocation**, which is how `web/README.md` documents it; `node --test web/tests/` fails
  for unrelated reasons.
- **`web/dist/.gitkeep` is a tracked file and `pnpm build` deletes it.** Check
  `git status` before you finish and `git checkout -- web/dist/.gitkeep` if it is gone.
- Commit with `git commit --no-gpg-sign`, conventional titles, no co-author trailer, no
  "generated with" footer, no em dashes. Last time git failed because your sandbox mounted
  the worktree's git metadata read-only. If that happens again, **leave the work uncommitted
  and say so in the report** - do not fight it, it will be committed for you.
- You cannot reach a local socket, so you cannot run the app or Playwright. Do not claim you
  did. Say plainly what you could not verify; it will be verified for you in a browser.
- If you write a Playwright test, note that typing into Monaco at full speed corrupts the
  buffer through a pre-existing race in the value-push effect. Use
  `keyboard.type(text, { delay: 80 })`. This affects tests only, not real users, and is not
  yours to fix.
- Never write into `tasks/`. Do not push, do not merge, do not touch other branches.

Write `/tmp/drillion-ui-poc/UI-POC-REPORT-2.md`: what you changed, what you researched and
what you took from it, what you could not verify, and anything you think is wrong with the
feedback.
