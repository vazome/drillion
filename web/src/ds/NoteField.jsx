import React from "react";
export function NoteField({ value = "", onChange, label = "Note", hint = "yours, kept with the task", dirty = false, placeholder, rows = 3, ariaLabel, style }) {
  const [focus, setFocus] = React.useState(false);
  return (
    <div style={{ display: "grid", gap: "10px", ...style }}>
      <div style={{ fontSize: "var(--fs-label)", fontWeight: 600, letterSpacing: "var(--ls-label)", textTransform: "uppercase", color: "var(--text-muted)" }}>
        {label}
        <span style={{ fontWeight: 400, textTransform: "none", letterSpacing: 0, fontSize: "12.5px", color: dirty ? "var(--text-muted)" : "var(--text-faint)" }}> · {dirty ? "unsaved" : hint}</span>
      </div>
      <textarea value={value} rows={rows} placeholder={placeholder} aria-label={ariaLabel || label}
        onChange={onChange ? (e) => onChange(e.target.value) : undefined}
        onFocus={() => setFocus(true)} onBlur={() => setFocus(false)}
        style={{ width: "100%", boxSizing: "border-box", display: "block", resize: "vertical", fontFamily: "var(--font-sans)", fontSize: "14px", lineHeight: "1.55", padding: "8px 12px", borderRadius: "var(--radius)", border: "1px solid var(--border-strong)", background: "var(--surface-2)", color: "var(--text)", outline: "none", boxShadow: focus ? "var(--focus-ring)" : "none", transition: "border-color var(--dur-press) var(--ease-out)" }}></textarea>
    </div>
  );
}
