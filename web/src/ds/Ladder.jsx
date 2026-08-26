import React from "react";
export function Ladder({ boxes = [0, 0, 0, 0, 0, 0, 0], highlight = -1, intervals = [2, 4, 8, 16, 28, 60, 120], style }) {
  return (
    <div style={{ display: "flex", gap: "8px", ...style }}>
      {boxes.map((n, i) => (
        <div key={i} style={{ flex: 1, background: "var(--surface-2)", border: "1px solid " + (i === highlight ? "var(--accent-line)" : "var(--border)"), borderRadius: "var(--radius)", padding: "10px 12px" }}>
          <div style={{ fontSize: "11px", fontWeight: 600, letterSpacing: ".06em", textTransform: "uppercase", color: "var(--text-muted)" }}>box {i + 1}</div>
          <div style={{ fontFamily: "var(--font-mono)", fontSize: "15px", margin: "4px 0 2px", color: "var(--text)" }}>{n} {n === 1 ? "card" : "cards"}</div>
          <div style={{ fontSize: "11px", color: "var(--text-faint)" }}>every {intervals[i]} d</div>
        </div>
      ))}
    </div>
  );
}
