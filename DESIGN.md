# Design handoff — drillion

This file is the brief for designing the web UI. It describes the product, the three screens, the
data each screen has, every state the UI must show, and the hard constraints. **No visual direction
has been decided** — palette, type, layout language and components are open. An earlier
exploration exists at `.superpowers/sdd/scalable-napping-treehouse/design-brief.md` (light-only,
"index cards on a desk"); treat it as one candidate, not a constraint.

## Product in one paragraph

A single-user, local web app for practising Python. A catalogue of ~100–180 short tasks, each
with a spec, a code editor, and a test that grades the code on fresh random data.
A spaced-repetition scheduler decides what comes back when (5-box ladder: 2/4/8/16/28 days). Hints
unlock with time; the solution unlocks after real effort. Sessions are 20–40 minutes a day, on a
laptop browser, until a fixed deadline (an interview date). The user is one person who is learning
Python for DevOps interviews — not a classroom, not a marketplace.

The feel to aim for: a focused workbench like HackerRank/Exercism's problem page, but calmer and
more personal — it should be **engaging to come back to daily**. Progress on the ladder is the
emotional core: cards climbing boxes and returning on schedule.

## Hard constraints

- **Light and dark modes**, system default, one-click toggle; the code editor is themed in both.
- **No hacker/terminal aesthetic**: no black background with green or neon text, no "matrix" look.
  Dark mode is a calm dark, not pure black.
- Desktop-first (≥1280 px); tablet-friendly is a bonus; mobile is out of scope.
- Accessible: real buttons, visible focus, WCAG AA contrast in both modes, keyboard: `Mod-Enter`
  runs tests.
- Implementation target: React + Tailwind v4 + shadcn/ui, tokens as CSS variables on `:root` and
  `.dark`. The editor is CodeMirror 6 (themeable: background, gutter, selection, caret, syntax
  colours for keyword/string/number/comment/function/variable).

## Screens

### 1. Catalogue + Today (`#/`)

Answers: *what do I do now?*

Data: `GET /api/catalogue` →
- `today.review[]` — due reviews, most overdue first; `today.new[]` — up to 2 new picks;
  `today.done_today` (count)
- `stats` — `boxes` (5 counts, one per ladder box), `due`, `seen`, `total`, `days_left` to the deadline
- `focus` — a tag or null (restricts *new* picks to a track), `tags[]` — all tags
- `tasks[]` — per row: `topic` (number), `title`, `tags[]`, `prereqs[]`,
  `status` ∈ `new | due | scheduled | open | done`, `box` (0–5), `due` (date), `seen` (count)

Elements: Today panel (reviews, then new picks, focus selector), search, tag chips (multi-select
AND), status filter, the task list (topic · title · tags · status · a miniature ladder
showing which box the card is in), a small stats strip (days left, due today, cards per box).

### 2. Task (`#/task/:slug`)

Answers: *what exactly is asked, and does my code pass?*

Data: `GET /api/task/{slug}` →
- `meta` — `topic`, `title`, `tags`, `prereqs`, `practices`, `source` (Exercism tasks)
- `spec_md` — the task's guidance as **GitHub-flavoured Markdown**, ~25–120 lines: `# title`,
  then `## Why` (business context), `## You get`, `## You return`, `## Rules` with worked
  examples, `## Read first` (the links, with notes), and whatever else the task adds
  (`## Introduction`, `## Instructions` on Exercism tasks). Render: headings, lists, tables,
  fenced code with language, GitHub alerts (`> [!NOTE]`, `[!TIP]`, `[!WARNING]`), ```mermaid
  diagrams, images from `assets/` (`GET /api/task/{slug}/assets/{name}`), and `![…](assets/x.webm)`
  as a muted looping video. No raw HTML. The spec pane scrolls; never truncate it.
- `code` — the editor text (a stub, or the user's draft); `has_given` — true when the region
  contains given code above `solve()` that must not be edited (show a note)
- `attempt` — null, or `{attempts, hints, active (seconds), seed, solution_shown}`
- `hints` — `{total: 3, shown[]: Markdown already revealed, next_in: seconds}`, rendered the same
  way as the spec
- `solution` — `{unlocked, need_attempts, need_secs}`
- `archive[]` — previous passes `{date, grade, code?}` (code shown only when allowed)

Layout: two panes (spec left, editor right; resizable). Toolbar above/below the editor: **Run**
(primary), timer (active time), attempts count, seed,
**Hint** (with countdown until the next level; disabled when exhausted), **Solution** (locked
state shows what is still needed), **Abandon**, archive access.

Results panel (below or beside the editor), states:
- idle (never run) · running · **failed** (headline lines — the assertion/exception — plus a
  collapsible full pytest output; line numbers refer to the editor) ·
  **passed**: grade line `QUICK · 4m12s · 1 attempt · box 3/5 · back in 8 days`, the ladder
  visibly stepping up, the passing code read-only, a way to go to the next Today item.

Other states: hint revealed (levels 1–3 stack up), solution revealed (marks the attempt: "this pass
won't promote"), unsaved-draft dot (autosave every ~1 s; a silent syntax error shows as an amber
dot and surfaces on Run), **conflict banner** (file changed on disk: reload / overwrite),
**draft restore** offer (a newer local draft exists), gated 423 messages ("not yet — 42 s").

### 3. Progress (`#/progress`)

Answers: *where am I on the ladder?*

Data: `GET /api/progress` → `boxes[5]`, `due`, `seen`, `total`, `per_tag{tag: {seen, total}}`,
`log[]` (last 30: `date, slug, grade, attempts, secs, new`).

Elements: the full-size ladder (5 boxes with counts and next-return intervals), a per-tag coverage
table, the recent log, days-left to the deadline.

## Grades and vocabulary (use these words)

`QUICK` (first try, under par) · `PASS` · `STRUGGLED` · `abandoned`. Boxes 1–5. "Due", "new",
"scheduled" (returns on a date), "open" (an attempt is in progress). Hints are "levels". The
solution "unlocks". The deadline is shown as days left.

## Out of scope

Accounts, sharing, leaderboards, mobile, marketing pages, onboarding flows, an admin/authoring UI
(tasks are authored as files).
