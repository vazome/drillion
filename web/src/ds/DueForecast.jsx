import React from "react";
import s from "./DueForecast.module.css";
import { Tip } from "./Tip.jsx";
/* Due-load forecast — 14 bars, today marked, the cap as a quiet line. */
export function DueForecast({ forecast = [], cap = 12, today, className, style }) {
  const start = new Date((today || new Date().toISOString().slice(0, 10)) + "T00:00:00");
  const dates = forecast.map((_, i) => { const d = new Date(start); d.setDate(d.getDate() + i); return d; });
  const peak = Math.max(cap, ...forecast, 1);
  const H = 118;
  const px = (n) => (n <= 0 ? 0 : Math.max(3, Math.round((n / peak) * H)));
  const total = forecast.reduce((a, b) => a + b, 0);
  const fmt = (d) => d.toLocaleDateString(undefined, { weekday: "short", day: "numeric", month: "short" });
  const aria = total === 0
    ? "Due-load forecast: nothing due in the next fourteen days."
    : "Due-load forecast, " + cap + " reviews a day. " + dates.map((d, i) => fmt(d) + " " + forecast[i]).join(", ") + ".";
  const [tip, setTip] = React.useState(null);
  const show = (e, text) => setTip({ text, x: e.currentTarget.offsetLeft + e.currentTarget.offsetWidth / 2 });

  return (
    <div className={className} style={style}>
      <div role="img" aria-label={aria} className={s.plot} onMouseLeave={() => setTip(null)}>
        {tip ? <Tip text={tip.text} x={tip.x} /> : null}
        <div className={s.bars}>
          {forecast.map((n, i) => {
            const isToday = i === 0;
            const over = Math.max(0, n - cap);
            const base = n - over;
            const text = n + (n === 1 ? " task" : " tasks") + " due " + (isToday ? "today, " : "") + fmt(dates[i]) + (over > 0 ? " · " + over + " over the cap" : "");
            return (
              <div key={i} className={s.bar} title={text} onMouseEnter={(e) => show(e, text)}>
                <div className={s.count} data-today={isToday ? "" : undefined}>{n}</div>
                <div className={s.column} style={{ height: H }}>
                  {over > 0 ? <div className={s.over} style={{ height: px(over) }} /> : null}
                  <div className={s.fill} data-today={isToday && n !== 0 ? "" : undefined} data-zero={n === 0 ? "" : undefined} data-capped={over > 0 ? "" : undefined} style={{ height: n === 0 ? 2 : px(base) }} />
                </div>
              </div>
            );
          })}
        </div>
        <div aria-hidden="true" className={s.capLine} style={{ bottom: px(cap) }} />
        <div aria-hidden="true" className={s.capLabel} style={{ bottom: px(cap) - 8 }}>{cap}/day</div>
      </div>
      <div className={s.axis}>
        {dates.map((d, i) => (
          <div key={i} className={s.axisCell}>
            <div className={s.dayLetter} data-today={i === 0 ? "" : undefined}>{"SMTWTFS"[d.getDay()]}</div>
            <div className={s.dayNum}>{d.getDate()}</div>
          </div>
        ))}
      </div>
      <div className={s.foot}>
        <span className={s.note}>
          {total === 0 ? "Nothing due in the next two weeks. New tasks arrive as you pick them up." : "Today includes everything overdue. A day over the line spills into the next."}
        </span>
        <div className={s.spacer} />
        {total === 0 ? null : <span className={s.total}>{total} tasks over 14 days · {forecast.filter((n) => n > cap).length} days above the cap</span>}
      </div>
    </div>
  );
}
