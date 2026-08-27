import React from "react";
/* Practice heatmap — 53 weeks × 7 days, four intensity steps off the accent. */
const HEAT = ["var(--surface-2)", "var(--accent-tint)", "color-mix(in srgb, var(--accent) 45%, var(--surface))", "var(--accent)"];
const heatLevel = (n) => (!n ? 0 : n <= 3 ? 1 : n <= 8 ? 2 : 3);

export function PracticeHeatmap({ days = {}, today, style, cell, gap = 4 }) {
  /* No `cell` given: measure the card and size the squares to fill its width. */
  const box = React.useRef(null);
  const [auto, setAuto] = React.useState(cell || 11);
  React.useEffect(() => {
    if (cell || !box.current || typeof ResizeObserver === "undefined") return;
    const ro = new ResizeObserver(([e]) => {
      const w = e.contentRect.width - 28 - 52 * gap;   // 20px weekday column + 8px gutter
      setAuto(Math.max(8, Math.floor(w / 53)));
    });
    ro.observe(box.current);
    return () => ro.disconnect();
  }, [cell, gap]);
  const size = cell || auto;
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
  const MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

  const counts = Object.entries(days).filter(([d]) => d >= iso(first) && d <= iso(end)).map(([, n]) => n);
  const practised = counts.filter((n) => n > 0).length;
  const passes = counts.reduce((a, b) => a + b, 0);
  const fmt = (d) => d.toLocaleDateString(undefined, { weekday: "short", day: "numeric", month: "short", year: "numeric" });
  const aria = "Practice over the last year: " + passes + " passes across " + practised + " days.";
  const track = { display: "grid", gridTemplateColumns: "repeat(53, minmax(0, 1fr))", gap: gap + "px" };
  const [tip, setTip] = React.useState(null);
  const show = (e, text) => setTip({ text, x: e.currentTarget.offsetLeft + e.currentTarget.offsetWidth / 2, y: e.currentTarget.offsetTop });
  /* Keep the bubble inside the card: clamp its centre once it has measured itself. */
  const clamp = (el) => {
    if (!el || !tip) return;
    const w = el.offsetWidth / 2 + 2;
    const room = (el.offsetParent || el.parentElement).clientWidth;
    el.style.left = Math.min(Math.max(tip.x, w), Math.max(w, room - w)) + "px";
  };

  return (
    <div style={style} ref={box}>
      <div role="img" aria-label={aria} style={{ display: "flex", gap: 8, position: "relative" }} onMouseLeave={() => setTip(null)}>
        {tip ? <div ref={clamp} style={{ position: "absolute", left: tip.x, top: tip.y - 8, transform: "translate(-50%, -100%)", pointerEvents: "none", zIndex: 2, whiteSpace: "nowrap", fontSize: 12.5, padding: "5px 9px", borderRadius: "var(--radius-sm)", background: "var(--text)", color: "var(--bg)", boxShadow: "0 2px 8px rgba(0,0,0,.18)" }}>{tip.text}</div> : null}
        <div style={{ display: "grid", gridTemplateRows: "14px repeat(7, " + size + "px)", gap: gap + "px", fontSize: 10, color: "var(--text-faint)", width: 20, justifyItems: "end", alignItems: "center" }}>
          <div /><div /><div>M</div><div /><div>W</div><div /><div>F</div><div />
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ ...track, height: 14, fontSize: 10, color: "var(--text-faint)", overflow: "hidden" }}>
            {months.map(({ c, m }) => <div key={c} style={{ gridRow: 1, gridColumn: c + 1 + " / span 4" }}>{MON[m]}</div>)}
          </div>
          <div style={{ ...track, gridTemplateRows: "repeat(7, " + size + "px)", gridAutoFlow: "column", marginTop: gap }}>
            {cols.flatMap((week) => week.map((d) => {
              const future = d > end;
              const n = days[iso(d)] || 0;
              const text = n === 0 ? "No practice on " + fmt(d) : n + (n === 1 ? " pass" : " passes") + " on " + fmt(d);
              return <div key={iso(d)} aria-label={future ? undefined : text} onMouseEnter={future ? undefined : (e) => show(e, text)}
                style={{ height: size, borderRadius: size > 14 ? 3 : 2, visibility: future ? "hidden" : "visible", background: HEAT[heatLevel(n)], boxShadow: n === 0 ? "none" : "inset 0 0 0 1px var(--accent-line)" }} />;
            }))}
          </div>
        </div>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 12 }}>
        <span style={{ fontSize: 13, color: "var(--text-muted)" }}>
          {passes === 0 ? "No passes yet. Every square fills in as you practise." : practised + (practised === 1 ? " day" : " days") + " with a pass in the last year"}
        </span>
        <div style={{ flex: 1 }} />
        <span style={{ fontSize: 11, color: "var(--text-faint)" }}>less</span>
        <div style={{ display: "flex", gap: 3 }}>
          {HEAT.map((c, i) => <div key={i} style={{ width: 12, height: 12, borderRadius: 2, background: c, boxShadow: i === 0 ? "none" : "inset 0 0 0 1px var(--accent-line)" }} />)}
        </div>
        <span style={{ fontSize: 11, color: "var(--text-faint)" }}>more</span>
      </div>
    </div>
  );
}
