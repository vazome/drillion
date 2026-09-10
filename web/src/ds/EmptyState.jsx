import React from "react";
import s from "./EmptyState.module.css";
export function EmptyState({ message, actionLabel, onAction, actionDisabled = false, align = "center", className, style }) {
  return (
    <div data-align={align} className={[s.root, className].filter(Boolean).join(" ")} style={style}>
      <span className={s.message}>{message}</span>
      {actionLabel ? (
        <button type="button" disabled={actionDisabled} onClick={onAction} className={s.action}>{actionLabel}</button>
      ) : null}
    </div>
  );
}
