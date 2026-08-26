import React from "react";
const ringConflict = (e) => { try { return e.target.matches(":focus-visible"); } catch { return true; } };
function Action({ label, onClick, strong, disabled }) {
  const [hover, setHover] = React.useState(false);
  const [focus, setFocus] = React.useState(false);
  return (
    <button type="button" disabled={disabled} onClick={onClick}
      onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)}
      onFocus={(e) => setFocus(ringConflict(e))} onBlur={() => setFocus(false)}
      style={{ fontFamily: "var(--font-sans)", fontSize: "13px", fontWeight: 600, whiteSpace: "nowrap", cursor: disabled ? "default" : "pointer", borderRadius: "var(--radius-sm)", boxShadow: focus ? "var(--focus-ring)" : "none", transition: "background-color var(--dur-fast) var(--ease-inout), border-color var(--dur-fast) var(--ease-inout), color var(--dur-fast) var(--ease-inout), box-shadow var(--dur-fast) var(--ease-out), transform var(--dur-press) var(--ease-out)", ...(strong
        ? { padding: "5px 10px", border: "1px solid " + (disabled ? "var(--border)" : "var(--border-strong)"), background: disabled ? "transparent" : (hover ? "var(--surface)" : "transparent"), color: disabled ? "var(--text-faint)" : "var(--text)" }
        : { padding: "5px 4px", border: "none", background: "transparent", color: disabled ? "var(--text-faint)" : "var(--accent)", textDecoration: (hover && !disabled) ? "underline" : "none" }) }}>{label}</button>
  );
}
export function ConflictBanner({ message = "This task changed on disk.", detail, reloadLabel = "Reload from disk", keepLabel = "Keep mine", onReload, onKeep, disabled = false, style }) {
  return (
    <div role="alert" style={{ background: "var(--warn-bg)", borderRadius: "var(--radius)", padding: "10px 12px 10px 14px", display: "flex", alignItems: "center", gap: "14px", ...style }}>
      <div style={{ flex: 1, display: "grid", gap: "2px", minWidth: 0 }}>
        <span style={{ fontFamily: "var(--font-sans)", fontSize: "14px", color: "var(--text)" }}>{message}</span>
        {detail ? <span style={{ fontFamily: "var(--font-mono)", fontSize: "12.5px", color: "var(--text-muted)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{detail}</span> : null}
      </div>
      <Action label={reloadLabel} onClick={onReload} disabled={disabled} strong />
      <Action label={keepLabel} onClick={onKeep} disabled={disabled} />
    </div>
  );
}
