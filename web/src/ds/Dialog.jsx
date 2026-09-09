import React from "react";
import { Button } from "./Button.jsx";

/** A modal panel over the current screen. It is a native <dialog> opened with showModal(),
 *  which is where the focus trap, the Escape key, the inert background and the backdrop all
 *  come from — none of them are ours to get wrong. Clicking the backdrop closes it too.
 *  The header is fixed and the body scrolls, so a caller that sets a height keeps it however
 *  much its content changes.
 *
 *  Every way out closes the element itself and lets its own close event report back, so the
 *  panel on screen and the state behind it can never disagree about whether it is open. */
export function Dialog({ open = false, onClose, label, children, style }) {
  const ref = React.useRef(null);
  React.useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (open && !el.open) el.showModal();
    else if (!open && el.open) el.close();
  }, [open]);

  return (
    <dialog ref={ref} aria-label={label} onClose={() => onClose?.()}
      onClick={(e) => { if (e.target === ref.current) ref.current.close(); }}
      style={{ width: "min(760px, calc(100vw - 32px))", maxHeight: "calc(100vh - 64px)", padding: 0, border: "none", borderRadius: "var(--radius)", background: "var(--bg)", color: "var(--text)", boxShadow: "var(--shadow-card)", boxSizing: "border-box", ...style }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, padding: "14px 20px", borderBottom: "1px solid var(--border)", flex: "none" }}>
        <h2 style={{ margin: 0, fontSize: "var(--fs-h)", fontWeight: 600 }}>{label}</h2>
        <div style={{ flex: 1 }} />
        <Button variant="quiet" onClick={() => ref.current?.close()}>Close</Button>
      </div>
      <div style={{ flex: 1, minHeight: 0, overflow: "auto", padding: 20 }}>{children}</div>
    </dialog>
  );
}
