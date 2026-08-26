import React from "react";
function fmt(s) { const m = Math.floor(s / 60), r = s % 60; return String(m).padStart(2, "0") + ":" + String(r).padStart(2, "0"); }
export function Timer({ seconds = 0, parMinutes, paused = false, style }) {
  const par = (parMinutes || 0) * 60;
  const color = par && seconds >= par * 2 ? "var(--fail)" : par && seconds >= par ? "var(--warn)" : "var(--text-muted)";
  return (
    <span style={{ fontFamily: "var(--font-mono)", fontVariantNumeric: "tabular-nums", fontSize: "15px", color, ...style }}>
      {paused ? "⏸ " : ""}{fmt(seconds)}{parMinutes ? <span style={{ opacity: .65 }}> / {fmt(par)} par</span> : null}
    </span>
  );
}
