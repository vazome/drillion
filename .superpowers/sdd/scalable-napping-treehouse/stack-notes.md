# Stack notes for Task 6 — verified via Context7 on 2026-08-25 (not blog recipes)

## Vite + Tailwind v4 (source: tailwindlabs/tailwindcss.com, shadcn-ui/ui installation/vite.mdx)
- `pnpm add tailwindcss @tailwindcss/vite`; `vite.config.ts`: `plugins: [react(), tailwindcss()]`.
- `src/index.css` starts with `@import "tailwindcss";` — no `@tailwind` directives, no tailwind.config.js.
- Class-based dark mode: `@custom-variant dark (&:where(.dark, .dark *));` right after the import.
- Tokens: `@theme { --color-desk: #EEF1F0; ... }` generates `--color-*` variables and utilities;
  dark overrides live on `.dark { --color-desk: ...; }` (shadcn's `cssVariables: true` convention).

## shadcn/ui on Vite (source: shadcn-ui/ui, fixtures/vite-with-tailwind/components.json + dark-mode/vite.mdx)
- `components.json`: `style: "new-york"`, `rsc: false`, `tsx: true`, `tailwind.css: "src/index.css"`,
  `cssVariables: true`, aliases `@/components`, `@/lib/utils`, `@/components/ui`, `iconLibrary: lucide`.
  Needs `baseUrl`/`paths` `@/* → ./src/*` in tsconfig(.app).json and `resolve.alias` in vite.config.
- `pnpm dlx shadcn@latest init` then `pnpm dlx shadcn@latest add button badge card dialog dropdown-menu
  input select separator table tabs toggle tooltip` (add more only when used).
- Dark mode: the docs' `ThemeProvider` (theme = "dark" | "light" | "system", persisted in
  localStorage under a storageKey, toggles `.dark`/`.light` on `<html>`, follows
  `prefers-color-scheme` for "system") + a `useTheme()` hook; mode toggle = DropdownMenu with
  Light/Dark/System. Copy that component verbatim into `src/components/theme-provider.tsx`.

## Editor: @uiw/react-codemirror (source: uiwjs/react-codemirror core/README + useCodeMirror.ts)
- `<CodeMirror value height theme extensions basicSetup indentWithTab onChange onCreateEditor readOnly />`.
- `indentWithTab` is a prop (default true) — no manual keymap for Tab.
- **Memoise `extensions` and `basicSetup`** (`useMemo`): the hook rebuilds and dispatches
  `StateEffect.reconfigure` whenever those prop references change, so inline arrays/objects
  reconfigure the editor every render.
- Extensions for us: `python()` from `@codemirror/lang-python`, `indentUnit.of("    ")` from
  `@codemirror/language`, `keymap.of([{ key: "Mod-Enter", run: () => { runTests(); return true } }])`
  from `@codemirror/view`, `EditorView.lineWrapping` optional.
- Theme: `createTheme({ theme: "light"|"dark", settings: { background, foreground, caret, selection,
  selectionMatch, lineHighlight, gutterBackground, gutterForeground, gutterActiveForeground,
  gutterBorder, fontFamily }, styles: [{ tag: t.keyword, color }, ...] })` from
  `@uiw/codemirror-themes` with `tags as t` from `@lezer/highlight`. Build one light and one dark
  theme from the design tokens and pick by `useTheme()`; pass as the `theme` prop.
- `readOnly` for the pass-state code view; `onCreateEditor(view)` to keep a ref for focus/`Mod-Enter`.

## Serving (already in web.py pattern; source: Starlette StaticFiles)
- `app.mount("/", StaticFiles(directory=ROOT/"web"/"dist", html=True))` registered last; hash router
  means no SPA fallback route is needed. Vite `base` stays `/`, assets under `/assets/`.

## Markdown guidance renderer (source: remarkjs/react-markdown README + remark-gfm README via Context7)
- `react-markdown` + `remark-gfm` → tables, task lists, footnotes, strikethrough, autolinks. Raw HTML
  is **escaped by default** (no `rehype-raw`) — the READMEs contain none; keep it that way (no XSS
  surface, the content is ours but the rule is free).
- `components` prop overrides elements: `img` → if `src` ends in `.webm/.mp4` render
  `<video autoPlay loop muted playsInline>` else `<img>`; `a` → `target="_blank" rel="noreferrer"`;
  relative `src`/`href` starting with `assets/` are prefixed with `/api/ex/{slug}/`.
- Fenced code: `rehype-highlight` (highlight.js, python grammar) or `code` component override that
  reuses the CodeMirror highlighter for identical colours in both themes — prefer the latter so
  spec examples and the editor look the same.
- GitHub alerts (`> [!NOTE]`) are NOT part of remark-gfm: add `remark-github-blockquote-alert`
  (verify on npm at install time; fallback: a 20-line remark plugin that maps the blockquote's
  first line) and style `.markdown-alert-note/-tip/-warning` from the tokens.
- Mermaid: `code` override for `language-mermaid` that calls `mermaid.render` client-side
  (`mermaid` package, `startOnLoad: false`, theme switched with the app theme); no server render.
- Hints arrive as Markdown strings — same component, no headings expected inside a hint.
