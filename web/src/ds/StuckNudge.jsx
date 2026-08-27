import React from "react";
/* StuckNudge — arrives once a task has been open a long while. Advises a hint first,
   burying and reading the material second. Never blocks the editor; dismissible for good. */
const NUDGE_LABEL = { fontSize: "11px", fontWeight: 600, letterSpacing: ".08em", textTransform: "uppercase", color: "var(--text-muted)" };
function NudgeButton({ variant, onClick, disabled, children }) {
  const [hover, setHover] = React.useState(false);
  const base = { fontFamily: "var(--font-sans)", fontWeight: 600, borderRadius: "var(--radius)", border: "1px solid transparent", lineHeight: 1.2, whiteSpace: "nowrap", cursor: disabled ? "default" : "pointer" };
  const look = disabled
    ? { background: "var(--surface-2)", color: "var(--text-faint)", fontSize: "14px", padding: "8px 14px" }
    : variant === "quiet"
      ? { background: "transparent", color: "var(--accent)", fontSize: "13px", padding: "8px 4px", textDecoration: hover ? "underline" : "none" }
      : { background: hover ? "var(--surface-2)" : "var(--surface)", color: "var(--text)", borderColor: "var(--border-strong)", fontSize: "14px", padding: "8px 14px" };
  return <button type="button" className="m-press" disabled={disabled} onClick={onClick} onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)} style={{ ...base, ...look }}>{children}</button>;
}
export function StuckNudge({ minutes = 30, hintsShown = 0, hintsTotal = 3, hintReady = true, onHint, onBury, onDismiss, placement = "corner", style }) {
  const corner = placement === "corner";
  return (
    <div className="m-rise" role="status" style={{
      width: corner ? 360 : "auto", background: "var(--surface)", borderRadius: "var(--radius)",
      boxShadow: corner ? "var(--shadow-pop)" : "var(--shadow-card)",
      borderLeft: "3px solid var(--accent)", padding: "14px 16px 16px", ...style,
    }}>
      <div style={{ display: "flex", alignItems: "flex-start", gap: "8px", marginBottom: "8px" }}>
        <span style={{ ...NUDGE_LABEL, flex: 1, lineHeight: 1.35 }}>{minutes} minutes on this task</span>
        <button type="button" onClick={onDismiss} aria-label="Dismiss" className="m-press" style={{ background: "transparent", border: "none", cursor: "pointer", width: "26px", height: "26px", margin: "-5px -6px -5px 0", display: "flex", alignItems: "center", justifyContent: "center", borderRadius: "var(--radius-sm)", fontSize: "16px", lineHeight: 1, color: "var(--text-faint)" }}>×</button>
      </div>
      <p style={{ margin: "0 0 4px", fontSize: "14px", lineHeight: 1.5, color: "var(--text)", textWrap: "pretty" }}>
        Take a hint. It opens the next step, not the answer, and the pass still counts.
      </p>
      <p style={{ margin: "0 0 12px", fontSize: "13.5px", lineHeight: 1.5, color: "var(--text-muted)", textWrap: "pretty" }}>
        If the problem still doesn't come apart after one, bury the task and go read the material. It comes back tomorrow, and you will be reading with a question in hand.
      </p>
      <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
        <NudgeButton onClick={onHint} disabled={!hintReady}>Show hint {hintsShown + 1}</NudgeButton>
        <NudgeButton variant="quiet" onClick={onBury}>Bury and read up</NudgeButton>
        <div style={{ flex: 1 }} />
        <span style={{ fontSize: "12px", color: "var(--text-faint)", whiteSpace: "nowrap" }}>{hintsShown} of {hintsTotal} shown</span>
      </div>
    </div>
  );
}
