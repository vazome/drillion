import React from "react";
export function Card({ label, children, padding = 20, style }) {
  return (
    <section style={{ background: "var(--surface)", boxShadow: "var(--shadow-card)", borderRadius: "var(--radius)", padding, ...style }}>
      {label ? <div style={{ fontSize: "var(--fs-label)", fontWeight: 600, letterSpacing: "var(--ls-label)", textTransform: "uppercase", color: "var(--text-muted)", marginBottom: 12 }}>{label}</div> : null}
      {children}
    </section>
  );
}
