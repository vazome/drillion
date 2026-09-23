# design-sync notes

## Ladder desk (B2, refined) · 2026-09-23

Source: the handoff in `2026-09-23-app-screens/` (README, PROMPT, DESIGN-SYSTEM.md, tokens, one
HTML and PNG per screen), committed without its `fonts/`. Every screen was rebuilt against it:
the sidebar shell, Today and the catalogue, the task header, the task page, the result panel,
Review, the lineage, Progress and Settings. The old top header, `Stats.tsx` and the two-step
danger zone are gone.

**Tokens.** `--control-edge` (every control's outline: Button secondary, Input, Select, Toggle,
NoteField, StuckNudge, ConflictBanner, TrackRail), `--strength-learning/familiar/solid`,
`--heat-0..4`, `--danger-surface`, `--danger-edge`, `--scrim` (the dialog backdrop and the
lineage overlay, the only blur). The favicon is theme-aware SVG plus 16/32 PNGs and a 180px
apple-touch-icon.

**Decisions made while building it:**

- *Review queue.* Up next is the head of the queue: reviews first, most overdue first, then
  new picks. The headline is a sentence: "One new pick, nothing due." / "12 reviews and 2 new
  picks." / "12 of 100 due reviews today, and 2 new picks." Over the cap, a muted line says
  "12 are served a day; the other 88 stay due." The Up next foot reads "1 of 14 today · then
  291 · 305 · 118 · all due →"; the numbers are links and "all due →" opens the catalogue with
  the due filter on. "Next in Today" after a pass moves to the next item.
- *Placement.* The first-run note sits above the headline and can be dismissed. With nothing
  left at all, the no-new reason fills the Up next card with its action (Clear focus, or the
  prereq link); with reviews left but no new picks, it is one muted line in the card's foot.
  "Worth a focus" moved to the sidebar under New picks from: "You keep struggling with [tag] ·
  N flagged", where the chip toggles focus. The spec pane ends with archive, note, hints, in
  that order, above the Stuck? bar, and a revealed hint scrolls into view.
- *Theme on the task page* is a text button with an icon (Sun/Asleep + Light/Dark) in the top
  bar, on the same state and store as the sidebar switch.
- *Narrow widths.* Below 1100px the sidebar becomes the 48px top bar (wordmark, Catalogue,
  Progress, Settings, theme) and New picks from moves into Today as wrapping track chips with
  the stuck line. Up next and the ladder stack; the recent cards go to 2 columns, then 1. The
  task puts the spec above the editor with the Stuck? bar pinned to its foot, and Review goes
  inline. The lineage columns stack under plain headings with no curves. Progress cards wrap
  and the year scrolls inside its own box. Nothing scrolls the page sideways at 720px.

**Local changes to vendored components:** RowFlags reads `needs 289` in warn mono; TaskPath
mutes the tier; Timer is `m:ss` at 17px; RequiresTag is a 24px borderless chip; FileTabs is an
editor-edge strip with an inset accent top; Dialog has a 64px header with "Esc closes" and an
icon-only Close; DepLineage is rewritten (280px cards, coloured curves, a `stacked` mode for
narrow screens, a legend); DueForecast draws the cap line and a hatched overflow;
PracticeHeatmap uses `--heat-0..4` on fixed 14px squares and scrolls, focusable, inside its
box; TopicStrips colours by strength and takes `bands`, `label`, `lapseLimit` and a sort.
`index.d.ts` follows.

**API additions**, each the smallest that made a screen real: `GET /api/picks` (focus, track
sizes, the stuck tag), `stats.week` (the last seven days worked), `prereqs` on catalogue rows,
`difficulty` and `status` on lineage refs, and `lapse_limit` on progress.

**Left out, and why:**

- Nav icons for Catalogue and Progress: neither is in the fixed Carbon set. The All tracks mark
  is a CSS 2x2 glyph.
- The fade above the Stuck? bar: no new gradients.
- The failed Run's list of rules that passed: the graders report only failures, so it says
  "N rules not met".
- "up next in Today" on lineage cards: that screen has no queue to ask.
- "See the passing code" after a pass: Review already shows it.
- ScreenTaskReviewFiles: every task edits one file, so Review takes one.
- Kept against the drawing: the catalogue's Known column, the FileTabs note line, tab size 8,
  and the Back to Today button beside Next in Today.
- TrackRail and ResultBanner are no longer used but stay vendored.

**Keyboard.** `/`, Enter on the first row or on Up next, and Mod-Enter / Mod-Shift-Enter all
still work. The grading bar is drawn under the editor but comes first in the DOM, so Tab
reaches Run before Monaco, where Tab only indents.

**E2e expectations changed:** Today is found by its Up next heading; results by region name
(Result of submit N, Output of your run) and the verdict words; Key binding, Tab size and the
Practice timer are pressed buttons; the danger zone is one step with no Cancel; the dialog
closes by "Close settings"; the lineage reads "Needs · N" and the header button "Opens N tasks";
a passed task opens on Review, so the a11y spec moved to 010; the restore wait is 30s because
it fsyncs every saved task file.

## Carbon icons — 2026-09-22

Source: the design system at 0.9.0 (`04a3cba`). `Icon`, `icons.js` and the Carbon licence came
in as a patch: 32 IBM Carbon icons copied from `@carbon/icons` 11.88 (Apache 2.0), with no
new dependency. The text glyph list is retired. Collapsible, Select, SortReset, Table,
Timer, ResultBanner, RequiresTag, GraceNotice, StuckNudge, DepLineage, ConflictBanner and
NoticeBanner now draw an `Icon` where they drew ▸ ▾ ↺ ▲ ▼ ⏸ ✓ ✗ × or →, and the screens
follow. An icon always sits beside a word and is `aria-hidden`; Dismiss is the one
icon-only control. Only prose keeps a glyph (`·` separators, "struggled 4×").

One local change: `Toggle`'s `label` is typed `ReactNode` instead of `string`, so the
header's theme switch can lead its word with Sun or Asleep.

## CSS Modules sync — 2026-09-10

Source: the supplied `drillion design system.zip` export. Components remain vendored.
The export uses prefixed global selectors and a `const s` class-name map because its
preview does not load modules. In Vite, replace that map with a default import from the
sibling `.module.css`, remove the component prefix from its selectors, and flatten sibling
component imports into `web/src/ds/`. Do not import the export's aggregate component CSS
from `styles.css`: Vite includes each module through its component. Keep `className` and
`style` in `index.d.ts` aligned with the runtime props.

The conversion carries these local adaptations forward:

- `SpecText` keeps `react-markdown`, GFM, alert classes, and task asset URLs. Its module now
  owns prose, tables, syntax colours and scoped plugin callouts; none belong in `tokens/base.css`.
- `Dialog` closes the native element on both Close and backdrop clicks; its close event
  reports the result. Its module keeps the fixed header, scrolling body, blur and open/close
  transitions. These differ from the export's sticky header and callback-only close buttons.
- `StuckNudge` retains the hint/read-material copy and no bury action. `ResultBanner` keeps
  entrance animation in its app wrapper. `DepLineage` retains `hrefOf`-controlled links.
- `PracticeHeatmap` derives a separate cell size instead of reassigning an effect dependency.
  Table headers retain sans-serif labels even for monospace data columns.
- Settings uses the export's single-column sections, aligned rows and key-binding dropdown,
  with styles in `Settings.module.css`. It retains the app's full font list, ligatures, tab
  size, relative line numbers and Restore workflow, which the mock omits. Paths and actions
  use the real API; preferences still use the shared browser store. Rows stack on narrow
  screens, and the dialog body is the only scroll area.
- `tokens/motion.css` and all other token values stay local and unchanged. `Kbd` still uses
  the native-element rule in `base.css`, matching the export.

Check with `pnpm --dir web build`, `pnpm --dir web lint`, and
`pnpm --dir web test`. With browser verification approved, also run
`pnpm --dir web screens` for keyboard, accessibility and task rendering coverage.

## Earlier sync notes

Some differences below have since landed upstream. The snapshot notes above take precedence
for component styling and the current local adaptations.

The vendored design system in `web/src/ds/` diverges from the Claude Design project by:

- the DIFFICULTY-AND-MOTION patch — `StatusBadge` gains the `easy` / `medium` / `hard`
  difficulty looks and the `quick` grade, `tokens/motion.css` exists and is imported from
  `styles.css`, and the inline transitions in `Button`, `Collapsible` (button + caret),
  `Select`, `Toggle` (track + knob) and `ConflictBanner` reference the motion tokens;
- a `SpecText` rewrite, and its asset URLs pointing at the real route `/api/task/{slug}/assets/{name}`;
- the vocabulary — comments, doc strings and `ConflictBanner`'s default message say *task*, the
  noun this project uses, not *drill*;
- a reduced-motion fix in `tokens/motion.css` — the upstream
  `@media (prefers-reduced-motion: reduce)` block zeroes the durations but not the delays, so
  `.m-stagger` and `.m-step` still trickled in over up to 260 ms. We add `animation-delay: 0s`
  and `transition-delay: 0s` to that block.
- a `Table` sortable-header accessibility fix — upstream leaves the sortable `<th>` without
  `aria-sort` and gives the header button a static `aria-label`, so a screen-reader user gets
  no signal of which column is sorted or what activating a header will do. We add `aria-sort`
  (`"ascending"` / `"descending"` / `"none"`, omitted on non-sortable columns) and make the
  button's `aria-label` name the direction the existing toggle will actually apply;
- an `Input` accessible-name prop — upstream `Input` accepts no `ariaLabel`, so the catalogue's
  search box shipped with no accessible name while the `Select` beside it had one. We add
  `ariaLabel` and render it as `aria-label`, matching `Select` and `Toggle`;
- `StatusBadge` drops the `scheduled` status and the `failed` grade — `api.py _status()` emits
  only `new`/`due`/`open`/`done`, and `scheduler.grade_of()` only `quick`/`pass`/`struggled`
  (plus `abandoned` from `attempts.abandon()`). `index.d.ts` matches;
- a callout block in `tokens/base.css` — upstream has no styling for GitHub alerts, and the
  plugin's own `alert.css` hardcodes GitHub's hexes and shows an octicon per panel. We draw the
  callouts from our tokens instead (left rule + tint per type, `--accent` / `--pass` / `--warn` /
  `--fail`) and hide the icon, leaving the uppercase label to name the type. `SpecText` passes
  `className` through on `p` so `markdown-alert-title` survives to be styled;
- `Timer` keeps its `parMinutes` prop, and drillion never passes it: par time never leaves the
  server, so the timer always renders bare elapsed time. The prop is dead here on purpose —
  leave it, so a resync is a no-op rather than a conflict.

- `RequiresTag` and `DepLineage` are vendored as `.jsx` with their prop contracts in
  `index.d.ts`, not as `.tsx` files carrying their own types the way the handoff prompt asked.
  Every other component here is `.jsx` + `index.d.ts`, and matching the idiom is what keeps a
  `/design-sync` a one-to-one file copy;
- the task payload sends each prereq edge already resolved — `{slug, topic, title, state}` —
  rather than the handoff's bare slugs. The design-system mock resolves slugs against a task
  list it holds in memory (`depsOf` in `ui_kits/drillion/Task.jsx`); the real task screen holds
  only its own task, so bare slugs would mean fetching the whole 182-row catalogue on every
  task open to look up two titles;
- `DepLineage` is a wired graph here, not the five-column chip grid the design-system
  component draws. It follows `explorations/dependency-graph.html` option C instead: fixed-size
  cards in three columns, joined by SVG beziers — solid for a passed prereq, dashed for a
  blocking one — with the `Before and after` summary row and the per-column headings dropped,
  a ladder meter and an `also needs NNN` line on each node, and a column that folds past eight
  nodes (a task can unlock twenty). Every node wears its first tag as a `TagChip`, and takes
  `ladder`, `hrefOf` and `onPrefetch` props the upstream component has no notion of —
  `onPrefetch` fires on hover and focus so walking the graph swaps a board instead of
  reloading a screen. Apply this upstream before any `/design-sync`, or the sync reverts a
  reviewed decision;
- every prereq link goes to that task's *lineage* (`#/task/{slug}/deps`), not to the task —
  including the chips in the task header, where the handoff said the opposite. You follow these
  to walk the graph; `Open NNN →` is the one way out of it into an editor;
- `DepLineage`'s `shortestPath` footer is never passed: the server does not compute a shortest
  way in. The prop stays, so a resync is a no-op;
- `Run` grades nothing here. The design-system mock runs it against the spec's worked example
  (`Output · your run`, stdout); drillion has no notion of the example as an input, so a Run
  executes the same pytest as a Submit and simply costs no attempt and moves no card.
- `TrackRail` came from the artifact as-is, converted to the local idiom (sibling
  `.module.css` import, `track-rail-` prefix dropped). Its pills replace the track chips that
  used to sit after the tier chips in the filter row, so a track is focused from one place.

Every entry above is a deliberate local divergence. Apply them upstream before any
`/design-sync`, or the next sync will silently overwrite them.
