import React from "react";
import s from "./Timer.module.css";
function fmt(sec) { const m = Math.floor(sec / 60), r = sec % 60; return String(m).padStart(2, "0") + ":" + String(r).padStart(2, "0"); }
export function Timer({ seconds = 0, parMinutes, paused = false, className, style }) {
  const par = (parMinutes || 0) * 60;
  const over = par && seconds >= par * 2 ? "double" : par && seconds >= par ? "par" : undefined;
  return (
    <span data-over={over} className={[s.root, className].filter(Boolean).join(" ")} style={style}>
      {paused ? "⏸ " : ""}{fmt(seconds)}{parMinutes ? <span className={s.par}> / {fmt(par)} par</span> : null}
    </span>
  );
}
