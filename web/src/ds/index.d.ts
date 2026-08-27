// Prop contracts as authored in the Claude Design project (drillion design system).
// The runtime lives in the sibling .jsx files; TypeScript reads this instead.
import type * as React from "react";

type El = React.ReactElement;
type Style = React.CSSProperties;

/** A verb-labelled action. Primary is reserved for the one main action on a screen (Run tests). */
export interface ButtonProps {
  variant?: "primary" | "secondary" | "quiet";
  disabled?: boolean;
  /** Keyboard hint rendered as a <kbd>, e.g. "Ctrl+Enter" */
  kbdHint?: string;
  onClick?: () => void;
  children?: React.ReactNode;
  style?: Style;
}
export declare function Button(props: ButtonProps): El;

/** White panel on the desk background. Hairline edge via shadow token, no drop shadows. */
export interface CardProps {
  /** Uppercase eyebrow label: "Today", "Spec", "Result", "Hints" */
  label?: React.ReactNode;
  padding?: number | string;
  children?: React.ReactNode;
  style?: Style;
}
export declare function Card(props: CardProps): El;

/** Text input (search, filters). 36px tall, hairline border, accent focus ring. */
export interface InputProps {
  value?: string;
  onChange?: (value: string) => void;
  placeholder?: string;
  /** monospace text (topic numbers, seeds) */
  mono?: boolean;
  /** label when no visible <label> names the field */
  ariaLabel?: string;
  style?: Style;
}
export declare function Input(props: InputProps): El;

/** Keyboard shortcut hint. Styling comes from the global kbd rule. */
export interface KbdProps { children?: React.ReactNode }
export declare function Kbd(props: KbdProps): El;

/** ▸ disclosure row that opens to monospace output. First use: the full pytest output. */
export interface CollapsibleProps {
  label?: React.ReactNode;
  /** right-aligned monospace detail on the row, e.g. "42 lines" */
  meta?: React.ReactNode;
  /** controlled open state; omit to let the component keep its own */
  open?: boolean;
  defaultOpen?: boolean;
  onToggle?: (open: boolean) => void;
  disabled?: boolean;
  /** monospace, never-wrapped body (default); false for prose */
  mono?: boolean;
  children?: React.ReactNode;
  style?: Style;
}
export declare function Collapsible(props: CollapsibleProps): El;

/** A line of copy plus an optional quiet action, for a panel with nothing in it. */
export interface EmptyStateProps {
  message?: React.ReactNode;
  actionLabel?: string;
  onAction?: () => void;
  /** gated action — e.g. nothing new left to pick today */
  actionDisabled?: boolean;
  /** "center" inside a panel (default), "left" inside a column of rows */
  align?: "center" | "left";
  style?: Style;
}
export declare function EmptyState(props: EmptyStateProps): El;

/** 36px dropdown, same shell as Input. Status filter and focus selector. */
export interface SelectOption { value: string; label?: string }
export interface SelectProps {
  value?: string;
  onChange?: (value: string) => void;
  options?: (string | SelectOption)[];
  /** first, empty-valued option — "all statuses", "no focus" */
  placeholder?: string;
  disabled?: boolean;
  mono?: boolean;
  /** label when no visible <label> wraps it */
  ariaLabel?: string;
  style?: Style;
}
export declare function Select(props: SelectProps): El;

/** Two-state switch (role="switch"). The light/dark switch in the header. */
export interface ToggleProps {
  checked?: boolean;
  onChange?: (checked: boolean) => void;
  /** visible text beside the switch — name the state you get, e.g. "Dark" */
  label?: string;
  disabled?: boolean;
  ariaLabel?: string;
  style?: Style;
}
export declare function Toggle(props: ToggleProps): El;

/** Dense list table: 40px rows, hairline separators, sortable header, tabular-nums. */
export interface TableColumn {
  key: string;
  label?: string;
  align?: "left" | "right" | "center";
  mono?: boolean;
  numeric?: boolean;
  muted?: boolean;
  small?: boolean;
  width?: string | number;
  sortable?: boolean;
  render?: (row: any) => React.ReactNode;
}
export interface TableProps {
  columns?: TableColumn[];
  /** `id` keys the row, `disabled: true` dims it and removes hover/click */
  rows?: any[];
  sortKey?: string;
  sortDir?: "asc" | "desc";
  onSort?: (key: string, dir: "asc" | "desc") => void;
  onRowClick?: (row: any) => void;
  emptyMessage?: React.ReactNode;
  style?: Style;
}
export declare function Table(props: TableProps): El;

/** Status / grade pill. Words carry the meaning; colour is never the only signal. */
export interface StatusBadgeProps {
  status?: "new" | "due" | "open" | "done" | "easy" | "medium" | "hard" | "quick" | "pass" | "struggled" | "abandoned";
  /** override label (e.g. "done 6 d") */
  children?: React.ReactNode;
  style?: Style;
}
export declare function StatusBadge(props: StatusBadgeProps): El;

/** Tag chip: filter (interactive, aria-pressed) or row annotation (small, static). */
export interface TagChipProps {
  label: string;
  active?: boolean;
  onClick?: () => void;
  /** 12px static row variant */
  small?: boolean;
  style?: Style;
}
export declare function TagChip(props: TagChipProps): El;

/** Miniature Leitner meter for rows and banners, one cell per rung. box 0 = all empty. */
export interface LadderMeterProps {
  /** which rung to fill, 0–7; 0 is a card that is not on the ladder yet */
  box?: number;
  intervals?: number[];
  style?: Style;
}
export declare function LadderMeter(props: LadderMeterProps): El;

/** Full-size ladder for the Progress page: one box per rung, with counts and return intervals. */
export interface LadderProps {
  /** card count per box, one entry per rung */
  boxes?: number[];
  /** index of the box to outline (most recent pass) */
  highlight?: number;
  intervals?: number[];
  style?: Style;
}
export declare function Ladder(props: LadderProps): El;

/** Active-time display. Muted under par, warn past par, fail past 2× par. */
export interface TimerProps {
  seconds?: number;
  parMinutes?: number;
  paused?: boolean;
  style?: Style;
}
export declare function Timer(props: TimerProps): El;

/** Test-result banner under the editor: idle · running · failed · passed. */
export interface ResultBannerProps {
  state?: "idle" | "running" | "failed" | "passed";
  /** failed: the assertion/exception headline (mono) */
  headline?: string;
  /** failed: full pytest output behind a disclosure */
  output?: string;
  /** passed: "QUICK · 4m12s · 1 attempt · box 3 of 7" */
  gradeLine?: string;
  /** passed: "8 days" */
  backIn?: string;
  style?: Style;
}
export declare function ResultBanner(props: ResultBannerProps): El;

/** One-sentence warning banner (draft restore, gated action) with quiet actions. */
export interface NoticeBannerProps {
  message: React.ReactNode;
  actions?: { label: string; onClick?: () => void }[];
  style?: Style;
}
export declare function NoticeBanner(props: NoticeBannerProps): El;

/** The disk-conflict decision, inline above the editor — a banner, never a modal. */
export interface ConflictBannerProps {
  message?: React.ReactNode;
  /** monospace second line — the path, or when it changed */
  detail?: React.ReactNode;
  reloadLabel?: string;
  keepLabel?: string;
  /** discards the local draft */
  onReload?: () => void;
  /** keeps the draft and dismisses */
  onKeep?: () => void;
  /** both actions disabled while the reload is in flight */
  disabled?: boolean;
  style?: Style;
}
export declare function ConflictBanner(props: ConflictBannerProps): El;

/** Renders a task's spec_md — GitHub-flavoured Markdown: ## sections as accent labels,
 * lists, tables, inline code and links, fenced Python with syntax colours, GitHub alerts. */
export interface SpecTextProps {
  /** the spec Markdown (task README from # title to ## Hints) */
  text?: string;
  /** skip the leading # h1 (the card header already shows the title) */
  hideTitle?: boolean;
  /** resolves relative assets/ links against /api/task/{slug}/assets/ */
  slug?: string;
  style?: Style;
}
export declare function SpecText(props: SpecTextProps): El;

/** Due-load forecast for the Progress page: 14 bars, today marked and labelled, the daily
 *  cap as a dashed line with the over-cap part of a bar hatched — a heavy day is information,
 *  not a warning, so no semantic colour is used. Hovering a bar shows a tooltip; the same
 *  text is on each bar as an aria-label, and the figure carries a spoken summary. */
export interface DueForecastProps {
  /** 14 integers; [0] is today and includes everything overdue, [13] is two weeks out */
  forecast?: number[];
  /** reviews served per day — the line; a day above it spills into the next */
  cap?: number;
  /** "YYYY-MM-DD" for bar [0], so weekday letters land right in any timezone */
  today?: string;
  style?: Style;
}
export declare function DueForecast(props: DueForecastProps): El;

/** Practice heatmap: 53 weeks × 7 days of passes, four intensity steps from `--surface-2`
 *  up through `--accent`. No total, no streak — days practised is a rolling count.
 *  Squares size themselves to fill the card unless `cell` is given. */
export interface PracticeHeatmapProps {
  /** "YYYY-MM-DD" → passes that day; days with none are absent */
  days?: Record<string, number>;
  /** "YYYY-MM-DD" — the grid ends on this day's week */
  today?: string;
  /** fixed square size in px; omitted, the grid measures its card and fills the width */
  cell?: number;
  /** gap between squares, px */
  gap?: number;
  style?: Style;
}
export declare function PracticeHeatmap(props: PracticeHeatmapProps): El;

/** Topic depth: one strip per tag. Strip width is the topic's size, its segments are the
 *  tasks in each ladder box (pale box 1 → accent box 7) followed by the unseen remainder,
 *  with lapses, due-in-7 and seen/total beside it. Sortable — stuck first by default —
 *  and each tag links to the catalogue filtered by that tag. Handles the full tag list
 *  by scrolling inside its card. */
export interface TopicStripsTag {
  tag: string;
  /** tasks carrying the tag */
  total: number;
  /** tasks seen at least once — the strip's coloured part */
  seen: number;
  /** 7 counts: tasks with this tag sitting in each ladder box */
  boxes: number[];
  /** struggles across the tag's tasks */
  lapses: number;
  /** due within the next 7 days, the overdue included */
  due7: number;
}
export interface TopicStripsProps {
  tags?: TopicStripsTag[];
  /** how many ladder boxes a strip is divided into, for the footer legend — seven as the scheduler ships */
  boxes?: number;
  defaultSort?: "stuck first" | "neglected first" | "most lapses" | "a–z";
  /** scroll height of the row list, px */
  maxHeight?: number;
  style?: Style;
}
export declare function TopicStrips(props: TopicStripsProps): El;

/** A nudge for a task that has been open a long while (30 minutes by default): take a hint,
 *  and if that doesn't open it, bury the task and go read the material. A `role="status"`
 *  card, never a modal — it does not block the editor and the × dismisses it for good.
 *  No countdown and no semantic colour: an accent rule, `--shadow-pop` in the corner. */
export interface StuckNudgeProps {
  /** minutes on the task, shown in the label */
  minutes?: number;
  /** hints already taken — sets the button's number and the "n of m shown" aside */
  hintsShown?: number;
  hintsTotal?: number;
  /** false when the next hint is still time-locked; disables the hint button */
  hintReady?: boolean;
  onHint?: () => void;
  onBury?: () => void;
  onDismiss?: () => void;
  /** "corner" — 360px and elevated, for a fixed bottom-right wrapper; "inline" — full width above the task */
  placement?: "corner" | "inline";
  style?: Style;
}
export declare function StuckNudge(props: StuckNudgeProps): El;

/** A group header inside a panel: an uppercase label, an aside that says what the group is.
 *  Every group in the Today panel sits under one, which is why those rows carry no status
 *  badge — the band already said it. `first` drops the separator on the top band. */
export interface BandProps {
  label: string;
  /** the quiet half-sentence beside it — "last 7 days", "paused — catching up" */
  aside?: React.ReactNode;
  /** first band in the panel: no top border, more headroom */
  first?: boolean;
  style?: Style;
}
export declare function Band(props: BandProps): El;

/** The learner's own words about a task: one note, edited in place, autosaved the way the
 *  editor is. Always open — a note you have to click to see is a note you never re-read.
 *  Plain text, no Markdown, no history; emptying the box deletes it. The component owns the
 *  field and the state line, never the saving: pass `dirty` while a save is pending. */
export interface NoteFieldProps {
  value?: string;
  onChange?: (text: string) => void;
  /** label above the field */
  label?: string;
  /** what the state line says when everything is saved */
  hint?: React.ReactNode;
  /** a save is pending — the line reads "unsaved" */
  dirty?: boolean;
  placeholder?: string;
  rows?: number;
  /** accessible name, when the visible label is not enough ("Your note on Counter — top N") */
  ariaLabel?: string;
  style?: Style;
}
export declare function NoteField(props: NoteFieldProps): El;

/** Undo the sort — back to `#` ascending. Sits at the end of the header row, past Status, and
 *  stays put and greyed when there is nothing to undo, so the column it occupies never
 *  changes width. */
export interface SortResetProps {
  /** already at the default sort */
  disabled?: boolean;
  onClick?: () => void;
  title?: string;
  ariaLabel?: string;
  style?: Style;
}
export declare function SortReset(props: SortResetProps): El;

/** A task's tier and tags as one filesystem-style path — `core/f-strings · loops`, the tier
 *  segment muted. One column, not two: the tier is the first segment of every row's path, so
 *  a separate tier column repeated the word. Truncates with an ellipsis and keeps the whole
 *  path in its tooltip. */
export interface TaskPathProps {
  tier: string;
  tags?: string[];
  /** between tags; " · " by default */
  separator?: string;
  style?: Style;
}
export declare function TaskPath(props: TaskPathProps): El;

/** The quiet notes a catalogue row can carry, beside the title: what it waits on, whether it
 *  is put aside today, whether it keeps beating you. Faint text rather than badges — none of
 *  these is the row's status, and a row with three of them must still read as one line.
 *  Renders nothing when there is nothing to say. */
export interface RowFlagsProps {
  /** prereqs not yet passed (`blocked`) — task numbers, or `{topic, title}` for the tooltip */
  needs?: Array<number | { topic: number; title?: string }>;
  /** put aside for today only; the box, the due date and the counts are untouched */
  buried?: boolean;
  /** how many times this task has been failed back down the ladder */
  lapses?: number;
  /** `stats.lapse_limit` — the flag appears at or above it; 0 turns the flag off */
  lapseLimit?: number;
  style?: Style;
}
export declare function RowFlags(props: RowFlagsProps): El | null;
