import React from "react";
import { Icon } from "./Icon.jsx";
import s from "./NoticeBanner.module.css";
export function NoticeBanner({ message, actions = [], className, style }) {
  return (
    <div className={[s.root, className].filter(Boolean).join(" ")} style={style}>
      <span aria-hidden="true" className={s.icon}><Icon name="Information" size={16} /></span>
      <span className={s.message}>{message}</span>
      {actions.map((a, i) => (
        <button key={i} type="button" onClick={a.onClick} className={s.action}>{a.label}</button>
      ))}
    </div>
  );
}
