import React from "react";
import s from "./NoticeBanner.module.css";
export function NoticeBanner({ message, actions = [], className, style }) {
  return (
    <div className={[s.root, className].filter(Boolean).join(" ")} style={style}>
      <span className={s.message}>{message}</span>
      {actions.map((a, i) => (
        <button key={i} type="button" onClick={a.onClick} className={s.action}>{a.label}</button>
      ))}
    </div>
  );
}
