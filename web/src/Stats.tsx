import type { ReactNode } from "react";
import { Card } from "./ds/index.js";
import { tally } from "./strength";
import s from "./Stats.module.css";

const Cell = ({ value, label }: { value: ReactNode; label: string }) => (
  <div><div className={s.num}>{value}</div><div className={s.label}>{label}</div></div>
);
const Rule = () => <div className={s.rule} />;

/** Where you stand in one strip, shared by the catalogue and the progress screen.
 * `practised` and `progressHref` drop out of the strip when they are not passed. */
export function Stats({ boxes, ladder, due, seen, total, practised, outOf, progressHref }: {
  boxes: number[]; ladder: number[]; due: number; seen: number; total: number;
  practised?: number; outOf?: number; progressHref?: string;   // `outOf`, not `window`: that name is the global
}) {
  const known = tally(boxes, ladder);
  return (
    <Card padding="12px 18px" className={s.strip}>
      {practised === undefined ? null : <><Cell label="days practised"
        value={<>{practised} <span className={s.of}>of {outOf}</span></>} /><Rule /></>}
      <div><div className={s.num} data-accent="">{due}</div><div className={s.label}>due today</div></div>
      <Rule />
      <Cell value={<>{seen} <span className={s.of}>/ {total}</span></>} label="tasks practised" />
      <Rule />
      <div className={s.known}>
        {(["learning", "familiar", "solid"] as const).map((k) => (
          <div key={k}>
            <div className={s.num}>{known[k]}</div>
            <div className={s.label}>{k}</div>
          </div>
        ))}
        <div className={s.spacer} />
        {progressHref ? <a href={progressHref} className={s.more}>Your progress →</a> : null}
      </div>
    </Card>
  );
}
