# Claude Design — prompts for the study UI

Written against Anthropic's help-center guidance (support.claude.com "Get started with Claude
Design", 2026-08): a prompt should state **Goal, Layout, Content, Audience**; attach context (link
the GitHub repo, screenshots); **start simple, then layer** (layout → interactions → polish);
**mention responsiveness early**; **ask for 2–3 variations**; give specific feedback ("8px", "use
the Card component"), and reference components by name once a system exists.

Setup before prompt 1: create a project, **link the GitHub repo `vazome/study` (branch `main`)**,
attach no design system (we want fresh directions), and paste `DESIGN.md` if the repo link does not
surface it. Do not import the old `design-brief.md` unless you want that direction.

---

## Prompt 0 — create the design system (do this first)

Where: Claude Design → your organization → design system → **Remix** chat (or a new project whose
deliverable is the UI kit, then publish it). Link the GitHub repo `vazome/study` (branch `main`) as
context. There are no brand assets: the system is authored from this brief, and the sample screen
at the end is the "real example" the docs say to include. Two steps: explore, then lock.

### 0a — explore

> **Goal.** Create the design system for "study", a local single-user web app for daily Python
> practice: coding exercises with a spec, a code editor, test results, hints, and a spaced-
> repetition ladder (5 boxes, cards return in 2/4/8/16/28 days). Read `DESIGN.md` in the linked
> repo for the screens, data and states the system must support.
>
> **Audience.** One engineer using it 20–40 minutes a day on a laptop for ~10 weeks. It must feel
> calm, focused and worth returning to — a personal workbench, not a SaaS dashboard and not a
> marketing site.
>
> **Character.** Three words to design to: *quiet, precise, encouraging.* Reference feel:
> Linear's restraint, Exercism's warmth, a good printed runbook's clarity. Anti-references:
> terminal/hacker (black + green/neon), gamified candy, glassmorphism, gradients as decoration.
>
> **Requirements.** Light AND dark themes from day one, dark being a calm deep tone, never pure
> black. Exactly one accent colour; semantic colours for pass / fail / warning that stay
> distinguishable from the accent and from each other in both themes. Two type families: a UI
> sans (variable weight, good at 13–15px) and a monospace for code and for the hand-aligned spec
> text (the spec must render in true monospace; it is never re-flowed). WCAG AA contrast on every
> text/background pair in both themes. 4px spacing base, 8px rhythm, small radii (4–8px), hairline
> borders over shadows.
>
> **Deliverable for this step.** Three candidate directions on one canvas, each shown as a
> component sheet — palette (light + dark swatches with contrast ratios), type scale, primary /
> secondary / quiet buttons, a status badge set (new · due · scheduled · open · done), a tag chip,
> a card, one table row, and a 40px-tall preview of a code editor surface with a few syntax
> colours. One sentence per direction. Do not build screens yet.

### 0b — lock and build the system

> Go with direction **N** [+ merges]. Build the complete design system and publish it.
>
> **Tokens** (name them so they map onto shadcn/ui + Tailwind v4 CSS variables, with values for
> `:root` and `.dark`): background, foreground, card, card-foreground, muted, muted-foreground,
> border, input, ring, primary/primary-foreground (the accent), secondary, destructive, plus
> semantic `success`, `warning`, `info`, and editor tokens: editor-background, editor-gutter,
> editor-line-highlight, editor-selection, editor-caret. Font stacks, type scale (11/12/13/14/16/
> 20/24/32), line heights, weights, spacing scale, radius scale, focus ring.
>
> **Components**, each with all variants and states (default, hover, focus-visible, active,
> disabled, loading where relevant), light and dark: Button (primary, secondary, quiet/ghost,
> destructive; sm/md; with icon), Badge/status pill (new, due, scheduled, open, done, and grades
> EASY / PASS / STRUGGLED / abandoned), Tag chip (selectable, multi-select AND filter), Input +
> search field, Select, Toggle (theme switch), Tooltip, Dialog (used for a "file changed on disk:
> reload / overwrite" conflict), Banner/inline alert (info, warning, error), Tabs, Table
> (dense rows, sortable header), Card, Progress/stat tile, Countdown label ("next hint in 42 s"),
> Timer display (normal → amber past par → red past 2×), Kbd hint (`⌘⏎`), Collapsible (for the
> full test output), Empty state, Skeleton.
>
> **Patterns** specific to this app: the **Ladder** — five slots showing which box a card is in
> and when it returns; three sizes (16px inline for table rows, 28px in a pass banner where it
> animates one step up, full-size on a progress page); the **two-pane workbench** (resizable split,
> spec left / editor right, toolbar + results); the **spec block** (monospace, section labels
> `WHY` / `YOU GET` / `YOU RETURN` / `─── exact rules ───` given a subtle emphasis, nothing else
> restyled); the **results panel** in idle / running / failed (headline lines + collapsible full
> output) / passed (grade line + ladder step) states.
>
> **Editor theme**: a CodeMirror-style theme for light and dark — background, gutter, active line,
> selection, caret, matching bracket, and syntax colours for keyword, string, number, comment,
> function name, variable, operator, type/class. Keep it low-contrast between tokens: it's a
> writing surface, not a rainbow.
>
> **Real example**: finish with the Exercise screen at 1440×900 in the failed state, built only
> from the components above, using the real spec from `exercises/ex_019_counter.py` (the `solve`
> docstring) — light and dark side by side. Then switch **Published** on.

Validate (docs' step 3): open a fresh test project and prompt "Design the catalogue + Today screen
from DESIGN.md" — it should come out on-system without restating any colours or fonts. If it
drifts, Remix the system with the specific fix ("badge text is 11px — make it 12px", "dark card
surface is too close to the background — raise it one step").

---

## Prompt 1 — three directions for the core screen

> **Goal.** Design the web UI for "study": a local, single-user app for daily Python practice.
> A catalogue of ~150 short coding exercises, each with a spec, a code editor, and a test that
> grades the code on fresh random data. A spaced-repetition scheduler (5-box Leitner ladder:
> cards return in 2/4/8/16/28 days) decides what comes back when. Hints unlock with time; the
> solution unlocks after real effort. The repo is linked; read `DESIGN.md` first — it lists the
> three screens, the exact data each screen receives from the API, every state, and the vocabulary.
>
> **Audience.** One person (me): a DevOps engineer learning Python for interviews, 20–40 minutes a
> day on a laptop browser, for ~10 weeks until a fixed date. Not a classroom, not a marketplace.
> It must feel worth coming back to daily; progress on the ladder is the emotional core.
>
> **Layout.** Desktop-first, 1440×900. Start with the **Exercise screen** only: two resizable
> panes — spec on the left (plain, hand-aligned monospace text with `WHY / YOU GET / YOU RETURN /
> exact rules` sections and 2–3 "read first" links), code editor on the right with a toolbar
> (Run as the primary action, an active-time timer that turns amber past par and red past 2×,
> attempts count, Hint with a countdown, Solution locked/unlocked, Abandon) and a results panel
> below the editor.
>
> **Content.** Use real content from the repo: exercise `ex_303_bob` (spec text in
> `exercises/ex_303_bob.py`, the `solve` docstring) with a failed test result showing two assertion
> lines, and a second frame of the same screen in the **passed** state with the grade line
> `PASS · 6m40s · 2 attempts · box 2/5 · back in 4 days` and the ladder visibly stepping up.
>
> **Constraints.** Light AND dark mode both required later — for now design light, but choose a
> palette that has an obvious calm-dark counterpart. Absolutely no hacker/terminal aesthetic: no
> black-with-green, no neon, no "matrix". One accent colour. The editor gets its own themed
> surface. WCAG AA contrast. Real buttons, visible focus. Implementation is React + Tailwind v4 +
> shadcn/ui with CodeMirror 6, so prefer shapes shadcn components can produce.
>
> **Deliverable.** Three distinct directions side by side (e.g. "workbench", "index cards on a
> desk", "editorial/notebook"), each: the Exercise screen in the failed state, one sentence on the
> idea, the palette and type choices. Do not design the other screens yet.

## Prompt 2 — pick one, extend to the other screens

> Go with direction **N** [+ any specific merges: "take the ladder treatment from direction M"].
> Now design the **Catalogue + Today** screen and the **Progress** screen in the same language,
> using the data in `DESIGN.md`: Today panel (due reviews first, then 2 new picks, a focus
> selector), search, multi-select tag chips, status filter, the exercise list with a miniature
> ladder per row, and a stats strip (days left, due today, cards per box). Progress: the full-size
> ladder with counts and return intervals, a per-tag coverage table, the last 30 log entries.
> Use real rows from the repo's `exercises/` (topic numbers, titles, tags). Keep 1440×900.

## Prompt 3 — states and dark mode

> Add the remaining Exercise-screen states from `DESIGN.md`: hint levels 1–3 revealed (they stack),
> solution unlocked (with the note that this pass will not promote), gated message ("not yet —
> 42 s"), unsaved-draft dot, the conflict banner (file changed on disk: reload / overwrite), and
> the draft-restore offer. Then produce the **dark mode** of all three screens: calm dark surfaces
> (not black), same accent, editor theme with syntax colours for keyword / string / number /
> comment / function / variable, AA contrast. Show light and dark of the Exercise screen side by
> side.

## Prompt 4 — tokens and handoff

> Export the design system for implementation with shadcn/ui + Tailwind v4: CSS variables for
> `:root` and `.dark` (background, card, muted, border, primary/accent, success, warning,
> destructive, ring, and the editor surface + gutter + selection + caret), font stacks and the
> type scale, spacing/radius, and the CodeMirror syntax colours for both modes. Name the
> components used per screen (Button variants, Badge for tags/status, Card, Table, Tabs,
> Tooltip, Dialog for the conflict banner, Toggle for the theme). Publish the design system so
> Claude Code can pull it with `/design-sync`.

## Feedback vocabulary that works
"Tighten the toolbar to one row; Run stays the only filled button." · "The ladder must read at
16px height on catalogue rows." · "Spec text is monospace and must not re-flow." · "Timer amber
is too close to the accent — pick a warmer amber." · "Show me two options for the pass banner."
