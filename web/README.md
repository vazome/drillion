# web — the frontend

React 19 + TypeScript + Vite. Three hash routes, catalogue, task and progress, plus Settings as a dialog, over `src/api.ts`,
the one `fetch` wrapper and every response shape from `src/drillion/api.py`. The editor is
Monaco, themed from the design tokens in both modes, with completions and diagnostics from a
basedpyright that the API runs locally and serves over `/lsp`.

```bash
pnpm --dir web install          # once
uv run drillion                 # API on 8765 (and it builds web/dist if stale)
pnpm --dir web dev              # Vite on 5173, proxying /api to 8765
pnpm --dir web lint             # runs in CI
pnpm --dir web build            # emits web/dist, which the server serves at /
pnpm --dir web screens          # Playwright: renders all 189 task pages, photographs the rest,
                                # and runs the keyboard/axe pass on Chromium, Firefox and WebKit
```

`web/dist` is generated and git-ignored: `serve()` builds it when it is missing or older than
`src/`, so a fresh clone just works.

Notes:

- `src/ds/` is the drillion design system ("Mineral Blue"), authored in Claude Design and
  vendored here. Treat it as vendored — changes belong upstream. The one exception is
  `SpecText.jsx`, whose regex Markdown parser was replaced with `react-markdown` + `remark-gfm`.
  Run `pnpm screens` after touching it — `e2e/render.spec.ts` renders every task spec.
  `Dialog.jsx` (the Settings modal) and the table roles inside `TopicStrips.jsx` were written
  here and belong upstream too.
- `e2e/a11y.spec.ts` is the accessibility gate: a keyboard-only pass over the loop, the focus
  trap, an axe audit of every screen against WCAG A and AA, and reflow at 200% zoom. It is the
  one spec the Firefox and WebKit projects run; screenshots stay on Chromium so a UI change
  does not churn three sets of captures. `color-contrast` is the single disabled rule, for the
  reason the spec names.
- `pnpm-workspace.yaml` is deliberate: without it a `pnpm-workspace.yaml` further up the tree
  (e.g. in `$HOME`) swallows this package and installs nothing here.
- No Tailwind, no shadcn/ui, no TanStack Query, no react-router — the design system's components
  are plain React over CSS variables, and three hash routes did not need a router.
