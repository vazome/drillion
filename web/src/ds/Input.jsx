import React from "react";
export function Input({ value, onChange, placeholder, mono = false, ariaLabel, style }) {
  return (
    <input value={value} placeholder={placeholder} aria-label={ariaLabel} onChange={onChange ? (e) => onChange(e.target.value) : undefined}      style={{ fontFamily: mono ? "var(--font-mono)" : "var(--font-sans)", fontSize: "14px", height: "var(--control-h)", padding: "0 12px", borderRadius: "var(--radius)", border: "1px solid var(--border-strong)", background: "var(--surface)", color: "var(--text)", outline: "none", boxSizing: "border-box", transition: "border-color var(--dur-press) var(--ease-out)", ...style }} />
  );
}
