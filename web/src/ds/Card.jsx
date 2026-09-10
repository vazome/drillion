import React from "react";
import s from "./Card.module.css";
export function Card({ label, children, padding = 20, className, style }) {
  return (
    <section className={[s.root, className].filter(Boolean).join(" ")} style={{ padding, ...style }}>
      {label ? <div className={s.label}>{label}</div> : null}
      {children}
    </section>
  );
}
