import React from "react";
const LOOKS = {
  new: { color: "var(--text-muted)", background: "var(--surface-2)" },
  due: { color: "var(--accent)", background: "var(--accent-tint)" },
  scheduled: { color: "var(--text-muted)", background: "transparent", border: "1px solid var(--border)" },
  open: { color: "var(--warn)", background: "var(--warn-bg)" },
  done: { color: "var(--pass)", background: "var(--pass-bg)" },
  easy: { color: "var(--pass)", background: "var(--pass-bg)" },
  pass: { color: "var(--pass)", background: "var(--pass-bg)" },
  struggled: { color: "var(--warn)", background: "var(--warn-bg)" },
  failed: { color: "var(--fail)", background: "var(--fail-bg)" },
  abandoned: { color: "var(--text-muted)", background: "var(--surface-2)" },
};
export function StatusBadge({ status = "new", children, style }) {
  const look = LOOKS[status] || LOOKS.new;
  return <span style={{ fontSize: "11px", fontWeight: 600, letterSpacing: ".06em", textTransform: "uppercase", padding: "3px 8px", borderRadius: "var(--radius-sm)", whiteSpace: "nowrap", ...look, ...style }}>{children || status}</span>;
}
