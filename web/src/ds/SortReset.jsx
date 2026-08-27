import React from "react";
export function SortReset({ disabled = false, onClick, title = "Reset sort", ariaLabel = "Reset sort to task number, ascending", style }) {
  const [hover, setHover] = React.useState(false);
  return (
    <button type="button" onClick={onClick} disabled={disabled} title={title} aria-label={ariaLabel}
      onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)}
      style={{ width: "28px", height: "24px", display: "inline-flex", alignItems: "center", justifyContent: "center", flexShrink: 0, background: (hover && !disabled) ? "var(--surface-2)" : "transparent", border: "none", borderRadius: "var(--radius-sm)", fontSize: "15px", lineHeight: 1, color: disabled ? "var(--border-strong)" : hover ? "var(--text)" : "var(--text-muted)", cursor: disabled ? "default" : "pointer", transition: "background-color var(--dur-press) var(--ease-out), color var(--dur-press) var(--ease-out)", ...style }}>
      <span aria-hidden="true">↺</span>
    </button>
  );
}
