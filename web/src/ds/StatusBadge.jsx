import React from "react";
const LOOKS = {
  // statuses — where the task sits in your workflow; api.py _status() emits these four
  new: { color: "var(--text-muted)", background: "var(--surface-2)" },
  due: { color: "var(--accent)", background: "var(--accent-tint)" },
  open: { color: "var(--warn)", background: "var(--warn-bg)" },
  done: { color: "var(--pass)", background: "var(--pass-bg)" },

  // difficulty — the task's own rating, independent of how you did on it
  easy: { color: "var(--pass)", background: "var(--pass-bg)" },
  medium: { color: "var(--warn)", background: "var(--warn-bg)" },
  hard: { color: "var(--fail)", background: "var(--fail-bg)" },

  // grades — how the attempt went; scheduler.grade_of() plus the abandoned case
  quick: { color: "var(--pass)", background: "var(--pass-bg)" },
  pass: { color: "var(--pass)", background: "var(--pass-bg)" },
  struggled: { color: "var(--warn)", background: "var(--warn-bg)" },
  abandoned: { color: "var(--text-muted)", background: "var(--surface-2)" },
};
export function StatusBadge({ status = "new", children, style }) {
  const look = LOOKS[status] || LOOKS.new;
  return <span style={{ fontSize: "11px", fontWeight: 600, letterSpacing: ".06em", textTransform: "uppercase", padding: "3px 8px", borderRadius: "var(--radius-sm)", whiteSpace: "nowrap", ...look, ...style }}>{children || status}</span>;
}
