import React from "react";
const ringCollapsible = (e) => { try { return e.target.matches(":focus-visible"); } catch (_) { return true; } };
export function Collapsible({ label, meta, open, defaultOpen = false, onToggle, disabled = false, mono = true, children, style }) {
  const [inner, setInner] = React.useState(defaultOpen);
  const [hover, setHover] = React.useState(false);
  const [focus, setFocus] = React.useState(false);
  const isOpen = open === undefined ? inner : open;
  const toggle = () => { if (disabled) return; if (open === undefined) setInner(!isOpen); if (onToggle) onToggle(!isOpen); };
  return (
    <div style={{ ...style }}>
      <button type="button" aria-expanded={isOpen} disabled={disabled} onClick={toggle}
        onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)}
        onFocus={(e) => setFocus(ringCollapsible(e))} onBlur={() => setFocus(false)}
        style={{ display: "flex", alignItems: "center", gap: "8px", width: "100%", padding: "6px 8px", textAlign: "left", background: (hover && !disabled) ? "var(--surface-2)" : "transparent", border: "none", borderRadius: "var(--radius-sm)", fontFamily: "var(--font-sans)", fontSize: "13px", fontWeight: 600, color: disabled ? "var(--text-faint)" : "var(--text)", cursor: disabled ? "default" : "pointer", boxShadow: focus ? "var(--focus-ring)" : "none", transition: "background .12s" }}>
        <span aria-hidden="true" style={{ display: "inline-block", width: "9px", fontSize: "11px", lineHeight: 1, color: disabled ? "var(--text-faint)" : "var(--text-muted)", transform: isOpen ? "rotate(90deg)" : "none", transition: "transform .15s ease-out" }}>▸</span>
        <span style={{ flex: 1 }}>{label}</span>
        {meta ? <span style={{ fontFamily: "var(--font-mono)", fontSize: "12.5px", fontWeight: 400, color: "var(--text-faint)", fontVariantNumeric: "tabular-nums" }}>{meta}</span> : null}
      </button>
      {isOpen ? (
        <div style={{ marginTop: "6px", background: "var(--surface-2)", borderRadius: "var(--radius-sm)", padding: "10px 12px", maxHeight: "260px", overflow: "auto", fontFamily: mono ? "var(--font-mono)" : "var(--font-sans)", fontSize: mono ? "var(--fs-code)" : "14px", lineHeight: mono ? "var(--lh-code)" : "var(--lh-body)", color: "var(--text)", whiteSpace: mono ? "pre" : "normal" }}>{children}</div>
      ) : null}
    </div>
  );
}
