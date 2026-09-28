# Motion pass: app → design system

The app changed in #300 (motion across the app, and a quieter task page). This folder carries
the matching changes to the drillion design system, ready to publish there. Nothing here is
used by the app.

`project/` mirrors the design system's own file tree: every file sits at the path it has in the
system, so each one replaces its namesake there whole. They were edited from the system's
version `1790454625-a34c`. `screenshots/` shows the three redrawn task cards as they render
with the system's `tokens.css` and `bundle.css`, light theme.

## What changed, file by file

| file | change |
| --- | --- |
| `components/core/FileTabs.jsx` | No caption row under the strip ("part of the chart, read-only, you write…"). Each tab already says `yours` or `read-only`, and its accessible name still says it in full, the run's mark included. `noteOf` and the `notes`/`note`/`file`/`flag` classes are gone. |
| `components/core/FileTabs.module.css` | The five caption-row rules removed. |
| `components/core/FileTabs.d.ts` | `partOf` is said in each locked tab's accessible name, not in a note. |
| `components/core/FileTabs.prompt.md` | The guidance drops the note under the strip. |
| `components/chart/PracticeHeatmap.jsx` | A month label is dropped when the next starts within three columns, so a clipped first month no longer prints over the second ("SepOct"). The native `title` on each square is gone: it doubled the hover bubble. |
| `components/bundle.js`, `components/bundle.css` | The same two changes, patched into the compiled bundle and its stylesheet line for line (no rebuild). Checked by mounting both components from the patched bundle: no errors, no caption row, labels start "Oct Nov Dec", no `title` attributes. |
| `README.md` | Hand-written part only; the generated tail is byte for byte as it was. The grade line loses "back in 8 days" (the ladder row says it); Motion gains the spring and the app's patterns; Task describes the one-line header; After a pass describes the new banner and Review's plain bar; FileTabs gains "nothing is written under the strip". |
| `components/ScreenTaskHeaders/preview.html`, `README.md` | Redrawn: the header is always one line. Four examples: a prereq not passed, passed, two prereqs whose chips drop their titles, and no prereqs. |
| `components/ScreenTask/preview.html`, `README.md` | Header: no "No prereqs", no "Opens 4 tasks", no "active" beside the timer. |
| `components/ScreenTaskReview/preview.html`, `README.md` | Header as above; Review's bar says "2 lines differ"; the left pane is headed plain "Yours"; the banner drops "back in 4 days" and the archive line, and gains the ladder row with 4d lit. |

Left as they were: `tokens.json`, `tokens/motion.css` (the app's durations and easings are the
same values), every other component and card, and the generated `api/` cards, `tokens.css` and
`manifest.json`, which the design system's page rewrites on its next save.

`PROMPT.md` is what to hand the design-side session.
