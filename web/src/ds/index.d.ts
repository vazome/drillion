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
  status?: "new" | "due" | "scheduled" | "open" | "done" | "easy" | "pass" | "struggled" | "failed" | "abandoned" | string;
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

/** Miniature 5-cell Leitner meter for rows and banners. box 0 = all empty. */
export interface LadderMeterProps {
  /** current box, 0–5 */
  box?: number;
  intervals?: number[];
  style?: Style;
}
export declare function LadderMeter(props: LadderMeterProps): El;

/** Full-size ladder for the Progress page: 5 boxes with counts and return intervals. */
export interface LadderProps {
  /** card count per box, length 5 */
  boxes?: number[];
  /** index (0–4) of the box to outline (most recent pass) */
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
  /** passed: "EASY · 4m12s · 1 attempt · box 3 of 5" */
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

/** Renders a drill's spec_md — GitHub-flavoured Markdown: ## sections as accent labels,
 * lists, tables, inline code and links, fenced Python with syntax colours, GitHub alerts. */
export interface SpecTextProps {
  /** the spec Markdown (drill README from # title to ## Hints) */
  text?: string;
  /** skip the leading # h1 (the card header already shows the title) */
  hideTitle?: boolean;
  /** resolves relative assets/ links against /api/ex/{slug}/ */
  slug?: string;
  style?: Style;
}
export declare function SpecText(props: SpecTextProps): El;
