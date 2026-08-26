import React from "react";
export function ResultBanner({ state = "idle", headline, output, gradeLine, backIn, style }) {
  const base = { borderRadius: "var(--radius)", padding: "12px 16px", fontSize: "14px", ...style };
  if (state === "idle") return <div style={{ ...base, background: "var(--surface-2)", color: "var(--text-faint)" }}>Not run yet — <kbd>Ctrl+Enter</kbd> runs the tests.</div>;
  if (state === "running") return <div style={{ ...base, background: "var(--surface-2)", color: "var(--text-muted)" }} aria-live="polite">Running…</div>;
  if (state === "failed") return (
    <div style={{ ...base, background: "var(--fail-bg)", borderLeft: "3px solid var(--fail)", color: "var(--text)" }} aria-live="polite">
      <div style={{ fontFamily: "var(--font-mono)", fontSize: "13.5px", whiteSpace: "pre-wrap", color: "var(--fail)", fontWeight: 600 }}>✗ {headline}</div>
      {output ? (
        <details style={{ marginTop: 8 }}>
          <summary style={{ cursor: "pointer", fontSize: "13px", color: "var(--text-muted)" }}>Show full output</summary>
          <pre style={{ margin: "8px 0 0", fontFamily: "var(--font-mono)", fontSize: "12.5px", lineHeight: 1.55, whiteSpace: "pre-wrap", color: "var(--text-muted)" }}>{output}</pre>
        </details>
      ) : null}
    </div>
  );
  return (
    <div style={{ ...base, background: "var(--pass-bg)", borderLeft: "3px solid var(--pass)", color: "var(--text)" }} aria-live="polite">
      <span style={{ fontWeight: 600, color: "var(--pass)", letterSpacing: ".04em" }}>✓ PASSED{gradeLine ? " · " + gradeLine : ""}</span>
      {backIn ? <span style={{ marginLeft: 10, fontSize: "13px", color: "var(--text-muted)" }}>back in {backIn}</span> : null}
    </div>
  );
}
