# Design handoff — drillion

This file is the brief for designing the web UI: the product, the three screens, the data each
screen has, every state the UI must show, and the hard constraints. It was written before any
visual direction existed and is kept as the contract the UI is measured against.

The direction has since been chosen: the **drillion design system** ("Mineral Blue"), authored in
Claude Design and vendored at `web/src/ds/` — see [`web/README.md`](web/README.md). An earlier
exploration at `.superpowers/sdd/scalable-napping-treehouse/design-brief.md` (light-only, "index
cards on a desk") was not taken.

## Product in one paragraph

A single-user, local web app for practising Python. A catalogue of 171 short tasks, each
with a spec, a code editor, and a test that grades the code on fresh random data.
A spaced-repetition scheduler decides what comes back when (5-box ladder: 2/4/8/16/28 days). Hints
unlock with time; the solution unlocks after real effort. Sessions are 20–40 minutes a day, on a
laptop browser, kept up over months — there is no deadline and no countdown, because a habit is
what carries the practice. The user is one person learning Python — not a classroom, not a
marketplace.

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
- Implementation: React 19 + TypeScript + Vite; the vendored design system's plain components over
  CSS variables (no Tailwind, no shadcn/ui — see `web/README.md` for why). The editor is
  CodeMirror 6 (themeable: background, gutter, selection, caret, syntax colours for
  keyword/string/number/comment/function/variable).

## Screens

### 1. Catalogue + Today (`#/`)

Answers: *what do I do now?*

Data: `GET /api/catalogue` →
- `today.review[]` — due reviews, most overdue first; `today.new[]` — up to 2 new picks;
  `today.recent[]` — every task worked in the last `window` days, newest first, open attempts
  included and leading, and a task whose last act was abandoning it left out; never filtered
  against the other two, since a card worked on Friday and due again today is both things at
  once; `today.done_today` (count)
- `stats` — `boxes` (5 counts, one per ladder box), `due`, `seen`, `total`, and `practised` of
  `window`: distinct days worked in the last 7, a rolling count rather than a streak
- `focus` — one string or null; it restricts *new* picks and is matched against a task's **tier,
  track and tags alike**. `tags[]`, `tiers[]`, `tracks[]` — the three vocabularies to filter by
- `tasks[]` — per row: `slug`, `topic` (number), `title`, `difficulty`, `tier`, `track?`, `tags[]`,
  `prereqs[]` (numbers), `practices[]`, `source?`,
  `status` ∈ `new | due | open | done`, `box` (0–4, the ladder has five), `due` (date),
  `seen` (count).
  **No `minutes`**: par time never leaves the server.

Elements: Today panel (recent activity, then new picks, focus selector), search, filter chips (tier, track,
tag), status filter, the task list (title · difficulty · the `tier/tag` path · status · a miniature
ladder showing which box the card is in), a small stats strip (days practised, due today, cards per box).

One flat table — no tier bands and no collapsing. The tier is the first segment of every row's
path, so a band header repeated the word and added a count, and a list that hides two thirds of
itself is not a catalogue. Every column header sorts, ascending then descending; `#` ascending is
the default, and the reset control (`↺`, past Status, greyed when there is nothing to undo)
restores it. `difficulty` and `status` sort by what the word means, not by the alphabet; ties fall
back to the task number. The tag map shows every tag reachable under the current filter at once, wrapped rather
than scrolled — pick `advanced` and 76 chips become the 11 that are actually under it. A tag
already switched on never drops out, or a filter that matched nothing could not be undone.

Every group in the Today panel sits under a band that names it, and the rows carry no status
badge as a result. Recent activity leads and is always present, empty line and all: coming back mid-week, the way
into what you were last doing beats the queue. The daily cap belongs to new picks alone — recent activity lists as many as the week holds,
because it is the way back into work already started, not a ration of new material.

Tier and tag render as one filesystem-style path, `core/f-strings`, with the tier segment muted —
one column, not two. Whatever `focus` a row is filtered by, the UI must be able to show it: a
filter the screen cannot display is a screen that says "0 of 171" with no way to explain itself.

### 2. Task (`#/task/:slug`)

Answers: *what exactly is asked, and does my code pass?*

Data: `GET /api/task/{slug}` →
- `meta` — `topic`, `title`, `difficulty`, `tier`, `track?`, `tags`, `prereqs`, `practices`,
  `source` (Exercism tasks). No `minutes` — see the vocabulary below.
- `spec_md` — the task's guidance as **GitHub-flavoured Markdown**, ~25–120 lines: `# title`,
  then `## Why` (business context), `## You get`, `## You return`, `## Rules` with worked
  examples, `## Read first` (the links, with notes), and whatever else the task adds
  (`## Introduction`, `## Instructions` on Exercism tasks). Render: headings, lists, tables,
  fenced code with language, GitHub alerts (`> [!NOTE]`, `[!TIP]`, `[!WARNING]`) and images
  from `assets/` (`GET /api/task/{slug}/assets/{name}`). No raw HTML. The spec pane scrolls;
  never truncate it. Mermaid diagrams and `assets/*.webm` are **not** rendered: no task ships
  either, and `web/src/ds/SpecText.jsx` says what to add back if one ever does.
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
  **passed**: grade line `QUICK · 4m12s · 1 attempt · box 3 of 5` — elapsed time, never time
  against par — the ladder visibly stepping up, the passing code read-only, a way to go to the
  next Today item.

Other states: hint revealed (levels 1–3 stack up), solution revealed (marks the attempt: "this pass
won't promote"), unsaved-draft dot (autosave every ~1 s; a silent syntax error shows as an amber
dot and surfaces on Run), **conflict banner** (file changed on disk: reload / overwrite),
**draft restore** offer (a newer local draft exists), gated 423 messages ("not yet — 42 s").

### 3. Progress (`#/progress`)

Answers: *where am I on the ladder?*

Data: `GET /api/progress` → `boxes[5]`, `due`, `seen`, `total`, `practised`, `window`,
`per_tag{tag: {seen, total}}`, `log[]` (last 30: `date, slug, grade, attempts, secs, new`).

Elements: the same stats strip, the full-size ladder (5 boxes with counts and next-return
intervals), a per-tag coverage table, the recent log.

## Vocabulary (use these words)

Every term — task, tier, difficulty, track, tag, card, box, attempt, grade, status, focus — is
defined once in [CONTEXT.md](CONTEXT.md), along with the synonyms to avoid. Use those words on
screen. This brief deliberately keeps no second copy: the copy it used to keep had already grown
two entries the original did not have.

Two entries are UI *constraints* rather than definitions, so they stay here:

**Par time is never shown.** `minutes` is the grader's input and stops at the server, so the
attempt timer counts up and changes no colour at any threshold. Nothing on any screen tells the
learner how long they were supposed to take.

**`status` has exactly four members** — `new` · `due` · `open` · `done`. `_status()` in `api.py`
has no fifth branch, so a filter offering a fifth matches nothing.

Boxes render 1–5 although state stores them 0–4. Hints are "levels". The solution "unlocks".
Showing up is counted as days practised.

## Out of scope

Accounts, sharing, leaderboards, mobile, marketing pages, onboarding flows, an admin/authoring UI
(tasks are authored as files).
