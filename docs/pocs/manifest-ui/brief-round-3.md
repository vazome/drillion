# Round 3: delete the two pieces that made a manifest look like a different app, then review my edits

Same worktree, branch `poc/manifest-ui`. Rounds 1 and 2 are committed through `554dcd8`.
Read [`brief.md`](brief.md) for background and the standing constraints; they all still apply,
especially **no new dependencies**.

The maintainer has used round 2 in a browser. His verdict: *"other than that I think it is
ok."* Two things go. Both are deletions, and the diff should be mostly red.

---

## 1. Remove the "Need a starting point?" outline entirely

His words: *"we dont need this part."*

That is `ManifestHelp` in `web/src/ManifestWorkspace.tsx`, the whole collapsible: the
explanation, the `YAML_OUTLINE` constant, the Insert outline and Remove outline buttons, and
the `task.yaml` / `YAML · whole document` bar that sits above it.

Delete all of it:
- `ManifestHelp` and `YAML_OUTLINE` from `ManifestWorkspace.tsx`
- its render site in `web/src/Task.tsx`, including the `key={...}` and the `disabled={...}`
  expression feeding it
- the now-dead rules in `ManifestWorkspace.module.css` (`.help`, `.filebar`, `.explanation`,
  `.outline`, `.actions`, and `.file` if nothing else uses it)
- any test that referenced the outline

The editor for a manifest should sit exactly where the editor for a python task sits, with
nothing above it.

## 2. Make the brief use python's arrangement, not its own

His words: *"why it differs from python arrangement why there is file name and blue line?"*

`ManifestBrief` gives a manifest a blue `border-top:3px solid var(--accent)` rule and a row
reading `task.yaml` on the left and `Requirements for this sitting` on the right. A python
task has neither. There is no reason for the two kinds to introduce themselves differently,
and the blue rule in particular reads as a different product.

In `web/src/Task.tsx` the spec card currently branches on kind for both its label and its
body. Remove the branch entirely, so a manifest renders exactly as python does:

```tsx
<Card label={`Spec · ${slug}/README.md`}>
  <SpecText text={task.spec_md} slug={slug} hideTitle />
```

Then delete `ManifestBrief` from `ManifestWorkspace.tsx` and its rules from
`ManifestWorkspace.module.css` (`.brief`, `.intro`, `.aside`, and the `.brief h2` / `.brief
code` overrides).

Keep the sentence `ManifestBrief` carried about Run versus Submit **only if** it already has
a home that is not kind-specific. If keeping it means inventing a new wrapper, drop it: the
Run and Submit buttons already carry their own shortcut hints.

After both deletions, `ManifestWorkspace.tsx` should hold `ManifestFailure` and nothing
else. If the file is then one component, consider whether it still earns its own module or
belongs beside the failure rendering it now solely provides. Your call; say what you chose.

**Do not touch `ManifestFailure`, the diagnostic hover, or the splitter.** He is happy with
all three.

---

## 3. Review pass on the maintainer-side edits

Some of what is on this branch was written by Claude, not you, and has not had a second
pair of eyes. Review it as a reviewer, not an implementer: report what you find, and fix
only what is clearly wrong and small. Anything larger, describe and leave.

**a. `54a9e12` — the editor diagnostic plumbing.**
- `web/src/useDraft.ts`: the 400 handler previously set a `syntaxBad` boolean and dropped
  `e.detail`; it now stores `{ message, line }` and exposes both `syntax` and a derived
  `syntaxBad`. Check every site that cleared the old boolean still clears the new state, and
  that nothing reads a stale value after a run lands or an attempt is abandoned.
- `web/src/Editor.tsx`: the decorations effect. Check specifically: is the decorations
  collection ever leaked or left attached to a disposed editor when `kind` changes and the
  editor is rebuilt? Is `marks.current` reset on that path? Are the deps right, or does the
  marker go stale when the model changes under it? Is clamping the line to the model's line
  count correct when the buffer shrank after the error was reported?

**b. The `Editor.css` conversion, inside `bcdcb99`.**
Your round 2 shipped these rules as `Editor.module.css` imported for side effects. They
never reached the browser: a `*.module.css` whose rules are all `:global()` exports no class
names and the bundler drops the file, so every hover rule was absent from the built CSS
while build, lint and all three node tests stayed green. Claude converted it to a plain
`web/src/Editor.css` with the `:global()` wrappers removed, matching `ds/styles.css`.
Confirm that is the right fix for this codebase, that no rule changed meaning when
unwrapped, and that nothing else in `web/src/` has the same latent problem.

**c. Anything else on the branch that looks wrong to you.** Say so plainly. A finding you
report and do not fix is a good outcome.

---

## Constraints and verification

- `pnpm --dir web build` and `pnpm --dir web lint` must pass.
- Node tests, **one file per invocation**: `css-modules`, `manifest-feedback`, `task-panes`.
- **`web/dist/.gitkeep` is tracked and `pnpm build` deletes it.** Check `git status` and
  restore it before finishing.
- Commit with `git commit --no-gpg-sign`, conventional titles, no co-author trailer, no
  "generated with" footer, no em dashes. If git is read-only again, leave the work
  uncommitted and say so; it will be committed for you.
- You cannot reach a local socket, so you cannot run the app or Playwright. Do not claim you
  did. A browser pass will be run against your work.
- Never write into `tasks/`. No push, no merge, no other branches.

Write `/tmp/drillion-ui-poc/docs/pocs/manifest-ui/report-round-3.md`: what you deleted, what you chose on the
`ManifestWorkspace.tsx` question, and your review findings as a numbered list separating
what you fixed from what you only report.
