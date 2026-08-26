# Claude Design — prompts for the drillion UI

Written against Anthropic's help-center guidance (support.claude.com "Get started with Claude
Design", 2026-08): a prompt should state **Goal, Layout, Content, Audience**; attach context (link
the GitHub repo, screenshots); **start simple, then layer** (layout → interactions → polish);
**mention responsiveness early**; **ask for 2–3 variations**; give specific feedback ("8px", "use
the Card component"), and reference components by name once a system exists.

The design system already exists: it was built with an earlier set of prompts, now deleted. The
system itself is the record of them, and re-running them would start over. Everything below is
written for a system that is already attached.

---

# Project prompts — design system attached

**Setup.** New project in Claude Design (a *project*, not a design system) → attach the existing
design system → link the GitHub repo **`vazome/drillion`**, branch `main`.

**The product is called drillion**, lowercase always. The repo has been renamed — package,
console script, env vars, `DESIGN.md` and `README.md` all say drillion now. The **design system
has not**: it is still titled "Study Design System", its `readme.md` opens "Design system for
**study**", and — the one that shows up on screen — its brand guidelines define the wordmark as
`"study"`. Run Prompt 0R below before Prompt A, or every screen the project draws puts the wrong
word in its header.

**Two rules for every prompt in this project.** Never restate a colour, a font, a radius or a
spacing value — if the output drifts, that is a bug in the system and gets fixed by remixing the
system, not by patching the prompt. Always name components: "use `Card` with an eyebrow",
"`StatusBadge`, not a new pill".

**Known gaps.** The system has 12 components; these screens need shapes it does not define —
a dense sortable **table** (catalogue rows, per-tag coverage), a **collapsible** (full pytest
output), a **select** (status filter, focus), a **toggle** (theme), a **dialog** or reuse of
`NoticeBanner` (file changed on disk), an **empty state** ("nothing due"). The project will
invent these and they will drift from the system. Either accept that and fold the good ones back
in later, or add them to the system first with a Remix prompt before starting the project.

## Prompt 0R — remix the existing system (do this before Prompt A)

Do **not** re-run Prompt 0; the system exists. This is a Remix of it, and it is short.

> Two changes to this design system.
>
> **1. The product is called drillion, not "study".** Lowercase always — "drillion", never
> "Drillion", exactly the way "study" was written. Rename the system to "drillion design system".
> In `readme.md`, replace every "study" with "drillion" and change the source link to
> `https://github.com/vazome/drillion`. In the brand guidelines, the wordmark is **"drillion"**
> set in IBM Plex Sans semibold, lowercase — same treatment, new word. Nothing else about the
> visual language changes.
>
> The components themselves carry no namespace — they are plain ES modules. The global
> `window.StudyDesignSystem_e20cf4` is defined in the compiled `_ds_bundle.js` and destructured by
> one line in each preview card (`core.card.html`, `feedback.card.html`, `spec.card.html`,
> `status.card.html`). Whichever way the rename takes it, the bundle and those four lines must
> agree — if the global becomes `DrillionDesignSystem_e20cf4`, update the cards to match; if it
> stays as it is, leave the cards alone. A half-renamed global breaks every preview.
>
> **2. Add the six components the screens need and the system does not have.** Build each in the
> existing language — current tokens, current spacing, light and dark, with default / hover /
> focus-visible / disabled states, and a preview card alongside the others:
>
> - **Table** — dense rows, hairline separators, sortable header, tabular-nums for numeric
>   columns. Used for the catalogue list (topic · title · tags · minutes · status · a 16px
>   `LadderMeter`) and the per-tag coverage table on Progress.
> - **Collapsible** — a ▸ disclosure row that opens to monospace output. Used for the full pytest
>   output under a failure headline; collapsed by default.
> - **Select** — 36px, matching `Input`. Used for the status filter (new · due · scheduled · open
>   · done) and the focus selector.
> - **Toggle** — the light/dark switch, sitting in the header.
> - **Conflict dialog** — "This drill changed on disk." with **Reload from disk** and **Keep
>   mine**. Build it as a `NoticeBanner` variant if that reads better than a modal; say which you
>   chose and why.
> - **EmptyState** — a line of copy plus an optional quiet action. First use: "Nothing due. Pick
>   anything below, or rest — that's training too."
>
> Keep the existing 12 components untouched. Republish when done.

## Prompt A — the Exercise screen, failed state

> **Goal.** Design the Exercise screen (`#/ex/:slug`) of **Drillion** using the attached design system.
> This is the screen the user spends 20–40 minutes a day inside, so it comes first. Read
> `DESIGN.md` in the linked repo, section "2. Exercise", for the exact data, layout and states.
>
> **Audience.** One engineer, laptop browser, 1440×900. Desktop-first; ≥1280px must work, mobile
> is out of scope.
>
> **Layout.** Two resizable panes. Left: the spec, rendered from GitHub-flavoured Markdown —
> headings, lists, fenced Python, a pipe table, a `> [!WARNING]` alert. It scrolls and is never
> truncated. Right: the code editor with a toolbar — **Run** as the only filled button, the
> active-time timer, attempts count, seed, **Hint** with its countdown, **Solution** in its locked
> state, **Abandon**. Results panel below the editor.
>
> **Content.** Use a real drill from the repo: `exercises/303_bob/README.md` for the spec and
> `exercises/303_bob/drill.py` for the editor contents. Show the **failed** state: two assertion
> headline lines plus a collapsed "full output" row.
>
> **On-system.** Build from the attached components — `Card`, `Button` (primary/secondary/quiet),
> `StatusBadge`, `TagChip`, `Timer`, `LadderMeter`, `SpecText`, `ResultBanner`, `Kbd` for `⌘⏎`.
> Do not introduce new colours, fonts or spacing. Where you need a shape the system lacks
> (collapsible, table), build it from the existing tokens and tell me you did.
>
> **Deliverable.** One screen, light mode, at 1440×900. Then two variations of the **toolbar and
> results arrangement only** — same visual language, different ergonomics.

## Prompt B — the other two screens

> Take arrangement **N**. Now design **Catalogue + Today** (`#/`) and **Progress** (`#/progress`)
> in the same language, per `DESIGN.md` sections 1 and 3.
>
> Catalogue: the Today panel (due reviews first, then up to two new picks, a focus selector),
> search, multi-select tag chips (AND), a status filter across `new · due · scheduled · open ·
> done`, the exercise list — topic · title · tags · minutes · status · a 16px `LadderMeter` per
> row — and the stats strip (days left, due today, cards per box). Use real rows from the repo's
> `exercises/`: real topic numbers, titles and tags, not lorem.
>
> Progress: the full-size `Ladder` with counts and return intervals, the per-tag coverage table,
> the last 30 log lines.
>
> Include the empty Today state: "Nothing due. Pick anything below, or rest — that's training
> too." Keep 1440×900, light mode.

## Prompt C — the remaining states, then dark

> Add the Exercise-screen states from `DESIGN.md` that are still missing: hint levels 1–3 revealed
> and stacked; solution revealed with the note that this pass will not promote; the gated message
> ("not yet — 42 s"); the unsaved-draft amber dot; the conflict banner (file changed on disk —
> reload / keep mine); the draft-restore offer; and the **passed** state with the grade line
> `EASY · 4m12s · 1 attempt · box 3 of 5 · back in 8 days`, the ladder stepping one cell, and the
> passing code read-only.
>
> Then produce **dark mode** for all three screens using the system's `.dark` tokens — including
> the editor surface and its syntax colours. Show the Exercise screen light and dark side by side.

## Prompt D — handoff to Claude Code

> For each screen, list the components used and the props each one needs, and name anything you
> built that is not in the design system. Export the screens so they can be read from the repo.

Then, in Claude Code: `/design-sync` to pull the system down, and build `web/` against it — Vite +
React 19 + TypeScript, Tailwind v4 with the system's tokens as CSS variables, CodeMirror 6 via
`@uiw/react-codemirror`, TanStack Query, hash routes. `task-6-brief.md` is **stale** — it specifies
vanilla JS with no build step and must be rewritten before anyone works from it.

## Checking the system holds

Open a throwaway project, attach the system, and prompt "design the catalogue + Today screen from
DESIGN.md". It should come out on-system without you restating a single colour or font. If it
drifts, fix the **system** with a Remix naming the specific defect — "badge text is 11px, make it
12px", "the dark card surface is too close to the background, raise it one step" — never by
patching the project prompt.

## Feedback vocabulary that works
"Tighten the toolbar to one row; Run stays the only filled button." · "The ladder must read at
16px height on catalogue rows." · "Spec text is monospace and must not re-flow." · "Timer amber
is too close to the accent — pick a warmer amber." · "Show me two options for the pass banner."
