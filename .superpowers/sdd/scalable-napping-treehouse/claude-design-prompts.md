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
