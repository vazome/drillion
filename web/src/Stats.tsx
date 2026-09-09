import type { CSSProperties, ReactNode } from "react";
import { Card } from "./ds/index.js";
import { tally } from "./strength";

const LABEL: CSSProperties = { fontSize: "var(--fs-label)", fontWeight: 600, letterSpacing: "var(--ls-label)", textTransform: "uppercase", color: "var(--text-muted)", whiteSpace: "nowrap" };
const NUM: CSSProperties = { fontFamily: "var(--font-mono)", fontSize: 20, fontVariantNumeric: "tabular-nums" };

const Cell = ({ value, label }: { value: ReactNode; label: string }) => (
  <div><div style={NUM}>{value}</div><div style={LABEL}>{label}</div></div>
);
const Rule = () => <div style={{ width: 1, background: "var(--border)" }} />;

/** Where you stand in one strip, shared by the catalogue and the progress screen.
 * `practised` and `progressHref` drop out of the strip when they are not passed. */
export function Stats({ boxes, ladder, due, seen, total, practised, outOf, progressHref }: {
  boxes: number[]; ladder: number[]; due: number; seen: number; total: number;
  practised?: number; outOf?: number; progressHref?: string;   // `outOf`, not `window`: that name is the global
}) {
  const known = tally(boxes, ladder);
  return (
    // wraps rather than pushing the page sideways: at 200% zoom the strip is wider than
    // the window, and a horizontal scrollbar under every screen is the wrong answer
    <Card padding="12px 18px" style={{ display: "flex", alignItems: "stretch", flexWrap: "wrap", gap: "10px 22px" }}>
      {practised === undefined ? null : <><Cell label="days practised"
        value={<>{practised} <span style={{ fontSize: 14, color: "var(--text-faint)" }}>of {outOf}</span></>} /><Rule /></>}
      <div><div style={{ ...NUM, color: "var(--accent)" }}>{due}</div><div style={LABEL}>due today</div></div>
      <Rule />
      <Cell value={<>{seen} <span style={{ fontSize: 14, color: "var(--text-faint)" }}>/ {total}</span></>} label="tasks practised" />
      <Rule />
      <div style={{ display: "flex", alignItems: "center", gap: 18, flex: 1 }}>
        {(["learning", "familiar", "solid"] as const).map((k) => (
          <div key={k}>
            <div style={{ ...NUM, fontSize: 15 }}>{known[k]}</div>
            <div style={{ ...LABEL, fontSize: 11 }}>{k}</div>
          </div>
        ))}
        <div style={{ flex: 1 }} />
        {progressHref ? <a href={progressHref} style={{ fontSize: 13, alignSelf: "flex-end", whiteSpace: "nowrap" }}>Your progress →</a> : null}
      </div>
    </Card>
  );
}
