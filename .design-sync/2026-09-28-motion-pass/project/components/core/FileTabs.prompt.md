The files of a task — a Helm chart, a Docker build context — as a tab strip on the editor's top edge: the learner writes one file and reads the rest.

```jsx
<FileTabs files={chart.files} active={open} onSelect={setOpen} panelId="editor-panel" />
<FileTabs files={context.files} active={open} onSelect={setOpen} panelId="editor-panel"
  label="Build context files" partOf="the build context" />
<div id="editor-panel" role="tabpanel" aria-label={open}>
  <Editor readOnly={!isMine(open)} … />
</div>
```

`files` puts the learner's file first, and exactly one has `readOnly: false`. That tab wears
the `yours` pill; every other tab says `read-only` itself, as a quiet word after its name led by Carbon's `Locked` at 12px (the
way Collapsible's faint meta sits on its row). There is no group label in the row: an
uppercase READ-ONLY between the tabs read as one more control, and with one read-only file
(`Dockerfile | app.py`) people clicked it. `partOf` names what the locked files belong to —
`"the chart"` by default, `"the build context"` for a Dockerfile task — and each locked tab's
accessible name says "part of the build context, read-only". Nothing is written under the
strip: the pill, the lock and the word already say which file is whose. `marked` means the
last run reported a problem in that file: a wavy warn underline under the name (the editor's
own squiggle, a shape as well as a colour), and the tab's accessible name says so.

Place it between the Run/Submit row and the editor, flush with the editor, whose top corners
go square. Not in the toolbar row: that row wraps, and file paths there would re-wrap it and
push the editor down. The strip never wraps (it scrolls inside itself) and has nothing under it,
so picking a tab or a new mark never changes its height and never moves the editor.

It is not an IDE: no tree, no add, close, rename or reorder, no file-type icons, no split view.
Arrow keys, Home and End move and open in one step.

Its own root has `min-width: 0`, but a parent grid or flex item must allow it too
(`minmax(0, 1fr)` tracks, `min-width: 0` on the column), or a long strip widens the page
instead of scrolling inside itself.
