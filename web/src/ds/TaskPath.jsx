import React from "react";
import s from "./TaskPath.module.css";
export function TaskPath({ tier, track, tags = [], separator = " · ", className, style }) {
  const path = tier || track;
  return (
    <span title={(path ? path + "/" : "") + tags.join(separator)} className={[s.root, className].filter(Boolean).join(" ")} style={style}>
      {path ? <span className={s.tier}>{path}/</span> : null}
      <span className={s.tags}>{tags.join(separator)}</span>
    </span>
  );
}
