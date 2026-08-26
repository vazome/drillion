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
A spaced-repetition scheduler decides what comes back when (7-box ladder: 2/4/8/16/28/60/120 days). Hints
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
- `today.review[]` — due reviews, most overdue first, at most 12; `today.due_total` — how many
  are really due, and `today.behind` — true once the backlog is past that cap, when `today.new[]`
  is held empty. Both must be said out loud: "showing 12 of 100 due", "new picks paused while you
  catch up". A cap the page hides reads as "done for today" with ninety cards waiting.
  `today.new[]` — up to 2 new picks;
  `today.recent[]` — every task worked in the last `window` days, newest first, open attempts
  included and leading, and a task whose last act was abandoning it left out; never filtered
  against the other two, since a card worked on Friday and due again today is both things at
  once; `today.done_today` (count); `today.no_new` — null while there are new picks, else the one
  reason there are none (`behind`, `cap`, `prereqs` with the nearest task, `focus`, `done`)
- `stats` — `boxes` (7 counts, one per ladder box), `ladder` (the return intervals, one per box), `due` (the whole backlog, not the capped
  list), `lapse_limit` (the lapse count a task is flagged at), `seen`, `total`, and `practised` of
  `window`: distinct days worked in the last 7, a rolling count rather than a streak
- `focus` — one string or null; it restricts *new* picks and is matched against a task's **tier,
  track and tags alike**. `tags[]`, `tiers[]`, `tracks[]` — the three vocabularies to filter by
- `tasks[]` — per row: `slug`, `topic` (number), `title`, `difficulty`, `tier`, `track?`, `tags[]`,
  `blocked[]` (slugs of prereqs not yet passed; empty once started), `source?`,
  `status` ∈ `new | due | open | done`, `box` (0–6, the ladder has seven), `due` (date),
  `seen` (count), `lapses` (count — at `stats.lapse_limit` the row is flagged as a task that
  keeps beating you: "you have struggled with this four times; the hints or the prereqs may be
  the problem, not you"), `buried` (boolean — put aside for today only).
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

A **buried** card is out of today's queue and nothing else: it keeps its box, its due date and
its counts, and the bury ends by itself tomorrow. Because it can lose nothing, it needs no
confirmation — but it does need the two reverse states. The Today panel's rows each carry a quiet
`Bury`, and a **Buried** band appears under them on any day something is buried, listing what is
put aside with `Unbury` on each row; the band is absent on a day with nothing in it. In the task
list a buried row is annotated in the same muted way the lapse flag is — `buried today` — and
keeps the status it actually has. The task page carries the same control beside `Abandon`: they
are the two ways of not finishing a task today, and only one of them costs the attempt.

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
- `meta` — `topic`, `title`, `difficulty`, `tier`, `track?`, `tags`, `source` (Exercism tasks). No `minutes` — see the vocabulary below.
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
- also `ladder`, `lapses`, `lapse_limit`, `nudge`, `reference`, `buried` — `web/src/api.ts` is the
  field-for-field contract for every payload
- `solution` — `{unlocked, need_attempts, need_secs}`
- `archive[]` — previous passes `{date, grade, code?}` (code shown only when allowed)
- `note` — the learner's own words about this task, `""` when there is none

A **note** is the one thing on the task page the learner wrote. One per task, edited in place,
autosaved the way the editor is (`PUT /api/task/{slug}/note`); no history, no per-attempt
threading, no Markdown. It belongs to the **task** and not to the attempt — a `struggled` grade,
a fresh attempt and an abandon all leave it exactly as it was — so it sits in the spec pane under
the solution and above the archive, in the order you read them: what the task asks, what you told
yourself about it, what you did last time. It is always open rather than behind a disclosure: a
note you have to click to see is a note you never re-read. Emptying the box deletes it, which is
the only way out it needs. Nothing reads notes outside the task they belong to — there is no
evidence yet that anyone wants to.

Layout: two panes (spec left, editor right; resizable). Toolbar above/below the editor: **Run**
(primary), timer (active time), attempts count, seed,
**Hint** (with countdown until the next level; disabled when exhausted), **Solution** (locked
state shows what is still needed), **Abandon**, archive access.

Results panel (below or beside the editor), states:
- idle (never run) · running · **failed** (headline lines — the assertion/exception — plus a
  collapsible full pytest output; line numbers refer to the editor) ·
  **passed**: grade line `QUICK · 4m12s · 1 attempt · box 3 of 7` — elapsed time, never time
  against par — the ladder visibly stepping, the passing code read-only, a way to go to the
  next Today item. A `struggled` pass steps the card *down* a box, so the banner must be able
  to show a fall as well as a climb, and carries `lapses` for the flag at `lapse_limit`.

Other states: hint revealed (levels 1–3 stack up), solution revealed (marks the attempt: "this pass
won't promote"), unsaved-draft dot (autosave every ~1 s; a silent syntax error shows as an amber
dot and surfaces on Run), **conflict banner** (file changed on disk: reload / overwrite),
**draft restore** offer (a newer local draft exists), gated 423 messages ("not yet — 42 s").

### 3. Progress (`#/progress`)

Answers: *where am I on the ladder?*

Data: `GET /api/progress` → `boxes[7]`, `ladder[7]`, `due`, `seen`, `total`, `practised`, `window`,
`per_tag{tag: {seen, total}}`, `log[]` (last 30: `date, slug, grade, attempts, secs, new`).

Elements: the same stats strip, the full-size ladder (7 boxes with counts and next-return
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
has no fifth branch, so a filter offering a fifth matches nothing. **Bury** deliberately does not
widen this: a buried card is still exactly `due`, and `buried` rides alongside as its own boolean.
Anything that genuinely is a fifth state — suspend, which no timer ever ends — has to reopen this
rule on purpose rather than widen it quietly.

Boxes render 1–7 although state stores them 0–6. Hints are "levels". The solution "unlocks".
Showing up is counted as days practised.

## Out of scope

Accounts, sharing, leaderboards, mobile, marketing pages, onboarding flows, an admin/authoring UI
(tasks are authored as files).
