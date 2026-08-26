import React from "react";
export function NoticeBanner({ message, actions = [], style }) {
  return (
    <div style={{ background: "var(--warn-bg)", borderRadius: "var(--radius)", padding: "10px 14px", display: "flex", alignItems: "center", gap: "16px", fontSize: "14px", color: "var(--text)", ...style }}>
      <span style={{ flex: 1 }}>{message}</span>
      {actions.map((a, i) => (
        <button key={i} type="button" onClick={a.onClick} style={{ background: "transparent", border: "none", padding: "4px", fontFamily: "var(--font-sans)", fontSize: "13px", fontWeight: 600, color: "var(--accent)", cursor: "pointer", whiteSpace: "nowrap" }}>{a.label}</button>
      ))}
    </div>
  );
}
