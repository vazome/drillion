import React from "react";
/* GraceNotice — the corner notice that explains why the clock still reads 00:00. Up from the
   moment a fresh attempt opens, and gone on its own when the reading grace runs out.
   Same shell as StuckNudge: this is a nudge too, just an early and quieter one.
   The eyebrow is not "Read first": every task README already owns that heading. */
export function GraceNotice({ seconds = 60, onDismiss, style }) {
  return (
    <div className="m-rise" role="status" style={{
      width: 360, background: "var(--surface)", borderRadius: "var(--radius)",
      boxShadow: "var(--shadow-pop)", borderLeft: "3px solid var(--accent)",
      padding: "14px 16px 16px", ...style,
    }}>
      <div style={{ display: "flex", alignItems: "flex-start", gap: "8px", marginBottom: "8px" }}>
        <span style={{ flex: 1, fontSize: "11px", fontWeight: 600, letterSpacing: ".08em", textTransform: "uppercase", color: "var(--text-muted)", lineHeight: 1.35 }}>Reading time</span>
        <button type="button" onClick={onDismiss} aria-label="Dismiss" className="m-press"
          style={{ background: "transparent", border: "none", cursor: "pointer", width: "26px", height: "26px", margin: "-5px -6px -5px 0", display: "flex", alignItems: "center", justifyContent: "center", borderRadius: "var(--radius-sm)", fontSize: "16px", lineHeight: 1, color: "var(--text-faint)" }}>×</button>
      </div>
      <p style={{ margin: 0, fontSize: "14px", lineHeight: 1.5, color: "var(--text)", textWrap: "pretty" }}>
        The clock starts in <span className="tabular" style={{ fontFamily: "var(--font-mono)", fontVariantNumeric: "tabular-nums" }}>{seconds}</span> {seconds === 1 ? "second" : "seconds"}. Read the whole spec before you write anything — it costs you nothing.
      </p>
    </div>
  );
}
