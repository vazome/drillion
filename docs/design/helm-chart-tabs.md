# Design handover: chart file tabs

One component for the task page (`#/task/:slug`), to be drawn in Claude Design and vendored into
`web/src/ds/` like the rest of the Mineral Blue system. [`DESIGN.md`](../../DESIGN.md) is the
product brief, [`CONTEXT.md`](../../CONTEXT.md) the vocabulary, and the concept this serves is
[`2026-09-22-helm-levels-1-2-design.md`](../superpowers/specs/2026-09-22-helm-levels-1-2-design.md).

## Why it is needed

drillion is adding Helm tasks. A Helm task is a chart with one file missing: the learner writes
that one file, and every other file of the chart is there to be read, not changed. On level 1
the learner writes `values.yaml` and reads the templates to find which keys do what; on level 2
they write a template and read `values.yaml` to learn what it can refer to. So the learner
has to switch between 2 to 6 files while only one of them is theirs.

Today the task page has exactly one file: the editor. This component lets it show several
without turning into an IDE.

## What exists

- The design system: `web/src/ds/`, plain React components over CSS custom properties with
  sibling CSS Modules, no Tailwind, no component library. Tokens in `web/src/ds/tokens/*.css`
  (both themes, IBM Plex Sans / Spline Sans Mono, spacing, motion). Closest relatives:
  `TrackRail.jsx` (a row of selectable pills), `Collapsible.jsx` (the head row idiom: mono,
  a caret, a faint `meta`).
- The task page (`web/src/Task.tsx`), editor side, top to bottom:
  1. a toolbar row: `attempt N`, `seed N`, a right-aligned `● unsaved` or `● syntax error on
     line N, not saved` in `--warn`, and Abandon;
  2. the Monaco editor, `clamp(280px, 42vh, 560px)` tall for non-Python tasks, themed from
     the same tokens;
  3. the Result card: a banner, the validator's diagnostics, then collapsibles.
- The track rail already has a `helm` track with its logo.

## What to draw: `FileTabs`

A tab strip that sits with the editor and picks which file it shows.

**Props**

```ts
files: {
  path: string        // "values.yaml", "templates/deployment.yaml", "Chart.yaml"
  readOnly: boolean   // exactly one file is false: the learner's
  marked?: boolean    // the last run reported a problem in this file
}[]
active: string        // the path shown in the editor now
onSelect: (path: string) => void
```

The order is fixed by the task, and the learner's file always comes first. Nothing is added,
closed, renamed or reordered: there is no `+`, no `×` and no drag.

**States each tab needs**

- **The learner's file, active and inactive.** It is the one that matters, so it should read as
  "yours" even when another tab is open. Its unsaved and syntax state stay in the toolbar row
  above, not on the tab.
- **A read-only file, active and inactive.** Visibly locked, so nobody types into it and
  wonders why nothing happens. When a read-only tab is active, the strip or the editor edge
  says so in words ("part of the chart, read-only"), not only with an icon.
- **Marked.** A run can report a problem inside a read-only file: the learner's values reached
  a template they cannot change. The mark says "look here" without being an alarm; the
  message itself is already in the Result card.
- **Long paths.** `templates/deployment.yaml` is typical. The directory can be quieter than
  the file name.

**Where it sits:** above the editor is the usual place and nearest the code; below the editor,
beside Run and Submit, was the first sketch. Pick one and say why. It must not push the editor
down or re-wrap when a tab is marked or selected: the toolbar row already works hard to never
move under the cursor.

## Hard constraints

- Both themes from the tokens, with no colour that exists in only one.
- No new dependency.
- Calm, like the rest of drillion: no badges with counts, no pulsing, no colour-only meaning.
- Accessible: `role="tablist"` / `tab` with `aria-selected`, arrow keys between tabs, Home/End,
  visible focus, read-only and marked states in the accessible name and not only in colour.
  `e2e/a11y.spec.ts` runs axe (WCAG A and AA, `color-contrast` included) in both themes and
  reflow at 200% zoom, so the strip has to survive both. At narrow widths it may scroll
  sideways inside itself, but never the page.
- `prefers-reduced-motion`: any transition collapses to nothing.
- It is not an IDE: no file tree, no folder nesting, no icons per file type, no split view.
  Six tabs is the realistic maximum.

## Deliverable

- `FileTabs.jsx` and `FileTabs.module.css` in the `ds/` idiom (named export, props as above).
- One entry in `ds/index.d.ts` and one export in `ds/index.js`.
- Any new tokens added to `tokens/*.css`.
- A mock of the task page's editor column with it in place: level 1 (learner on `values.yaml`,
  four read-only files, one marked) and level 2 (learner on `templates/deployment.yaml`, a
  read-only file active), each in light and dark.

Agents integrate it: showing the read-only files in the same Monaco editor with editing
switched off, wiring `marked` from the run's diagnostics, and the "Rendered" output, which
reuses `Collapsible` and needs no new drawing.
