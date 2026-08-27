import React from "react";
import { Tip } from "./Tip.jsx";
/* Due-load forecast — 14 bars, today marked, the cap as a quiet line. */
export function DueForecast({ forecast = [], cap = 12, today, style }) {
  const start = new Date((today || new Date().toISOString().slice(0, 10)) + "T00:00:00");
  const dates = forecast.map((_, i) => { const d = new Date(start); d.setDate(d.getDate() + i); return d; });
  const peak = Math.max(cap, ...forecast, 1);
  const H = 118;
  const px = (n) => (n <= 0 ? 0 : Math.max(3, Math.round((n / peak) * H)));
  const total = forecast.reduce((a, b) => a + b, 0);
  const fmt = (d) => d.toLocaleDateString(undefined, { weekday: "short", day: "numeric", month: "short" });
  const mono = { fontFamily: "var(--font-mono)", fontVariantNumeric: "tabular-nums" };
  const aria = total === 0
    ? "Due-load forecast: nothing due in the next fourteen days."
    : "Due-load forecast, " + cap + " reviews a day. " + dates.map((d, i) => fmt(d) + " " + forecast[i]).join(", ") + ".";
  const [tip, setTip] = React.useState(null);
  const show = (e, text) => setTip({ text, x: e.currentTarget.offsetLeft + e.currentTarget.offsetWidth / 2 });

  return (
    <div style={style}>
      <div role="img" aria-label={aria} style={{ position: "relative", paddingRight: 54 }} onMouseLeave={() => setTip(null)}>
        {tip ? <Tip text={tip.text} x={tip.x} /> : null}
        <div style={{ display: "flex", alignItems: "flex-end", gap: 6 }}>
          {forecast.map((n, i) => {
            const isToday = i === 0;
            const over = Math.max(0, n - cap);
            const base = n - over;
            const text = n + (n === 1 ? " task" : " tasks") + " due " + (isToday ? "today, " : "") + fmt(dates[i]) + (over > 0 ? " · " + over + " over the cap" : "");
            return (
              <div key={i} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "stretch" }} title={text} onMouseEnter={(e) => show(e, text)}>
                <div style={{ ...mono, height: 17, fontSize: 11.5, textAlign: "center", color: isToday ? "var(--accent)" : "transparent" }}>{n}</div>
                <div style={{ height: H, display: "flex", flexDirection: "column", justifyContent: "flex-end" }}>
                  {over > 0 ? <div style={{ height: px(over), borderRadius: "3px 3px 0 0", border: "1px solid var(--accent-line)", borderBottom: "none", background: "repeating-linear-gradient(135deg, var(--accent-line) 0 2px, transparent 2px 5px)" }} /> : null}
                  <div style={{ height: n === 0 ? 2 : px(base), borderRadius: over > 0 ? 0 : "3px 3px 0 0", background: n === 0 ? "var(--border)" : isToday ? "var(--accent)" : "var(--accent-tint)", boxShadow: n === 0 || isToday ? "none" : "inset 0 0 0 1px var(--accent-line)" }} />
                </div>
              </div>
            );
          })}
        </div>
        <div aria-hidden="true" style={{ position: "absolute", left: 0, right: 54, bottom: px(cap), borderTop: "1px dashed var(--border-strong)" }} />
        <div aria-hidden="true" style={{ ...mono, position: "absolute", right: 0, bottom: px(cap) - 8, fontSize: 11, color: "var(--text-faint)" }}>{cap}/day</div>
      </div>
      <div style={{ display: "flex", gap: 6, paddingRight: 54, marginTop: 6 }}>
        {dates.map((d, i) => (
          <div key={i} style={{ flex: 1, textAlign: "center" }}>
            <div style={{ fontSize: 11, fontWeight: i === 0 ? 600 : 400, color: i === 0 ? "var(--accent)" : "var(--text-muted)" }}>{"SMTWTFS"[d.getDay()]}</div>
            <div style={{ ...mono, fontSize: 10.5, color: "var(--text-faint)" }}>{d.getDate()}</div>
          </div>
        ))}
      </div>
      <div style={{ display: "flex", alignItems: "baseline", gap: 8, marginTop: 12 }}>
        <span style={{ fontSize: 13, color: "var(--text-muted)" }}>
          {total === 0 ? "Nothing due in the next two weeks. New tasks arrive as you pick them up." : "Today includes everything overdue. A day over the line spills into the next."}
        </span>
        <div style={{ flex: 1 }} />
        {total === 0 ? null : <span style={{ ...mono, fontSize: 12.5, color: "var(--text-faint)" }}>{total} tasks over 14 days · {forecast.filter((n) => n > cap).length} days above the cap</span>}
      </div>
    </div>
  );
}
