import React from "react";
export function Button({ variant = "primary", disabled = false, kbdHint, onClick, children, style }) {
  const [hover, setHover] = React.useState(false);
  const base = { fontFamily: "var(--font-sans)", fontSize: "14px", fontWeight: 600, padding: "8px 14px", borderRadius: "var(--radius)", border: "1px solid transparent", display: "inline-flex", alignItems: "center", gap: "8px", whiteSpace: "nowrap", lineHeight: 1.2, cursor: disabled ? "default" : "pointer", transition: "background .12s, border-color .12s" };
  let look;
  if (disabled) look = { background: "var(--surface-2)", color: "var(--text-faint)" };
  else if (variant === "primary") look = { background: hover ? "var(--accent-hover)" : "var(--accent)", color: "var(--on-accent)" };
  else if (variant === "secondary") look = { background: hover ? "var(--surface-2)" : "var(--surface)", color: "var(--text)", borderColor: "var(--border-strong)" };
  else look = { background: "transparent", color: "var(--accent)", padding: "8px 4px", textDecoration: hover ? "underline" : "none" };
  return (
    <button type="button" disabled={disabled} onClick={onClick} onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)} style={{ ...base, ...look, ...style }}>
      {children}
      {kbdHint ? <kbd style={{ opacity: .8 }}>{kbdHint}</kbd> : null}
    </button>
  );
}
