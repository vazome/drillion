# Design handover — Progress page visualisations

> Built. The design chose the third topic shape — one strip per tag — and the three
> components live in `web/src/ds/` as `DueForecast`, `PracticeHeatmap` and `TopicStrips`.
> The brief below is kept as the record of what was asked.

Three components for `#/progress`, to be drawn in Claude Design and vendored into
`web/src/ds/` like the rest of the Mineral Blue system. This file is everything the designer
needs; [`DESIGN.md`](../../DESIGN.md) is the product brief behind it and
[`CONTEXT.md`](../../CONTEXT.md) the vocabulary.

## What exists

- The design system: `web/src/ds/` — plain React components over CSS custom properties, no
  Tailwind, no chart library. Tokens in `web/src/ds/tokens/*.css` (colours for light and dark,
  IBM Plex Sans / Spline Sans Mono, spacing, motion). `Ladder.jsx` is the closest relative of
  what is asked for here: a row of boxes, an uppercase 11px label, a mono number, a faint
  caption.
- The page today (`web/src/Progress.tsx`), 1180px wide, a grid of cards with 18px gaps:
  1. the stats strip — days practised, due today, cards seen, one cell per ladder box
  2. **The ladder** — seven boxes with counts and their return intervals
  3. a two-column row: **Coverage by tag** (a sortable table, 360–420px wide, 76 tags,
     scrolls inside its card) beside **Last 30 sessions** (a log table)
- Card idiom: `<Card label="…">` draws the uppercase label; numbers are mono with
  `tabular-nums`; muted text is `--text-muted`, captions `--text-faint`; the accent is
  `--accent` and its tint `--accent-tint`; semantic colours are `--pass`, `--warn`, `--fail`
  with matching `-bg` tints.

## Hard constraints

- Both themes from the tokens; no colour that exists only in one.
- No new dependency. SVG or a CSS grid, drawn by hand; the data is small (14 bars, 371 days,
  76 rows).
- Calm. This is not a dashboard. No streak, no "longest run", no "don't break the chain" —
  `CONTEXT.md` forbids streaks on purpose; days practised is a rolling count.
- No deadline language. drillion has no countdown; a heavy day ahead is information, not a
  warning.
- Desktop-first at 1180px content width; it may stack, it need not shrink to a phone.
- Accessible: every cell readable without colour (a `title`, and a text alternative or an
  `aria-label` on the whole figure), focus visible where anything is interactive.
- `prefers-reduced-motion`: any reveal collapses to nothing.
- Deliverable per component: one `.jsx` in the `ds/` idiom (named export, props below,
  inline styles over the CSS variables), one line for `ds/index.d.ts`, and any new tokens
  added to `tokens/*.css`. Agents integrate; they do not draw.

## 1. Due-load forecast

**Question it answers:** *what is coming?* On a fixed ladder the future is exact — every card
has a due date — so this is a count, not an estimate.

**Props**

```ts
forecast: number[]   // 14 integers; [0] is today and includes everything overdue, [13] is two weeks out
cap: number          // reviews drillion serves per day, currently 12; a day above it spills into the next
```

**Shape:** a strip of 14 bars in a card, today marked, the cap as a quiet line so a day above
it reads as "this will spill over" without a warning colour. Weekday letters or day-of-month
under the bars; the count on hover and, for today, in the open.

**States:** every bar zero (fresh install): the card still renders, with one line of muted
copy. One very tall bar (a backlog): the axis scales, the others stay legible.

**Where:** below **The ladder**, full width, before the two-column row.

## 2. Practice heatmap

**Question it answers:** *have I been here?* Intensity per calendar day over the last year.

**Props**

```ts
days: Record<string, number>   // "YYYY-MM-DD" → passes that day; days with none are absent
today: string                  // "YYYY-MM-DD", so the grid ends on the right day in any timezone
```

**Shape:** the GitHub grid — 53 columns of 7, month labels above, a four-step intensity scale
from `--surface-2` up through the accent tint. A cell's `title` is the date and the count. A
legend: "less … more". No total, no streak, no longest anything.

**States:** a learner one week in has seven cells and 364 empty ones — the empty grid must
look intentional, not broken. Dark mode: the intensity steps must stay distinct on
`--surface`.

**Where:** below the forecast, full width. Together the two say "what's behind, what's ahead".

## 3. Topic heatmap

**Question it answers:** *which topics are deep, which are neglected, which are stuck?*
Coverage by tag is one number per tag. This is the second axis.

The visual is **open** — the developer does not know how it should look and wants the design
to decide. Below is the data that can be computed per tag, all from `progress.json` and task
metadata, and three shapes to weigh.

**Props**

```ts
tags: Array<{
  tag: string
  total: number         // tasks carrying the tag
  seen: number          // tasks seen at least once
  boxes: number[]       // 7 counts: tasks with this tag sitting in each ladder box (unseen tasks are in none)
  lapses: number        // times a card with this tag was graded struggled, summed across the tag's tasks; never resets
  due7: number          // due within the next 7 days, overdue included
}>
ladder: number[]        // the seven return intervals, for labelling boxes
```

76 tags; the long tail has one or two tasks each. Whatever the shape, it must handle 76 rows
— scroll inside the card like the coverage table, or rank and fold.

**Shapes to weigh**

- *Tags × ladder boxes.* Rows are tags, seven columns are boxes, intensity is the count. Reads
  as depth: a topic whose mass sits in boxes 6–7 is learned, one stuck in 1–2 is not. The most
  literal use of what the ladder already means.
- *Tags × recency.* Rows are tags, columns are the last N weeks, intensity is passes. Reads as
  attention: a topic that has gone quiet stands out as a run of empty cells.
- *One strip per tag.* A single row per tag with its box distribution as a tiny stacked bar,
  lapses as a mark, `due7` as a number. Compact, sortable, closer to a table than a heatmap.

Whichever wins, the sort matters more than the colour: neglected-first or stuck-first is the
useful default, and the tag name is a link to the catalogue filtered by that tag
(`#/?tag=…` does not exist yet; the integration will add it).

**Where:** replaces or sits beside **Coverage by tag**. If it replaces it, seen/total per tag
must survive somewhere in the new component.

## Data the API will send

`GET /api/progress` gains `forecast`, `cap`, `days`, `today`, and `per_tag` grows the fields
above. Nothing the page shows today is removed. The shapes are fixed so the design can be
built against real numbers; a `progress.json` with a year of history is available on request
for the mock.
