import React from "react";
import s from "./Button.module.css";
export function Button({ variant = "primary", disabled = false, kbdHint, onClick, children, className, style }) {
  return (
    <button type="button" disabled={disabled} onClick={onClick} data-variant={variant}
      className={[s.root, className].filter(Boolean).join(" ")} style={style}>
      {children}
      {kbdHint ? <kbd className={s.kbd}>{kbdHint}</kbd> : null}
    </button>
  );
}
