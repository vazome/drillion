import React from "react";
import s from "./TagChip.module.css";
export function TagChip({ label, active = false, onClick, small = false, className, style }) {
  const attrs = {
    "data-active": active ? "" : undefined,
    "data-small": small ? "" : undefined,
    className: [s.root, className].filter(Boolean).join(" "),
    style,
  };
  return onClick
    ? <button type="button" aria-pressed={active} onClick={onClick} data-clickable="" {...attrs}>{label}</button>
    : <span {...attrs}>{label}</span>;
}
