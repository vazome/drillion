import React from "react";
import s from "./PracticeHeatmap.module.css";
import { Tip } from "./Tip.jsx";
/* Practice heatmap — 53 weeks × 7 days on the heat-0…heat-4 steps (the steps live in the
   module, as [data-heat] on a square). Fixed squares: past its box the year scrolls inside
   it, never the page. */
const heatLevel = (n) => (!n ? 0 : n === 1 ? 1 : n <= 3 ? 2 : n <= 6 ? 3 : 4);

export function PracticeHeatmap({ days = {}, today, className, style, cell = 14, gap = 3 }) {
  const cellSize = cell;
  const iso = (d) => d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
  const end = new Date((today || new Date().toISOString().slice(0, 10)) + "T00:00:00");
  const last = new Date(end); last.setDate(last.getDate() + (6 - end.getDay()));   // fill to the end of this week
  const first = new Date(last); first.setDate(first.getDate() - 53 * 7 + 1);

  const cols = [];
  for (let c = 0; c < 53; c++) {
    const week = [];
    for (let r = 0; r < 7; r++) { const d = new Date(first); d.setDate(d.getDate() + c * 7 + r); week.push(d); }
    cols.push(week);
  }
  const months = [];
  let prev = -1;
  cols.forEach((week, c) => { const m = week[0].getMonth(); if (m !== prev && c < 51) { months.push({ c, m }); prev = m; } });
  // a label spans four columns: a month the year only clips the end of would print over the next
  const labels = months.filter((x, i) => !months[i + 1] || months[i + 1].c - x.c >= 3);
  const MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

  const counts = Object.values(days);
  const practised = counts.filter((n) => n > 0).length;
  const passes = counts.reduce((a, b) => a + b, 0);
  const fmt = (d) => d.toLocaleDateString(undefined, { weekday: "short", day: "numeric", month: "short", year: "numeric" });
  const aria = "Practice over the last year: " + passes + " passes across " + practised + " days.";
  const [tip, setTip] = React.useState(null);
  // the bubble sits outside the scrolling plot, which would clip it above the top row: so it
  // is placed against the root, less however far the year has been scrolled
  const show = (e, text) => {
    const sq = e.currentTarget, plot = sq.offsetParent;
    setTip({ text, x: sq.offsetLeft - plot.scrollLeft + sq.offsetWidth / 2, y: plot.offsetTop + sq.offsetTop });
  };

  return (
    <div className={className ? s.root + " " + className : s.root} style={style}>
      {tip ? <Tip text={tip.text} x={tip.x} y={tip.y} /> : null}
      <div role="img" aria-label={aria} tabIndex={0} className={s.plot} onMouseLeave={() => setTip(null)} onScroll={() => setTip(null)}>
        <div className={s.grid} style={{ "--cols": "repeat(53, " + cellSize + "px)" }}>
          <div className={s.months} style={{ gap: gap + "px" }}>
            {labels.map(({ c, m }) => <div key={c} style={{ gridRow: 1, gridColumn: c + 1 + " / span 4" }}>{MON[m]}</div>)}
          </div>
          <div className={s.cells} style={{ gap: gap + "px", gridTemplateRows: "repeat(7, " + cellSize + "px)", marginTop: gap }}>
            {cols.flatMap((week) => week.map((d) => {
              const future = d > end;
              const n = days[iso(d)] || 0;
              const text = n === 0 ? "No practice on " + fmt(d) : n + (n === 1 ? " pass" : " passes") + " on " + fmt(d);
              return <div key={iso(d)} onMouseEnter={future ? undefined : (e) => show(e, text)}
                className={s.cell} data-heat={heatLevel(n)} data-future={future ? "" : undefined} data-round={cellSize > 14 ? "lg" : undefined}
                style={{ height: cellSize }} />;
            }))}
          </div>
        </div>
      </div>
      <div className={s.foot}>
        <span className={s.scaleLabel}>less</span>
        <div className={s.scale}>
          {[0, 1, 2, 3, 4].map((i) => <div key={i} className={s.swatch} data-heat={i} />)}
        </div>
        <span className={s.scaleLabel}>more</span>
      </div>
    </div>
  );
}
