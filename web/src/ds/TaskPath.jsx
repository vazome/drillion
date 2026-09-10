import React from "react";
import s from "./TaskPath.module.css";
export function TaskPath({ tier, tags = [], separator = " · ", className, style }) {
  return (
    <span title={tier + "/" + tags.join(separator)} className={[s.root, className].filter(Boolean).join(" ")} style={style}>
      <span className={s.tier}>{tier}/</span>
      <span className={s.tags}>{tags.join(separator)}</span>
    </span>
  );
}
