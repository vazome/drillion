import React from "react";
export function Input({ value, onChange, placeholder, mono = false, style }) {
  const [focus, setFocus] = React.useState(false);
  return (
    <input value={value} placeholder={placeholder} onChange={onChange ? (e) => onChange(e.target.value) : undefined} onFocus={() => setFocus(true)} onBlur={() => setFocus(false)}
      style={{ fontFamily: mono ? "var(--font-mono)" : "var(--font-sans)", fontSize: "14px", height: "var(--control-h)", padding: "0 12px", borderRadius: "var(--radius)", border: "1px solid var(--border-strong)", background: "var(--surface)", color: "var(--text)", outline: "none", boxShadow: focus ? "var(--focus-ring)" : "none", boxSizing: "border-box", ...style }} />
  );
}
