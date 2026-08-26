import type { CSSProperties, ReactNode } from "react";
import { Card } from "./ds/index.js";

const LADDER = [2, 4, 8, 16, 28];   // days between sightings, per box — src/drillion/scheduler.py
const LABEL: CSSProperties = { fontSize: "var(--fs-label)", fontWeight: 600, letterSpacing: "var(--ls-label)", textTransform: "uppercase", color: "var(--text-muted)", whiteSpace: "nowrap" };
const NUM: CSSProperties = { fontFamily: "var(--font-mono)", fontSize: 20, fontVariantNumeric: "tabular-nums" };

const Cell = ({ value, label }: { value: ReactNode; label: string }) => (
  <div><div style={NUM}>{value}</div><div style={LABEL}>{label}</div></div>
);
const Rule = () => <div style={{ width: 1, background: "var(--border)" }} />;

/** The ladder in one strip: what is left, what is due, where the cards sit.
 * Shared by the catalogue and the progress screen; `daysLeft` and `ladderHref`
 * are the catalogue's extras and drop out when they are not passed. */
export function Stats({ boxes, due, seen, total, daysLeft, ladderHref }: {
  boxes: number[]; due: number; seen: number; total: number; daysLeft?: number; ladderHref?: string;
}) {
  return (
    <Card padding="12px 18px" style={{ display: "flex", alignItems: "stretch", gap: 22 }}>
      {daysLeft === undefined ? null : <><Cell value={daysLeft} label="days left" /><Rule /></>}
      <div><div style={{ ...NUM, color: "var(--accent)" }}>{due}</div><div style={LABEL}>due today</div></div>
      <Rule />
      <Cell value={<>{seen} <span style={{ fontSize: 14, color: "var(--text-faint)" }}>/ {total}</span></>} label="cards seen" />
      <Rule />
      <div style={{ display: "flex", alignItems: "center", gap: 18, flex: 1 }}>
        {boxes.map((n, i) => (
          <div key={i}>
            <div style={{ ...NUM, fontSize: 15 }}>{n}</div>
            <div style={{ fontSize: 11, color: "var(--text-faint)", whiteSpace: "nowrap" }}>box {i + 1} · every {LADDER[i]} d</div>
          </div>
        ))}
        <div style={{ flex: 1 }} />
        {ladderHref ? <a href={ladderHref} style={{ fontSize: 13, alignSelf: "flex-end", whiteSpace: "nowrap" }}>The ladder →</a> : null}
      </div>
    </Card>
  );
}
