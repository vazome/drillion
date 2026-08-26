# web — the frontend

React 19 + TypeScript + Vite. The visual language is the **drillion design system** ("Mineral Blue"),
authored in Claude Design and vendored here under `src/ds/`.

## Layout

| path | what it is |
|---|---|
| `src/ds/` | the design system, as authored: 17 components (`.jsx`) + `index.d.ts` (their prop contracts) + `tokens/*.css`. Treat as vendored — changes belong upstream in the Claude Design project. |
| `src/ds/SpecText.jsx` | the one exception: the design's regex Markdown parser was replaced with `react-markdown` + `remark-gfm`. Same styling, real parser (see the comment in the file). |
| `src/api.ts` | every response shape from `src/drillion/api.py`, and the one `fetch` wrapper |
| `src/App.tsx` | hash router, theme, header |
| `src/Catalogue.tsx`, `src/Task.tsx`, `src/Progress.tsx` | the three screens |
| `src/Editor.tsx` | CodeMirror 6, themed from the design tokens in both modes |

## Dev loop

```bash
uv run drillion                 # API on 8765 (and it builds web/dist if stale)
pnpm --dir web dev              # Vite on 5173, proxying /api to 8765
```

`pnpm build` emits `web/dist`, which `uv run drillion` serves at `/`. `web/dist` is generated and
git-ignored: `serve()` builds it when it is missing or older than `src/`, so a fresh clone just works.

## Check

```bash
pnpm --dir web check 8765       # renders all 171 task specs through SpecText
```

Asserts no GitHub-alert marker leaks as literal text, every `## ` heading becomes an `<h2>`, and
lists stay lists. Run it against a live server after touching `SpecText.jsx`.

## Notes

- `pnpm-workspace.yaml` is deliberate: without it a `pnpm-workspace.yaml` further up the tree
  (e.g. in `$HOME`) swallows this package and installs nothing here.
- No Tailwind, no shadcn/ui, no TanStack Query, no react-router — the design system's components
  are plain React over CSS variables, and three hash routes did not need a router. See the
  frontend note in the SDD ledger.
