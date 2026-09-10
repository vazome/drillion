import React from "react";
import s from "./Band.module.css";
export function Band({ label, aside, first = false, className, style }) {
  return (
    <div data-first={first ? "" : undefined} className={[s.root, className].filter(Boolean).join(" ")} style={style}>
      <span className={s.label}>{label}</span>
      {aside ? <span className={s.aside}>{aside}</span> : null}
    </div>
  );
}
