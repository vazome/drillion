import React from "react";
export function Collapsible({ label, meta, open, defaultOpen = false, onToggle, disabled = false, mono = true, children, style }) {
  const [inner, setInner] = React.useState(defaultOpen);
  const [hover, setHover] = React.useState(false);
  const [press, setPress] = React.useState(false);
  const isOpen = open === undefined ? inner : open;
  const toggle = () => { if (disabled) return; if (open === undefined) setInner(!isOpen); if (onToggle) onToggle(!isOpen); };
  return (
    <div style={{ ...style }}>
      <button type="button" aria-expanded={isOpen} disabled={disabled} onClick={toggle}
        onMouseEnter={() => setHover(true)} onMouseLeave={() => { setHover(false); setPress(false); }}
        onPointerDown={() => setPress(true)} onPointerUp={() => setPress(false)}
        style={{ display: "flex", alignItems: "center", gap: "8px", width: "100%", padding: "6px 8px", textAlign: "left", background: (hover && !disabled) ? "var(--surface-2)" : "transparent", border: "none", borderRadius: "var(--radius-sm)", fontFamily: "var(--font-sans)", fontSize: "13px", fontWeight: 600, color: disabled ? "var(--text-faint)" : "var(--text)", cursor: disabled ? "default" : "pointer", transform: (press && !disabled) ? "translateY(1px)" : "none", transition: "transform var(--dur-press) var(--ease-out), background var(--dur-press) var(--ease-out)" }}>
        <span aria-hidden="true" style={{ display: "inline-block", width: "9px", fontSize: "11px", lineHeight: 1, color: disabled ? "var(--text-faint)" : "var(--text-muted)", transform: isOpen ? "rotate(90deg)" : "none", transition: "transform var(--dur-fast) var(--ease-out)" }}>▸</span>
        <span style={{ flex: 1 }}>{label}</span>
        {meta ? <span style={{ fontFamily: "var(--font-mono)", fontSize: "12.5px", fontWeight: 400, color: "var(--text-faint)", fontVariantNumeric: "tabular-nums" }}>{meta}</span> : null}
      </button>
      {isOpen ? (
        <div className="m-expand" style={{ marginTop: "6px", background: "var(--surface-2)", borderRadius: "var(--radius-sm)", padding: "10px 12px", maxHeight: "260px", overflow: "auto", fontFamily: mono ? "var(--font-mono)" : "var(--font-sans)", fontSize: mono ? "var(--fs-code)" : "14px", lineHeight: mono ? "var(--lh-code)" : "var(--lh-body)", color: "var(--text)", whiteSpace: mono ? "pre" : "normal" }}>{children}</div>
      ) : null}
    </div>
  );
}
