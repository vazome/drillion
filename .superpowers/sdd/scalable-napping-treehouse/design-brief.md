# Design brief — Study (Python drills workbench)

Single user, daily 20–40 min sessions, Windows browser (Chrome/Edge) opened from WSL. Not a marketing
page: a workbench. Every screen answers one question — catalogue: *what do I do now?*; exercise:
*what exactly is asked, and does my code pass?*; progress: *where am I on the ladder?*

**Hard constraints (from Daniel):** calm and professional; **no hacker/terminal aesthetic — no black
background, no green-on-black, no neon**; one accent colour; the editor theme matches the palette.

## Concept — "index cards on a desk"

The scheduler is a Leitner system: literally index cards in five boxes that come back in 2 / 4 / 8 /
16 / 28 days. The UI borrows that world quietly: white cards (panels) on a cool mineral-grey desk,
DIN-style labels like a printed runbook, monospace for the hand-aligned specs. The one memorable
element is **the ladder**: five slots showing which box a card sits in and when it returns. It
appears small on every catalogue row, in the pass banner (the card visibly steps up one slot), and
full-size on the progress page. It is information, not decoration.

Avoided on purpose: cream paper + serif + terracotta; near-black + acid accent; newspaper hairlines
with zero radius. Nothing here should read as a template or a terminal.

## Tokens (copy into `:root`)

```css
:root {
  /* surfaces */
  --desk:        #EEF1F0;   /* page background — cool mineral grey */
  --card:        #FFFFFF;   /* panels */
  --card-2:      #F7F8F7;   /* secondary panel / table header */
  --editor:      #FBFBFA;   /* CodeMirror background */
  --gutter:      #F1F3F2;   /* CodeMirror gutter */
  --rule:        #D8DEDB;   /* borders */
  --rule-strong: #BFC7C3;   /* emphasised borders, input borders */

  /* ink */
  --ink:         #1B2320;   /* primary text */
  --ink-2:       #4C5653;   /* secondary text */
  --ink-3:       #7A8481;   /* muted text, placeholders, timestamps */

  /* the one accent: plum */
  --accent:      #5A3E9C;   /* buttons, links, active chip, focus ring, ladder highlight */
  --accent-hover:#4A3283;
  --accent-tint: #EEE9F8;   /* chip backgrounds, selected row */
  --accent-line: #C9BDE8;   /* accent borders */

  /* semantic (small areas only: result banner, status pills, timer) */
  --pass:        #2F7A63;  --pass-bg: #E3F1EA;
  --fail:        #B03A2E;  --fail-bg: #F8E6E3;
  --warn:        #B7791F;  --warn-bg: #FBF0DA;

  /* type */
  --font-label: Bahnschrift, "DIN Alternate", "Roboto Condensed", "Segoe UI", system-ui, sans-serif;
  --font-body:  "Segoe UI", system-ui, -apple-system, "Helvetica Neue", Arial, sans-serif;
  --font-mono:  "Cascadia Mono", "Cascadia Code", Consolas, "JetBrains Mono", ui-monospace, Menlo, monospace;

  /* scale */
  --fs-title: 22px;  --fs-h: 17px;  --fs-body: 15px;  --fs-small: 13px;  --fs-label: 12px;
  --fs-spec: 13.5px; --fs-code: 14px;
  --lh-body: 1.5;    --lh-spec: 1.6;  --lh-code: 1.55;
  --radius: 6px;     --radius-pill: 999px;
  --space: 8px;      /* all spacing is a multiple of 8px: 8 / 16 / 20 / 24 / 32 */
  --shadow: 0 1px 2px rgba(27, 35, 32, .06), 0 0 0 1px var(--rule);   /* card edge */
  --focus: 0 0 0 2px var(--card), 0 0 0 4px var(--accent);           /* visible focus ring */
}
```

Text contrast: `--ink` on `--card` 15.9:1; `--ink-2` 7.6:1; `--ink-3` 4.6:1 (muted only, ≥13px);
`--accent` on white 7.6:1; white on `--accent` 7.6:1; `--pass`/`--fail`/`--warn` on their `-bg`
tints ≥ 4.8:1. Never put accent text on the accent tint smaller than 13px.

## Typography

- **Labels / eyebrows / headings** — `--font-label` (Bahnschrift). Eyebrows: 12px, uppercase,
  letter-spacing .08em, weight 600, colour `--ink-3` ("TODAY", "SPEC", "RESULT", "HINTS").
  Page title: 22px, weight 600, `--ink`, no uppercase. Section heading: 17px/600.
- **Body / UI** — `--font-body` (Segoe UI), 15px/1.5, weight 400; buttons 14px/600.
- **Code and specs** — `--font-mono`. Spec `<pre>`: 13.5px/1.6, `white-space: pre-wrap`,
  `max-width: 74ch`, colour `--ink`; the `─── exact rules ───` line and `WHY:` / `YOU GET:` /
  `YOU RETURN:` openers are styled by a tiny post-process in JS: wrap the three openers in
  `<b class="spec-key">` (weight 600, colour `--accent`) — nothing else is transformed.
  Editor: 14px/1.55. Numbers in tables (topic, minutes, attempts, timer): mono with
  `font-variant-numeric: tabular-nums`.

## Components

- **Button** — primary (Run tests): `--accent` bg, white text, 14px/600, 8px 14px padding, radius
  6px, hover `--accent-hover`, focus `--focus`. Secondary: white bg, `--rule-strong` border,
  `--ink` text. Quiet (hint/solution/discard): no border, `--accent` text, underline on hover.
  Disabled: `--card-2` bg, `--ink-3` text, no hover. Every button is a `<button>` with a verb label.
- **Chip** (tag filter) — pill, 13px, `--card-2` bg, `--rule` border, `--ink-2` text; active:
  `--accent-tint` bg, `--accent-line` border, `--accent` text. Tags on rows use the same chip at
  12px without hover.
- **Status pill** — 12px label font, uppercase: `new` (`--card-2`/`--ink-2`), `due`
  (`--accent-tint`/`--accent`), `open` (`--warn-bg`/`--warn`), `done` (`--pass-bg`/`--pass`,
  shown with the ladder meter and "back in N d").
- **Ladder meter** (signature, small) — five cells 7×11px, gap 2px, radius 2px; cells up to the
  current box are `--accent`, the rest `--rule`. Tooltip/`title`: "box 3 of 5 — every 8 days".
  On new cards all cells are `--rule`.
- **Ladder** (signature, large, progress page) — five slots as tall rounded rectangles on
  `--card-2`, each with the box number (label font, 12px), the interval ("every 8 days"), and the
  count of cards as a stack of thin white lines (one line per card, max 30 drawn, then "+N").
  The slot with the most recent pass is outlined in `--accent-line`.
- **Result banner** — full width under the editor. Fail: `--fail-bg` with a 3px left border
  `--fail`, headline lines in mono 13.5px, "Show full output" disclosure (`<details>`). Pass:
  `--pass-bg`/`--pass` with the grade line in label font ("PASSED · EASY · 4m12s · 1 attempt")
  and the meter animating one cell (250 ms, `prefers-reduced-motion` → none).
- **Timer** — mono, tabular, 15px: `04:12` then muted `/ 10:00 par`. Colour `--ink-2`; from par
  `--warn`; from 2× par `--fail`. Paused while the tab is hidden (shows `⏸`).
- **Inputs** (search) — white, `--rule-strong` border, radius 6px, 36px tall, focus ring.
- **Banner** (409 / draft found / offline editor) — `--warn-bg`, one sentence, two quiet
  buttons ("Reload from disk" / "Keep mine"; "Restore draft" / "Discard draft").
- **Cards/panels** — white, `--shadow`, radius 6px, padding 20px. No gradients, no drop
  shadows beyond the 1px edge.

## Layouts

Page frame: header 56px, `--desk` background, content padding 24px, no max-width (it's a
workbench), except text columns (spec ≤ 74ch, progress ≤ 960px).

**Header (all pages):** left — wordmark "Study" in label font 17px/600 + muted "87 drills";
centre — nothing; right — `Focus: all ▾` (select), "Catalogue" / "Progress" links, and the quiet
countdown "68 days to Nov 2" (`--ink-3`, tabular).

### Catalogue + Today (`#/`)
```
┌ Study · 87 drills                          Focus: [all ▾]   Catalogue   Progress   68 days to Nov 2 ┐
│                                                                                                      │
│  TODAY                                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────────────────────────────┐    │
│  │ due   ▮▮▯▯▯   9   sorted with key=                          10 min   core · rsample   [Open] │    │
│  │ new   ▯▯▯▯▯   1   f-strings — aligned report columns        10 min   core            [Open] │    │
│  │ new   ▯▯▯▯▯   2   slicing — combine start, stop, step       10 min   core            [Open] │    │
│  └──────────────────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                                      │
│  ALL DRILLS                                                                                          │
│  [ search title or topic…              ]   status: (all) new due open done                           │
│  core  data-structures  files-text  stdlib-ops  errors  http  concurrency  testing  cloud  llm  …    │
│  ┌──────────────────────────────────────────────────────────────────────────────────────────────┐    │
│  │   1   f-strings — aligned report columns          10 m   core                      new       │    │
│  │   2   slicing — combine start, stop, step         10 m   core                      new       │    │
│  │   9   sorted with key=                            10 m   core · rsample      ▮▮▯▯▯  due       │    │
│  │  19   Counter — top N by frequency                12 m   data-structures    ▮▮▮▯▯  done 6 d  │    │
│  └──────────────────────────────────────────────────────────────────────────────────────────────┘    │
```
Row: 44px tall, topic number right-aligned mono `--ink-3`, title `--ink` 15px, minutes mono,
tag chips, meter + status pill at the right edge. Whole row is a link; hover `--card-2`.
Empty Today: "Nothing due. Pick anything below, or rest — that's training too." Focus with
nothing new left: "Focus `rsample` has nothing new left. [Clear focus]".

### Exercise (`#/ex/<slug>`) — the screen that matters
```
┌ ‹ Catalogue     19 · Counter — top N by frequency     data-structures · rsample         68 days to Nov 2 ┐
│                                                                                                          │
│ ┌ SPEC ───────────────────────────────┐ ┌ [ Run tests  Ctrl+Enter ]   04:12 / 12:00 par   attempt 1   seed 4357 ┐ │
│ │ WHY: A team lead asks "which        │ │                                                                     │ │
│ │ services are crashing the most?"    │ │  1  def solve(lines, n):                                            │ │
│ │ …                                   │ │  2      raise NotImplementedError                                   │ │
│ │                                     │ │  3                                                                  │ │
│ │ YOU GET: `lines` — …                │ │                                                                     │ │
│ │ YOU RETURN: …                       │ │                                                                     │ │
│ │                                     │ │                                                                     │ │
│ │ ─── exact rules ───                 │ │                                                                     │ │
│ │ …                                   │ └─────────────────────────────────────────────────────────────────────┘ │
│ │                                     │  ● unsaved                                Discard attempt · Archive     │
│ │ READ FIRST                          │ ┌ RESULT ─────────────────────────────────────────────────────────────┐ │
│ │ • realpython.com/…                  │ │ ✗  NotImplementedError                                   attempt 1  │ │
│ │ • docs.python.org/…                 │ │ ▸ Show full output                                                  │ │
│ │ TAKE-HOME: `sorted(rows, key=score)`│ └─────────────────────────────────────────────────────────────────────┘ │
│ │                                     │                                                                         │
│ │ HINTS                               │                                                                         │
│ │ [ Show hint 1 ]  Hint 2 in 42 s     │                                                                         │
│ │ Solution: locked — 2 more attempts, │                                                                         │
│ │ 6 more minutes                      │                                                                         │
│ └─────────────────────────────────────┘                                                                         │
```
Grid: `grid-template-columns: minmax(360px, 42%) 1fr; gap: 24px`. Under 900px the columns stack
(spec first). Left card scrolls independently; the editor column is sticky-top. Editor min-height
320px, grows with content up to 60vh then scrolls. The given-code note (when `has_given`) sits
above the editor in `--ink-3` 13px: "Code above `solve()` is given — keep helpers inside `solve()`."
Revealed hints render as quiet cards under the buttons, in body font. The pass state replaces
the RESULT card content: "PASSED · EASY · 4m12s · 1 attempt", the meter stepping up, "back in 8
days", then the passing code read-only (editor becomes read-only with `--card-2` background) and
a primary "Back to Today".

### Progress (`#/progress`)
```
┌ Study …                                                                 68 days to Nov 2 ┐
│  THE LADDER                                                                              │
│  ┌ box 1 ┐ ┌ box 2 ┐ ┌ box 3 ┐ ┌ box 4 ┐ ┌ box 5 ┐      due now  3      started 21 / 87  │
│  │ ≡≡≡≡  │ │ ≡≡    │ │ ≡     │ │       │ │       │                                          │
│  │ every │ │ every │ │ every │ │ every │ │ every │                                          │
│  │ 2 d   │ │ 4 d   │ │ 8 d   │ │ 16 d  │ │ 28 d  │                                          │
│  └───────┘ └───────┘ └───────┘ └───────┘ └───────┘                                          │
│  BY TAG                       seen / total                                                 │
│  core             ▮▮▮▮▮▮▮▯▯▯▯▯▯▯▯▯▯   7 / 17                                                │
│  data-structures  ▮▮▯▯▯▯▯▯            2 / 8                                                 │
│  RECENT                                                                                    │
│  2026-08-25  ex_019_counter   PASS       2 attempts   6m40s                                 │
└────────────────────────────────────────────────────────────────────────────────────────────┘
```

## CodeMirror theme (light, matches the tokens)

```
.cm-editor            background --editor; color --ink; font --font-mono 14px/1.55; border 1px --rule; radius 6px
.cm-gutters           background --gutter; color --ink-3; border-right 1px --rule
.cm-activeLine        background #F3F1FA        (plum tint)
.cm-activeLineGutter  background #ECE9F5
.cm-selectionBackground, ::selection   #E4E1F3
.cm-cursor            border-left 2px --accent
.cm-matchingBracket   text-decoration underline; text-decoration-color --accent
&.cm-focused          outline none; box-shadow --focus (on .cm-editor)
HighlightStyle:
  keyword               #5A3E9C  (accent)          weight 600
  definition(name), function(name)   #1B2320       weight 600
  string, special(string)            #8A5A1A
  number, bool, null                 #2A6F8F
  comment, meta                      #7A8481  italic
  operator, punctuation              #4C5653
  variableName, propertyName         #1B2320
  className, typeName                #3D2C6E
```
Read-only (after pass): `.cm-editor` background `--card-2`, cursor hidden.

## Copy (verbs, sentence case, one job per element)

- Buttons: "Run tests" (with `Ctrl+Enter` shown as a kbd hint), "Open", "Show hint 1", "Hint 2 in
  42 s" (disabled), "Show solution — won't count as a pass", "Discard attempt", "Back to Today",
  "Clear focus", "Reload from disk", "Keep mine", "Restore draft", "Discard draft".
- States: "Solution unlocks after 3 attempts and 10 minutes (you're at 1 and 4 min)."; "Nothing
  due. Pick anything below, or rest — that's training too."; "Saved" / "Unsaved" dot;
  "Editor couldn't load (offline?) — using a plain text box. Run still works."; 
  "This file changed on disk (VS Code?)." with the two buttons.
- Errors say what happened and what to do: "Line 3: unexpected indent — fix it and run again."
- Pass line format: `PASSED · EASY · 4m12s · 1 attempt · box 3 of 5 · back in 8 days`.

## Motion

Only three: result card fades in (150 ms); the ladder meter steps one cell on pass (250 ms
ease-out); hint cards expand (150 ms). `@media (prefers-reduced-motion: reduce)` disables all.

## Quality floor

Responsive to 720px (stacked exercise page); all interactive elements keyboard-reachable with
the `--focus` ring; `aria-live="polite"` on the result card so a screen reader hears the verdict;
tag chips are `<button aria-pressed>`; colour never the only signal (pills carry words; the
meter has a `title`). No images, no icon fonts — the few glyphs (✓ ✗ ▸ ●) are text.
