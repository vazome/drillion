Implement the new drillion UI ("B2 · Ladder desk, refined") from the design handoff in `.design-sync/2026-09-23-app-screens/`. It's the settled design for every app screen, in light and dark, plus token and logo updates.

## Read first, then plan

1. Read `AGENTS.md`, `DESIGN.md`, `web/README.md` and `.design-sync/NOTES.md`. The NOTES list the local changes to `web/src/ds/` that must survive.
2. Read the handoff: `README.md` (what each file is), `DESIGN-SYSTEM.md` (the brand book; its **App screens** section is the layout spec), `screens/*.md` (one note per screen), and look at `screenshots/*-light.png` and `*-dark.png`. `screens/*.html` hold the exact values; open any of them with `?theme=dark` or `?theme=light`.
3. Map every screen to the code that renders it now (`Catalogue.tsx`, `Task.tsx`, `TaskPanes.tsx`, `Editor.tsx`, `Deps.tsx`, `Progress.tsx`, `Stats.tsx`, `Settings.tsx`, `App.tsx`, `web/src/ds/*`). List what each screen needs that the API doesn't give yet, for example "opens N tasks" (reverse prereqs), days practised this week, and the counts per ladder rung.
4. Give me a phased plan and wait for my OK before you write any code.

## What changes

**Tokens** (`web/src/ds/tokens/colors.css`, in both `:root` and `.dark`). Add `--control-edge`, `--strength-learning`, `--strength-familiar`, `--strength-solid`, `--heat-0`…`--heat-4`, `--danger-surface`, `--danger-edge` and `--scrim`, with the values in the handoff's `tokens.css`. The existing values already match, so leave them alone. Keep `--focus-ring` built from `var(--surface)`/`var(--accent)`. Control edges (Input, Select, a secondary Button, the search field, TrackRail pills) move from `--border-strong` (1.6:1) to `--control-edge` (3:1). Keep `--border-strong` for hairlines.

**Logo and favicon.** Replace `web/public/favicon.svg` with `assets/favicon.svg`. It switches colours with the theme, and the inside of the d is transparent. Add `favicon-32.png`, `favicon-16.png`, and `favicon-180.png` as the apple-touch-icon, with their `<link>` tags in `web/index.html`. `logo*.svg` are the same mark if the app or README draws it anywhere. `assets/wordmark-candidate.svg` is a candidate only: don't use it.

**Screens.** Build them in this order, one reviewable commit each:

1. **Shell.** A 248px sidebar: the wordmark and task count, Catalogue and Progress, then "New picks from" with the tracks as bars sized by task count. Settings, the theme switch and the version line sit at the foot. The Task page swaps the sidebar for a 48px top bar with a breadcrumb.
2. **Today and Catalogue.** A one-sentence headline for the day, with "done today" and "practised" beside it. Up next is a card with a number panel, what passing it opens, and Start task (Enter). Beside it, the ladder: seven rungs labelled 2d…120d, grouped under learning/familiar/solid in their colours, plus a 7-day practised strip with today dashed. Pick up where you left off: four cards, with the state they share said once in the band's line. Catalogue: `/` search by the heading, a status toggle with counts, wrapped tags, one-line rows, "needs 289" in words, and the up-next row marked.
3. **Task header.** Two lines when a task has prereqs. Line one: number, title, timer. Line two: difficulty · path · status · Needs chips (▲ warn not passed, ✓ pass passed; titles dropped past two chips or past a 30-character title, kept in a tooltip) · "Opens N tasks →", or "Lineage →" when it opens nothing. Abandon is a quiet link beside the timer.
4. **Task page.** The spec pane has a "Stuck?" bar pinned to its foot, holding the hint countdown and the solution gate. File tabs: yours first with a `yours` pill; context files `read-only`. The bar under the editor is grading only: submits and seed, Run (secondary), Submit (the one primary).
5. **Result panel.** Every state in `ScreenResultStates`: idle, running, a green Run, a failed Submit, a pass that climbs, a struggled pass with the keeps-beating-you note, a hint revealed, the solution shown, the changed-on-disk banner, and the 30-minute nudge. A failed Run says no attempt was used and nothing moved.
6. **Review after a pass.** The editor pane becomes Review, with Compare · Yours · Reference and side by side or inline. Changed lines use `accent-tint` with `accent-line` word marks, never red or green, because both versions passed. The spec pane narrows to 440px. The passed banner sits under the diff. `ScreenTaskReviewFiles` (several edited files) is a future case: build it only if a task already edits more than one file; otherwise leave the component ready and note it.
7. **Lineage.** Three columns (needs · this task · opens) joined by curves: warn dashed for a prereq not passed, pass solid for a passed one, control-edge dashed for what the task opens. Every card opens its own lineage, and "Open NNN" goes to the editor.
8. **Progress.** Three strength cards with the live "back in …" ranges from `strength.ts`, the 14-day due load (cap dashed, overflow hatched), the practice year on `heat-0`…`heat-4`, topic depth with stuck topics first, and the last 30 sessions.
9. **Settings dialog.** Over `--scrim` with a 3px blur: Editor, Your data (paths with Copy), Back up and Restore side by side, and the Danger zone on `--danger-surface` in a `--danger-edge` frame. Its button stays disabled until `erase progress` is typed.

## Rules

- Real data only. The screenshots use real tasks (289, 290, 322, the docker track); Progress uses sample data. Never hardcode what the API serves. If a screen needs data the server lacks, add the smallest API change and say so in the commit.
- Prereqs are information, never a gate.
- A strength colour always sits beside its word and a 1/2/3-bar mark, never colour alone.
- No streaks. No new gradients, shadows or blur except the dialog backdrop.
- Keep every existing keyboard binding (`/`, Enter on the first row or on Up next, `Mod-Enter`). If the design's Run/Submit shortcuts conflict with what the app does now, keep the app's and tell me.
- Components stay vendored in `web/src/ds/`. Use CSS Modules and tokens only: no raw hex values in components, no Tailwind.
- WCAG AA in both themes. The contrast table in `DESIGN-SYSTEM.md` lists the pairs that sit at the floor: don't lighten those.

## Done means

- `pnpm --dir web build`, `pnpm --dir web lint` and `pnpm --dir web test` pass. Ask me before running `pnpm --dir web screens` (Playwright + axe), then make it pass. Update any e2e expectations the new layout changes, and say which.
- For each screen, a screenshot in light and dark next to the matching handoff PNG, with the differences listed.
- A new dated section in `.design-sync/NOTES.md` saying what came in, what was adapted locally, and what's left out.
- Work on a new branch with small commits. Don't push or open a PR until I say so.
