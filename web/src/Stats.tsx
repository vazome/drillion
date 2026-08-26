import type { CSSProperties, ReactNode } from "react";
import { Card } from "./ds/index.js";

const LABEL: CSSProperties = { fontSize: "var(--fs-label)", fontWeight: 600, letterSpacing: "var(--ls-label)", textTransform: "uppercase", color: "var(--text-muted)", whiteSpace: "nowrap" };
const NUM: CSSProperties = { fontFamily: "var(--font-mono)", fontSize: 20, fontVariantNumeric: "tabular-nums" };

const Cell = ({ value, label }: { value: ReactNode; label: string }) => (
  <div><div style={NUM}>{value}</div><div style={LABEL}>{label}</div></div>
);
const Rule = () => <div style={{ width: 1, background: "var(--border)" }} />;

/** The ladder in one strip, shared by the catalogue and the progress screen.
 * `practised` and `ladderHref` drop out of the strip when they are not passed. */
export function Stats({ boxes, ladder, due, seen, total, practised, outOf, ladderHref }: {
  boxes: number[]; ladder: number[]; due: number; seen: number; total: number;
  practised?: number; outOf?: number; ladderHref?: string;   // `outOf`, not `window`: that name is the global
}) {
  return (
    <Card padding="12px 18px" style={{ display: "flex", alignItems: "stretch", gap: 22 }}>
      {practised === undefined ? null : <><Cell label="days practised"
        value={<>{practised} <span style={{ fontSize: 14, color: "var(--text-faint)" }}>of {outOf}</span></>} /><Rule /></>}
      <div><div style={{ ...NUM, color: "var(--accent)" }}>{due}</div><div style={LABEL}>due today</div></div>
      <Rule />
      <Cell value={<>{seen} <span style={{ fontSize: 14, color: "var(--text-faint)" }}>/ {total}</span></>} label="cards seen" />
      <Rule />
      <div style={{ display: "flex", alignItems: "center", gap: 18, flex: 1 }}>
        {boxes.map((n, i) => (
          <div key={i}>
            <div style={{ ...NUM, fontSize: 15 }}>{n}</div>
            <div style={{ fontSize: 11, color: "var(--text-faint)", whiteSpace: "nowrap" }}>box {i + 1} · every {ladder[i]} d</div>
          </div>
        ))}
        <div style={{ flex: 1 }} />
        {ladderHref ? <a href={ladderHref} style={{ fontSize: 13, alignSelf: "flex-end", whiteSpace: "nowrap" }}>The ladder →</a> : null}
      </div>
    </Card>
  );
}
