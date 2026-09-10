import React from "react";
import s from "./StatusBadge.module.css";
export function StatusBadge({ status = "new", children, className, style }) {
  return <span data-status={status} className={[s.root, className].filter(Boolean).join(" ")} style={style}>{children || status}</span>;
}
