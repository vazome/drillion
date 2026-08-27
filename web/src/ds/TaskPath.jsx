import React from "react";
export function TaskPath({ tier, tags = [], separator = " · ", style }) {
  return (
    <span title={tier + "/" + tags.join(separator)} style={{ fontFamily: "var(--font-mono)", fontSize: "12.5px", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis", ...style }}>
      <span style={{ color: "var(--text-faint)" }}>{tier}/</span>
      <span style={{ color: "var(--text-muted)" }}>{tags.join(separator)}</span>
    </span>
  );
}
