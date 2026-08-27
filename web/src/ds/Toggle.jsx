import React from "react";
export function Toggle({ checked = false, onChange, label, disabled = false, ariaLabel, style }) {
  const [hover, setHover] = React.useState(false);
  const [press, setPress] = React.useState(false);
  const on = checked && !disabled;
  return (
    <button type="button" role="switch" aria-checked={!!checked} aria-label={label ? undefined : ariaLabel} disabled={disabled}
      onClick={onChange ? () => onChange(!checked) : undefined}
      onMouseEnter={() => setHover(true)} onMouseLeave={() => { setHover(false); setPress(false); }}
      onPointerDown={() => setPress(true)} onPointerUp={() => setPress(false)}
      style={{ display: "inline-flex", alignItems: "center", gap: "8px", padding: "3px", background: "transparent", border: "none", borderRadius: "var(--radius-sm)", cursor: disabled ? "default" : "pointer", transform: (press && !disabled) ? "translateY(1px)" : "none", transition: "transform var(--dur-press) var(--ease-out)", ...style }}>
      <span aria-hidden="true" style={{ position: "relative", width: "34px", height: "20px", flex: "none", borderRadius: "var(--radius-pill)", boxSizing: "border-box", border: "1px solid " + (on ? "var(--accent)" : "var(--border-strong)"), background: disabled ? "var(--surface-2)" : (on ? (hover ? "var(--accent-hover)" : "var(--accent)") : (hover ? "var(--surface-2)" : "var(--surface)")), transition: "background var(--dur-press) var(--ease-out), border-color var(--dur-press) var(--ease-out)" }}>
        <span style={{ position: "absolute", top: "2px", left: "2px", width: "14px", height: "14px", borderRadius: "var(--radius-pill)", background: disabled ? "var(--text-faint)" : (on ? "var(--on-accent)" : "var(--border-strong)"), transform: checked ? "translateX(14px)" : "none", transition: "transform var(--dur-fast) var(--ease-step)" }}></span>
      </span>
      {label ? <span style={{ fontFamily: "var(--font-sans)", fontSize: "13px", color: disabled ? "var(--text-faint)" : "var(--text-muted)", whiteSpace: "nowrap" }}>{label}</span> : null}
    </button>
  );
}
