# drillion design handoff: app screens, 2026-09-23

Exported from the drillion design system (Claude Design, "B2 · Ladder desk, refined"). Unzip into the repo as `.design-sync/2026-09-23-app-screens/`.

| path | what |
| --- | --- |
| `PROMPT.md` | the brief for Claude Code |
| `DESIGN-SYSTEM.md` | the brand book; **App screens** is the layout spec, **Visual foundations** has the contrast table |
| `tokens.css`, `tokens.json` | every token, light and dark; new: `control-edge`, `strength-*`, `heat-0..4`, `danger-surface`, `danger-edge`, `scrim` |
| `screens/Screen*.html` + `.md` | the nine reference screens (1440px wide), token-driven; open with `?theme=dark` or `?theme=light` |
| `screenshots/*-light.png`, `*-dark.png` | the same screens rendered |
| `assets/` | `favicon.svg` (switches with the theme), `favicon-16/32/180/512.png`, `logo.svg`, `logo-dark.svg`, `logo-mono.svg`, `wordmark-candidate.svg` (a candidate, not adopted) |
| `fonts/` | IBM Plex Sans and Spline Sans Mono, copied from `web/public/fonts` so the screens render offline (OFL) |

Screens: Catalogue + Today, Task (mid-attempt), Task headers with prereqs, Result panel states, Review after a pass, Review across several files (future case), Lineage, Progress (sample data), Settings.
