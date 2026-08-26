import React from "react";
const ringToggle = (e) => { try { return e.target.matches(":focus-visible"); } catch { return true; } };
export function Toggle({ checked = false, onChange, label, disabled = false, ariaLabel, style }) {
  const [focus, setFocus] = React.useState(false);
  const [hover, setHover] = React.useState(false);
  const on = checked && !disabled;
  return (
    <button type="button" role="switch" aria-checked={!!checked} aria-label={label ? undefined : ariaLabel} disabled={disabled}
      onClick={onChange ? () => onChange(!checked) : undefined}
      onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)}
      onFocus={(e) => setFocus(ringToggle(e))} onBlur={() => setFocus(false)}
      style={{ display: "inline-flex", alignItems: "center", gap: "8px", padding: "3px", background: "transparent", border: "none", borderRadius: "var(--radius-sm)", cursor: disabled ? "default" : "pointer", boxShadow: focus ? "var(--focus-ring)" : "none", ...style }}>
      <span aria-hidden="true" style={{ position: "relative", width: "34px", height: "20px", flex: "none", borderRadius: "var(--radius-pill)", boxSizing: "border-box", border: "1px solid " + (on ? "var(--accent)" : "var(--border-strong)"), background: disabled ? "var(--surface-2)" : (on ? (hover ? "var(--accent-hover)" : "var(--accent)") : (hover ? "var(--surface-2)" : "var(--surface)")), transition: "background-color var(--dur-fast) var(--ease-inout), border-color var(--dur-fast) var(--ease-inout), color var(--dur-fast) var(--ease-inout), box-shadow var(--dur-fast) var(--ease-out), transform var(--dur-press) var(--ease-out)" }}>
        <span style={{ position: "absolute", top: "2px", left: checked ? "16px" : "2px", width: "14px", height: "14px", borderRadius: "var(--radius-pill)", background: disabled ? "var(--text-faint)" : (on ? "var(--on-accent)" : "var(--border-strong)"), transition: "left var(--dur-base) var(--ease-step)" }}></span>
      </span>
      {label ? <span style={{ fontFamily: "var(--font-sans)", fontSize: "13px", color: disabled ? "var(--text-faint)" : "var(--text-muted)", whiteSpace: "nowrap" }}>{label}</span> : null}
    </button>
  );
}
