import React from "react";
export function EmptyState({ message, actionLabel, onAction, actionDisabled = false, align = "center", style }) {
  const [hover, setHover] = React.useState(false);
  return (
    <div style={{ display: "grid", gap: "10px", justifyItems: align === "left" ? "start" : "center", textAlign: align === "left" ? "left" : "center", padding: "var(--space-6) var(--space-4)", ...style }}>
      <span style={{ fontFamily: "var(--font-sans)", fontSize: "14px", lineHeight: "var(--lh-body)", color: "var(--text-muted)", maxWidth: "52ch", textWrap: "pretty" }}>{message}</span>
      {actionLabel ? (
        <button type="button" disabled={actionDisabled} onClick={onAction}
          onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)}
          style={{ background: "transparent", border: "none", borderRadius: "var(--radius-sm)", padding: "4px 6px", fontFamily: "var(--font-sans)", fontSize: "13px", fontWeight: 600, color: actionDisabled ? "var(--text-faint)" : "var(--accent)", textDecoration: (hover && !actionDisabled) ? "underline" : "none", cursor: actionDisabled ? "default" : "pointer" }}>{actionLabel}</button>
      ) : null}
    </div>
  );
}
