import React from "react";
export function Band({ label, aside, first = false, style }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: "10px", padding: first ? "14px 0 8px" : "10px 0 6px", borderTop: first ? "none" : "1px solid var(--border)", ...style }}>
      <span style={{ fontSize: "var(--fs-label)", fontWeight: 600, letterSpacing: "var(--ls-label)", textTransform: "uppercase", color: "var(--text-muted)", whiteSpace: "nowrap" }}>{label}</span>
      {aside ? <span style={{ fontSize: "12.5px", color: "var(--text-faint)", whiteSpace: "nowrap" }}>{aside}</span> : null}
    </div>
  );
}
