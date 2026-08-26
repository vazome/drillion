# design-sync notes

The vendored design system in `web/src/ds/` diverges from the Claude Design project by:

- the DIFFICULTY-AND-MOTION patch — `StatusBadge` gains the `easy` / `medium` / `hard`
  difficulty looks and the `quick` grade, `tokens/motion.css` exists and is imported from
  `styles.css`, and the inline transitions in `Button`, `Collapsible` (button + caret),
  `Select`, `Toggle` (track + knob) and `ConflictBanner` reference the motion tokens;
- a `SpecText` rewrite.

Apply both upstream before any `/design-sync`, or the next sync will overwrite them.
