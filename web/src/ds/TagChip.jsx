import React from "react";
export function TagChip({ label, active = false, onClick, small = false, style }) {
  const [hover, setHover] = React.useState(false);
  const s = { fontSize: small ? "12px" : "12.5px", padding: small ? "2px 9px" : "4px 11px", borderRadius: "var(--radius-pill)", whiteSpace: "nowrap", fontFamily: "var(--font-sans)", cursor: onClick ? "pointer" : "default",
    background: active ? "var(--accent-tint)" : hover && onClick ? "var(--surface-2)" : small ? "transparent" : "var(--surface-2)",
    border: active ? "1px solid var(--accent-line)" : "1px solid var(--border)",
    color: active ? "var(--accent)" : "var(--text-muted)", fontWeight: active ? 600 : 400, ...style };
  return onClick
    ? <button type="button" aria-pressed={active} onClick={onClick} onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)} style={s}>{label}</button>
    : <span style={s}>{label}</span>;
}
