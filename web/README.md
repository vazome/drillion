# web — the frontend (not built yet)

The design brief is `../DESIGN.md`. Planned stack: React 19 + TypeScript + Vite, Tailwind v4 +
shadcn/ui (light/dark via `.dark` class, tokens as CSS variables), TanStack Query, react-router
(hash routes), CodeMirror 6 via `@uiw/react-codemirror`. Verified setup notes:
`../.superpowers/sdd/scalable-napping-treehouse/stack-notes.md`.

Build output goes to `web/dist`, which `uv run study` serves at `/`; the JSON API lives under
`/api/` (see `src/study/api.py`). Dev loop once it exists: `pnpm --dir web dev` with a proxy to
`http://127.0.0.1:8765`.
