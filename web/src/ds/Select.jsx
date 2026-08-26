import React from "react";
const ringSelect = (e) => { try { return e.target.matches(":focus-visible"); } catch (_) { return true; } };
export function Select({ value, onChange, options = [], placeholder, disabled = false, mono = false, ariaLabel, style }) {
  const [focus, setFocus] = React.useState(false);
  const [hover, setHover] = React.useState(false);
  const opts = options.map((o) => (typeof o === "string" ? { value: o, label: o } : o));
  return (
    <span style={{ position: "relative", display: "inline-flex", alignItems: "center" }}>
      <select value={value} disabled={disabled} aria-label={ariaLabel}
        onChange={onChange ? (e) => onChange(e.target.value) : undefined}
        onFocus={(e) => setFocus(ringSelect(e))} onBlur={() => setFocus(false)}
        onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)}
        style={{ appearance: "none", WebkitAppearance: "none", fontFamily: mono ? "var(--font-mono)" : "var(--font-sans)", fontSize: "14px", height: "var(--control-h)", padding: "0 30px 0 12px", borderRadius: "var(--radius)", border: "1px solid var(--border-strong)", background: (hover && !disabled) ? "var(--surface-2)" : (disabled ? "var(--surface-2)" : "var(--surface)"), color: disabled ? "var(--text-faint)" : "var(--text)", outline: "none", boxShadow: focus ? "var(--focus-ring)" : "none", cursor: disabled ? "default" : "pointer", boxSizing: "border-box", transition: "background-color var(--dur-fast) var(--ease-inout), border-color var(--dur-fast) var(--ease-inout), color var(--dur-fast) var(--ease-inout), box-shadow var(--dur-fast) var(--ease-out), transform var(--dur-press) var(--ease-out)", ...style }}>
        {placeholder ? <option value="">{placeholder}</option> : null}
        {opts.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
      <span aria-hidden="true" style={{ position: "absolute", right: "11px", fontSize: "10px", lineHeight: 1, color: disabled ? "var(--text-faint)" : "var(--text-muted)", pointerEvents: "none" }}>▾</span>
    </span>
  );
}
