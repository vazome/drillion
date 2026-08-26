# design-sync notes

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

Every entry above is a deliberate local divergence. Apply them upstream before any
`/design-sync`, or the next sync will silently overwrite them.
