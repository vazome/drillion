import React from "react";
import { Icon } from "./Icon.jsx";
import s from "./SortReset.module.css";
export function SortReset({ disabled = false, onClick, title = "Reset sort", ariaLabel = "Reset sort to task number, ascending", className, style }) {
  return (
    <button type="button" onClick={onClick} disabled={disabled} title={title} aria-label={ariaLabel}
      className={[s.root, className].filter(Boolean).join(" ")} style={style}>
      <Icon name="Reset" size={16} />
    </button>
  );
}
