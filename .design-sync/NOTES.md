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

Every entry above is a deliberate local divergence. Apply them upstream before any
`/design-sync`, or the next sync will silently overwrite them.
